module "vcn" {
  source  = "oracle-terraform-modules/vcn/oci"
  version = "3.6.0"

  # Required Inputs
  compartment_id = var.compartment_ocid

  # Optional Inputs
  region = var.region

  vcn_name                = var.vcn_name
  create_internet_gateway = true
  create_nat_gateway      = false
  create_service_gateway  = false
}
