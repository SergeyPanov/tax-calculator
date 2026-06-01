resource "oci_core_security_list" "private-security-list" {
  compartment_id = var.compartment_ocid
  vcn_id         = module.vcn.vcn_id

  display_name = "${var.vcn_name}-private-security-list"

  egress_security_rules {
    stateless        = false
    destination      = "0.0.0.0/0"
    destination_type = "CIDR_BLOCK"
    protocol         = "all"
  }

  ingress_security_rules {
    stateless   = false
    source      = "10.0.0.0/16"
    source_type = "CIDR_BLOCK"
    protocol    = "6"
    tcp_options {
      min = 22
      max = 22
    }
  }
}
