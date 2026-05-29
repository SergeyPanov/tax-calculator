output "name-of-first-availability-domain" {
  value = data.oci_identity_availability_domains.ads.availability_domains[0].name
}

output "instance-name" {
  value = oci_core_instance.ubuntu_instance.display_name
}

output "instance-OCID" {
  value = oci_core_instance.ubuntu_instance.id
}

output "instance-shape" {
  value = oci_core_instance.ubuntu_instance.shape
}

output "instance-state" {
  value = oci_core_instance.ubuntu_instance.state
}

output "instance-OCPUs" {
  value = oci_core_instance.ubuntu_instance.shape_config[0].ocpus
}

output "instance-memory-in-GBs" {
  value = oci_core_instance.ubuntu_instance.shape_config[0].memory_in_gbs
}
