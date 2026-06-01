variable "tenancy_ocid" {
  type        = string
  description = "OCID of your OCI tenancy"
}

variable "user_ocid" {
  type        = string
  description = "OCID of the OCI user for Terraform"
}

variable "fingerprint" {
  type        = string
  description = "Fingerprint of the API key pair used for authentication"
}

variable "private_key_path" {
  type        = string
  description = "Path to the PEM private key file for OCI API authentication"
}

variable "region" {
  type        = string
  description = "OCI region (e.g. eu-frankfurt-1, us-ashburn-1)"
}

variable "compartment_ocid" {
  type        = string
  description = "OCID of the compartment to create resources in"
}
