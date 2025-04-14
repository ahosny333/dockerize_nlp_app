locals {
  vpc_name           = "terraform-vpc"
  internet_gw_name   = "terraform-internet-gateway"
  route_table_name   = "terraform-route-table"
  public_subnet_name = "terraform-public-subnet"
  server_name        = "ec2-${local.vpc_name}-${local.public_subnet_name}"
}
data "aws_region" "current" {}
data "aws_availability_zones" "available" {}

resource "aws_vpc" "vpc" {
  cidr_block = "10.0.0.0/16"
  tags = {
    Name = local.vpc_name
  }
}



resource "aws_internet_gateway" "gw" {
  vpc_id = aws_vpc.vpc.id

  tags = {
    Name = local.internet_gw_name
  }
}

resource "aws_route_table" "table" {
  vpc_id = aws_vpc.vpc.id

  route {
    cidr_block = "0.0.0.0/0"
    gateway_id = aws_internet_gateway.gw.id
  }

  tags = {
    Name   = local.route_table_name
    testid = aws_subnet.pub_subnet.id
  }
}

resource "aws_subnet" "pub_subnet" {
  vpc_id                  = aws_vpc.vpc.id
  cidr_block              = "10.0.1.0/24"
  map_public_ip_on_launch = true
  availability_zone       = data.aws_availability_zones.available.names[5]

  tags = {
    Name = "${local.public_subnet_name}"
  }
}

resource "aws_route_table_association" "public_assoc" {
  subnet_id      = aws_subnet.pub_subnet.id
  route_table_id = aws_route_table.table.id
}

output "vpc_id" {
  value = aws_vpc.vpc.id
}
output "az" {
  value = data.aws_availability_zones.available.names
}
