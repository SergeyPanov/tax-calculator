variable "region" {
  type        = string
  description = "OCI region (e.g. eu-frankfurt-1, us-ashburn-1)"
}

# Compartment
variable "compartment_ocid" {
  type        = string
  description = "OCID of the compartment to create resources in"
}
