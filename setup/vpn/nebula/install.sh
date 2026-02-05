#! /bin/bash

case $(arch) in
  x86_64)
    URL="https://github.com/slackhq/nebula/releases/download/v1.10.2/nebula-linux-amd64.tar.gz"
    ;;
  aarch64)
    URL="https://github.com/slackhq/nebula/releases/download/v1.10.2/nebula-linux-arm-7.tar.gz"
    ;;
  *)
    URL=""
    ;;
esac

wget -nc $URL
tar -xvf nebula-*.tar.gz
sudo mv ./nebula ./nebula-cert /usr/local/bin/
sudo mkdir -p /etc/nebula
sudo curl -o /etc/systemd/system/nebula.service https://raw.githubusercontent.com/tacoverflow/home-lab/refs/heads/main/setup/vpn/nebula/systemd/nebula.service
