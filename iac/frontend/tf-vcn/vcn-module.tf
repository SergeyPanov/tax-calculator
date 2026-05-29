module "vcn" {
  source  = "oracle-terraform-modules/vcn/oci"
  version = "3.6.0"
  # insert the 1 required variable here

  # Required Inputs
  compartment_id = var.compartment_ocid

  # Optional Inputs
  region = var.region

  # Changing the following default values
  vcn_name                = "tax-calculator-vcn"
  create_internet_gateway = true
  create_nat_gateway      = true
  create_service_gateway  = true
}
