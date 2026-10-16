variable "aws_region" {
  type    = string
  default = "ap-south-1"
}
variable "cluster_name" {
  type    = string
  default = "relaydesk-eks"
}
variable "environment" {
  type    = string
  default = "capstone"
}
variable "kubernetes_version" {
  type    = string
  default = "1.35"
}
variable "admin_cidrs" {
  description = "Public IP CIDRs permitted to reach the EKS API, for example your current public IP /32."
  type        = list(string)
  validation {
    condition     = length(var.admin_cidrs) > 0 && alltrue([for cidr in var.admin_cidrs : can(cidrhost(cidr, 0)) && cidr != "0.0.0.0/0"])
    error_message = "Supply valid restricted CIDRs; 0.0.0.0/0 is not permitted."
  }
}
variable "node_instance_type" {
  type    = string
  default = "t3.large"
}
