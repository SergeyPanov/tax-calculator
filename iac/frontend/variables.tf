# OCI Authentication
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

# Compartment
variable "compartment_ocid" {
  type        = string
  description = "OCID of the compartment to create resources in"
}

# Compute
variable "availability_domain_number" {
  type        = number
  description = "Availability domain index (1, 2, or 3). A1.Flex capacity can vary by AD — try others if provisioning fails."
  default     = 1
}

variable "instance_shape" {
  type        = string
  description = "OCI compute shape. VM.Standard.A1.Flex is ARM-based always-free (4 OCPU / 24 GB total free allowance)."
  default     = "VM.Standard.A1.Flex"
}

variable "instance_ocpus" {
  type        = number
  description = "Number of OCPUs for flexible shapes"
  default     = 1
}

variable "instance_memory_in_gbs" {
  type        = number
  description = "Memory in GB for flexible shapes"
  default     = 6
}

# Set this variable to pin the instance image and prevent unintended replacement
# on future plans. Leave empty to auto-resolve the latest Oracle Linux 8 ARM image.
# After first apply, run: terraform output instance_image_id
# and set this variable to that value.
variable "instance_image_id" {
  type        = string
  description = "OCID of the compute image. Leave empty to use the latest Oracle Linux 8 image compatible with the chosen shape."
  default     = ""
}

# Networking
variable "vcn_cidr" {
  type        = string
  description = "CIDR block for the VCN"
  default     = "10.0.0.0/16"
}

variable "subnet_cidr" {
  type        = string
  description = "CIDR block for the public subnet"
  default     = "10.0.1.0/24"
}

# Access
variable "ssh_authorized_keys" {
  type        = string
  description = "Public SSH key(s) to authorize on the instance (contents of ~/.ssh/id_rsa.pub or similar)"
}
