output "instance_public_ip" {
  description = "Public IP address of the frontend instance. Use this to configure DNS A records."
  value       = oci_core_instance.frontend.public_ip
}

output "instance_id" {
  description = "OCID of the compute instance"
  value       = oci_core_instance.frontend.id
}

output "instance_image_id" {
  description = "OCID of the image used. Pin this value in instance_image_id variable to prevent unexpected instance replacement on future plans."
  value       = local.resolved_image_id
}

output "availability_domain" {
  description = "Availability domain the instance was provisioned in"
  value       = local.availability_domain
}

output "vcn_id" {
  description = "OCID of the VCN"
  value       = oci_core_vcn.frontend.id
}

output "ssh_command" {
  description = "Example SSH command to connect to the instance"
  value       = "ssh ubuntu@${oci_core_instance.frontend.public_ip}"
}
