# Compartment
variable "compartment_ocid" {
  type        = string
  description = "OCID of the compartment to create resources in"
}

variable "subnet_id" {
  type        = string
  description = "OCID of the public subnet to place the instance in"
}

variable "ssh_pub_key" {
  type        = string
  description = "Path to the SSH public key file to connect to the compute instance"
}

variable "instance_name" {
  type        = string
  description = "Display name for the compute instance"
  default     = "tax-calculator"
}
