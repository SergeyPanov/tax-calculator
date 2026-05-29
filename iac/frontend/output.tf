
output "vcn_id" {
  description = "OCID of the VCN"
  value       = module.vcn.vcn_id
}

output "ig_route_table_id" {
  description = "Route table ID for public subnets (includes internet gateway)"
  value       = module.vcn.id-for-route-table-that-includes-the-internet-gateway
}

output "nat_gateway_id" {
  description = "NAT gateway ID"
  value       = module.vcn.nat-gateway-id
}

output "nat_route_table_id" {
  description = "Route table ID for private subnets (includes NAT gateway)"
  value       = module.vcn.id-for-for-route-table-that-includes-the-nat-gateway
}

# Outputs for public subnet
output "public-subnet-name" {
  # oci_core_subnet.vcn-public-subnet.display_name
  value = module.vcn.public-subnet-name
}
output "public-subnet-OCID" {
  value = module.vcn.public-subnet-OCID
}

# Outputs for private security list

output "private-security-list-name" {
  value = module.vcn.private-security-list-name
}
output "private-security-list-OCID" {
  value = module.vcn.private-security-list-OCID
}


output "ubuntu-images" {
  value = module.compute.instance-shape
}
