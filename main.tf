module  "aws_instance" "CSRv" {

  source = "./csrv"
  create = true  
  CSRv-name = "testcsrv"
  CSRv-image-version = "cisco_CSR-.17.3.4a-AX"
  Instance-type = "t2.medium"
  
  Subnet-name = "subnet4"
  SG-name = "launch-wizard-27"
  SSH-key-name = "jonsun-ec2-key"
  KMS-alias-name = "alias/jonsun_csrv_kms_key"
  Root-volume-size = 8
  Root-volume-encrypted = true
  Private-ip = null
}

