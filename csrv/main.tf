/*
data "aws_eip" "csrv" {
  filter {
    name   = "tag:Name"
    values = [var.CSRv-name]
  }
}
*/

data "aws_kms_key" "this" {
  count = var.create ? 1 : 0
  key_id = "alias/jonsun_csrv_kms_key"
}

data "aws_subnet" "selected" {
  count = var.create ? 1 : 0
  filter {
    name   = "tag:Name"
    values = [var.Subnet-name]
  }
}

data "aws_security_group" "selected" {
  count = var.create ? 1 : 0
  name = var.SG-name
}

data "aws_ami" "CSRv" {
  count = var.create ? 1 : 0

  most_recent      = true
  owners           = ["aws-marketplace"]

  filter {
    name   = "description"
    values = [var.CSRv-image-version]
  }

}

resource "aws_instance" "CSRv" {
  count = var.create ? 1 : 0
  ami           = data.aws_ami.CSRv.image_id
  instance_type = var.Instance-type
  
  subnet_id = data.aws_subnet.selected.id
  vpc_security_group_ids = [data.aws_security_group.selected.id]
  key_name = var.SSH-key-name
  
 
  root_block_device {
    encrypted = true
    kms_key_id = data.aws_kms_key.this.id
    volume_size = var.Root-volume-size
  }
 


  private_ip = var.Private-ip

  tags = {
    name = var.CSRv-name
  }
  
}

/*  cannot be allowed in the innovaiton lab
resource "aws_eip_association" "eip_assoc" {
  count = var.create ? 1 : 0
  instance_id   = aws_instance.CSRv.id
  allocation_id = data.aws_eip.csrv.id
}
*/

