#! /bin/bash -xe
# Place on /opt/iptables-aws-reroute-hack.sh

#sudo iptables -X

AWS_PROFILE=terraform
ip_pairs=$(aws ec2 describe-instances \
        --filters "Name=tag:k8s,Values=true" "Name=instance-state-name,Values=running" \
        --query "Reservations[].Instances[][PrivateIpAddress,PublicIpAddress]" \
        --output text)

echo "$ip_pairs" | while read internal_ip external_ip; do
        sudo iptables -t nat -A OUTPUT -p tcp --dport 10250  -d $internal_ip -j DNAT --to-destination $external_ip
done
