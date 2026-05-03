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
  type    = string
  default = "The SSH public key to connect to the compute instance"
}
