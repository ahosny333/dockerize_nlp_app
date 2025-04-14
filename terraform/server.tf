resource "aws_security_group" "sg" {
  name        = "my_sg_ter"
  description = "Allow TLS inbound traffic and all outbound traffic"
  vpc_id      = aws_vpc.vpc.id

  tags = {
    Name = "ter_sg"
  }
}

resource "aws_vpc_security_group_ingress_rule" "sg_rule1" {
  security_group_id = aws_security_group.sg.id
  cidr_ipv4         = "0.0.0.0/0"
  from_port         = 80
  ip_protocol       = "tcp"
  to_port           = 80
}

resource "aws_vpc_security_group_ingress_rule" "sg_rule2" {
  security_group_id = aws_security_group.sg.id
  cidr_ipv4         = "0.0.0.0/0"
  from_port         = 22
  ip_protocol       = "tcp"
  to_port           = 22
}

resource "aws_vpc_security_group_ingress_rule" "sg_rule3" {
  security_group_id = aws_security_group.sg.id
  cidr_ipv4         = "0.0.0.0/0"
  from_port         = 5000
  ip_protocol       = "tcp"
  to_port           = 5000
}

resource "aws_vpc_security_group_egress_rule" "sg_rule4" {
  security_group_id = aws_security_group.sg.id

  cidr_ipv4   = "0.0.0.0/0"
  from_port   = 0
  to_port     = 65535
  ip_protocol = "tcp"

}

resource "aws_instance" "ec2_instance" {
  ami                         = var.ami_id
  instance_type               = var.instance_type
  key_name                    = var.ssh_key_name
  associate_public_ip_address = true
  subnet_id                   = aws_subnet.pub_subnet.id
  vpc_security_group_ids      = [aws_security_group.sg.id]
  root_block_device {
    volume_size = 8
    volume_type = "gp2"
  }


  user_data = file("userdata.sh")


  provisioner "remote-exec" {
    inline = [
      "while [ ! -f /tmp/userdata-complete ]; do sleep 2; done"
    ]
    connection {
      type        = "ssh"
      user        = "ubuntu"
      private_key = file("hj2.pem")
      host        = self.public_ip
    }
  }

  tags = {
    Name = local.server_name
  }
}

