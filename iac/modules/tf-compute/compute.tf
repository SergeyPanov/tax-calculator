resource "oci_core_instance" "ubuntu_instance" {
  # Required
  availability_domain = data.oci_identity_availability_domains.ads.availability_domains[1].name
  compartment_id      = var.compartment_ocid
  shape               = "VM.Standard.E2.1.Micro"

  source_details {
    source_type             = "image"
    source_id               = data.oci_core_images.ubuntu.images[0].id
    boot_volume_size_in_gbs = 50
  }

  create_vnic_details {
    assign_public_ip = true
    subnet_id        = var.subnet_id
  }

  metadata = {
    ssh_authorized_keys = file(var.ssh_pub_key)
  }

  # Optional
  display_name         = var.instance_name
  preserve_boot_volume = false
}
