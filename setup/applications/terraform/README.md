# Terraform for IaC

## Installation

1. Install go if needed (note: this is for a RPI/ARM arch, use your machine arch instead)

```bash
curl -o /tmp/go1.25.1.linux-armv6l.tar.gz https://go.dev/dl/go1.25.1.linux-armv6l.tar.gz
sudo tar -C /usr/local -xzf /tmp/go1.25.1.linux-armv6l.tar.gz
vim /etc/profile
# add next line
# export PATH=$PATH:/usr/local/go/bin
go version
# go version go1.25.1 linux/arm
```

2. Install terraform
```bash
go install github.com/hashicorp/terraform/terraform@latest
```
