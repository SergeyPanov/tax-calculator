terraform {
  required_providers {
    oci = {
      source  = "oracle/oci"
      version = "~> 6.0"
    }
  }
  required_version = ">= 1.3.0"
}

module "vcn" {
  source           = "./tf-vcn"
  region           = var.region
  compartment_ocid = var.compartment_ocid
}

module "compute" {
  source           = "./tf-compute"
  compartment_ocid = var.compartment_ocid
  subnet_id        = module.vcn.public-subnet-OCID
  ssh_pub_key      = var.ssh_pub_key
}
