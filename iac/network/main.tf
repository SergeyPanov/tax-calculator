terraform {
  required_providers {
    oci = {
      source  = "oracle/oci"
      version = "~> 6.0"
    }
  }
  required_version = ">= 1.3.0"
}

resource "oci_identity_compartment" "tax_calculator" {
  compartment_id = var.tenancy_ocid
  name           = "tax-calculator"
  description    = "Compartment for tax-calculator resources"
}

module "vcn" {
  source           = "../modules/tf-vcn"
  region           = var.region
  compartment_ocid = oci_identity_compartment.tax_calculator.id
  vcn_name         = "tax-calculator-vcn"
}
