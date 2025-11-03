# Terraform for IaC

## Installation

1. Install go if needed (note: this is for a RPI/ARM arch, use your machine arch instead)

```bash
wget -P /tmp/ https://dl.google.com/go/go1.25.3.linux-arm64.tar.gz
sudo tar -C /usr/local -xzf /tmp/go1.25.3.linux-arm64.tar.gz
vim /etc/profile
# add next line
# export PATH=$PATH:/usr/local/go/bin
go version
# go version go1.25.1 linux/arm
```

2. Install terraform
```bash
curl -o /tmp/terraform_1.13.3_linux_arm.zip https://releases.hashicorp.com/terraform/1.13.3/terraform_1.13.3_linux_arm.zip
unzip -d /tmp/terraform_1.13.3_linux_arm /tmp/terraform_1.13.3_linux_arm.zip 
sudo mv /tmp/terraform_1.13.3_linux_arm/terraform /usr/local/bin/terraform
terraform version
# Terraform v1.13.3
# on linux_arm
```
