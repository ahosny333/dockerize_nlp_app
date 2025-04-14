#!/bin/bash
cd /home/ubuntu
mkdir start_dir
mkdir start_dir2
echo "apt-get update" 
sudo apt-get update -y 
sudo apt-get install -y build-essential python3-pip >> test.txt

echo "====end update======" >> test.txt

sudo pip install --break-system-packages https://s3.amazonaws.com/cloudformation-examples/aws-cfn-bootstrap-py3-latest.tar.gz >> test.txt

echo "Installing Docker prerequisites" >> test.txt
sudo apt-get install -y apt-transport-https ca-certificates curl gnupg-agent software-properties-common >> test.txt

echo "Adding Docker’s official GPG key" >> test.txt
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo apt-key add - >> test.txt

echo "Setting up the Docker repository" >> test.txt
sudo add-apt-repository "deb [arch=amd64] https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable" >> test.txt

echo "Updating apt-get for Docker packages" >> test.txt
sudo apt-get update -y >> test.txt

echo "Installing Docker" >> test.txt
sudo apt-get install -y docker-ce docker-ce-cli containerd.io >> test.txt

echo "Starting and enabling Docker service" >> test.txt
sudo systemctl start docker
sudo systemctl enable docker
echo "====Docker installation completed====" >> test.txt

touch /tmp/userdata-complete
echo "====end timeout finish======" >> test.txt
