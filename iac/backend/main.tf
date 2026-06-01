terraform {
  required_providers {
    oci = {
      source  = "oracle/oci"
      version = "~> 6.0"
    }
  }
  required_version = ">= 1.3.0"
}

data "terraform_remote_state" "network" {
  backend = "local"

  config = {
    path = "../network/terraform.tfstate"
  }
}

module "compute" {
  source           = "../modules/tf-compute"
  compartment_ocid = data.terraform_remote_state.network.outputs.compartment_id
  subnet_id        = data.terraform_remote_state.network.outputs.public_subnet_id
  ssh_pub_key      = var.ssh_pub_key
  instance_name    = "tax-calculator-backend"
}
