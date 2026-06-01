output "compartment_id" {
  description = "OCID of the tax-calculator compartment"
  value       = oci_identity_compartment.tax_calculator.id
}

output "vcn_id" {
  description = "OCID of the VCN"
  value       = module.vcn.vcn_id
}

output "public_subnet_id" {
  description = "OCID of the public subnet"
  value       = module.vcn.public-subnet-OCID
}

output "private_security_list_id" {
  description = "OCID of the private security list"
  value       = module.vcn.private-security-list-OCID
}
