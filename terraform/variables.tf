variable "aws_region" {
  type        = string
  description = "region used to deploy workloads"
  default     = "us-east-1"
}
variable "ami_id" {
  type        = string
  description = "ami id used to deploy workloads"
  default     = "ami-084568db4383264d4"
}
variable "instance_type" {
  type        = string
  description = "instance type used to deploy workloads"
  default     = "t2.micro"
}
variable "ssh_key_name" {
  type        = string
  description = "ssh key name used to deploy workloads"
  default     = "hj2_aws"
}
