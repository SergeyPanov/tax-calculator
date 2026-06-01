variable "region" {
  type        = string
  description = "OCI region (e.g. eu-frankfurt-1, us-ashburn-1)"
}

variable "compartment_ocid" {
  type        = string
  description = "OCID of the compartment to create resources in"
}

variable "vcn_name" {
  type        = string
  description = "Display name for the VCN and related resources"
  default     = "tax-calculator-vcn"
}
