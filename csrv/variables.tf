variable "create" {
  description = "Whether to create an instance"
  type        = bool
  default     = true
}

variable "CSRv-name" {
  description = "Name to be used on EC2 instance created"
  type        = string
  default     = "testcsrv"
}


variable "CSRv-image-version" {
  description = "CSRv image version"
  type        = string
  default     = "cisco_CSR-.17.3.4a-AX"
}

variable "SG-name" {
  description = "Security Group Name"
  type        = string
  default     = "launch-wizard-27"
}

variable "Subnet-name" {
  description = "Subnet Name"
  type        = string
  default     = "subnet4"
}

variable "SSH-key-name" {
  description = "key pair name for SSH connection"
  type        = string
  default     = "jonsun-ec2-key"
}

variable "Instance-type" {
  description = "instance type of the EC2"
  type        = string
  default     = "t2.medium"
}


variable "Private-ip" {
  description = "private ip address for the EC2"
  type        = string
  default     = null
}


variable "Root-volume-size" {
  description = "the root block device volume size"
  type        = number
  default     = 8
}

variable "Root-volume-encrypted" {
  description = "the root block device volume be encrypted or not"
  type        = bool
  default     = true
}

variable "KMS-alias-name" {
  description = "the kms key alias name"
  type        = string
  default     = "alias/jonsun_csrv_kms_key"
}