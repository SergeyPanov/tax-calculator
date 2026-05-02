terraform {
  required_providers {
    oci = {
      source  = "oracle/oci"
      version = "~> 6.0"
    }
  }
  required_version = ">= 1.3.0"
}

provider "oci" {
  tenancy_ocid     = var.tenancy_ocid
  user_ocid        = var.user_ocid
  fingerprint      = var.fingerprint
  private_key_path = var.private_key_path
  region           = var.region
}

# ---------------------------------------------------------------------------
# Data sources
# ---------------------------------------------------------------------------

data "oci_identity_availability_domains" "ads" {
  compartment_id = var.tenancy_ocid
}

locals {
  availability_domain = data.oci_identity_availability_domains.ads.availability_domains[
    var.availability_domain_number - 1
  ].name
}

# Resolve the latest Oracle Linux 8 image compatible with the chosen shape.
# This data source is only used when instance_image_id variable is not set.
# After first apply, pin the image to prevent unexpected instance replacement:
#   terraform output instance_image_id  → set instance_image_id variable to that value.
data "oci_core_images" "oracle_linux_8" {
  compartment_id           = var.compartment_ocid
  operating_system         = "Oracle Linux"
  operating_system_version = "8"
  shape                    = var.instance_shape
  sort_by                  = "TIMECREATED"
  sort_order               = "DESC"
  state                    = "AVAILABLE"
}

locals {
  resolved_image_id = var.instance_image_id != "" ? var.instance_image_id : data.oci_core_images.oracle_linux_8.images[0].id
}

# ---------------------------------------------------------------------------
# Networking
# ---------------------------------------------------------------------------

resource "oci_core_vcn" "frontend" {
  compartment_id = var.compartment_ocid
  cidr_block     = var.vcn_cidr
  display_name   = "frontend-vcn"
  dns_label      = "frontendvcn"
}

resource "oci_core_internet_gateway" "frontend" {
  compartment_id = var.compartment_ocid
  vcn_id         = oci_core_vcn.frontend.id
  display_name   = "frontend-igw"
  enabled        = true
}

resource "oci_core_route_table" "public" {
  compartment_id = var.compartment_ocid
  vcn_id         = oci_core_vcn.frontend.id
  display_name   = "frontend-public-rt"

  route_rules {
    destination       = "0.0.0.0/0"
    destination_type  = "CIDR_BLOCK"
    network_entity_id = oci_core_internet_gateway.frontend.id
  }
}

# ---------------------------------------------------------------------------
# Network Security Group — targeted port rules for the instance
# Preferred over subnet-wide security lists for precise exposure control.
# ---------------------------------------------------------------------------

resource "oci_core_network_security_group" "frontend" {
  compartment_id = var.compartment_ocid
  vcn_id         = oci_core_vcn.frontend.id
  display_name   = "frontend-nsg"
}

resource "oci_core_network_security_group_security_rule" "ingress_ssh" {
  network_security_group_id = oci_core_network_security_group.frontend.id
  direction                 = "INGRESS"
  protocol                  = "6" # TCP
  source                    = "0.0.0.0/0"
  source_type               = "CIDR_BLOCK"
  stateless                 = false

  tcp_options {
    destination_port_range {
      min = 22
      max = 22
    }
  }
}

resource "oci_core_network_security_group_security_rule" "ingress_http" {
  network_security_group_id = oci_core_network_security_group.frontend.id
  direction                 = "INGRESS"
  protocol                  = "6" # TCP
  source                    = "0.0.0.0/0"
  source_type               = "CIDR_BLOCK"
  stateless                 = false

  tcp_options {
    destination_port_range {
      min = 80
      max = 80
    }
  }
}

resource "oci_core_network_security_group_security_rule" "ingress_https" {
  network_security_group_id = oci_core_network_security_group.frontend.id
  direction                 = "INGRESS"
  protocol                  = "6" # TCP
  source                    = "0.0.0.0/0"
  source_type               = "CIDR_BLOCK"
  stateless                 = false

  tcp_options {
    destination_port_range {
      min = 443
      max = 443
    }
  }
}

resource "oci_core_network_security_group_security_rule" "egress_all" {
  network_security_group_id = oci_core_network_security_group.frontend.id
  direction                 = "EGRESS"
  protocol                  = "all"
  destination               = "0.0.0.0/0"
  destination_type          = "CIDR_BLOCK"
  stateless                 = false
}

# ---------------------------------------------------------------------------
# Subnet — public, uses the route table above
# Default security list is kept minimal (no ingress rules); NSG handles them.
# ---------------------------------------------------------------------------

resource "oci_core_subnet" "public" {
  compartment_id             = var.compartment_ocid
  vcn_id                     = oci_core_vcn.frontend.id
  cidr_block                 = var.subnet_cidr
  display_name               = "frontend-public-subnet"
  dns_label                  = "frontendpub"
  route_table_id             = oci_core_route_table.public.id
  prohibit_public_ip_on_vnic = false
}

# ---------------------------------------------------------------------------
# Cloud-init — installs nginx and opens the OS-level firewall
# ---------------------------------------------------------------------------

locals {
  cloud_init_script = <<-EOT
    #!/bin/bash
    set -euo pipefail

    # Install and start nginx
    dnf install -y nginx
    systemctl enable --now nginx

    # Open ports 80 and 443 in firewalld (OCI Oracle Linux has it enabled by default)
    firewall-cmd --permanent --add-service=http
    firewall-cmd --permanent --add-service=https
    firewall-cmd --reload
  EOT
}

# ---------------------------------------------------------------------------
# Compute instance — VM.Standard.A1.Flex (ARM, always-free tier)
# ---------------------------------------------------------------------------

resource "oci_core_instance" "frontend" {
  compartment_id      = var.compartment_ocid
  availability_domain = local.availability_domain
  display_name        = "frontend-instance"
  shape               = var.instance_shape

  shape_config {
    ocpus         = var.instance_ocpus
    memory_in_gbs = var.instance_memory_in_gbs
  }

  source_details {
    source_type = "image"
    source_id   = local.resolved_image_id
  }

  create_vnic_details {
    subnet_id              = oci_core_subnet.public.id
    assign_public_ip       = true
    display_name           = "frontend-vnic"
    nsg_ids                = [oci_core_network_security_group.frontend.id]
    skip_source_dest_check = false
  }

  metadata = {
    ssh_authorized_keys = var.ssh_authorized_keys
    user_data           = base64encode(local.cloud_init_script)
  }

  preserve_boot_volume = false
}
