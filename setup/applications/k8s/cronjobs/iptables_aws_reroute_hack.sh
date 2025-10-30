#! /bin/bash -xe
# Place on /opt/iptables_aws_reroute_hack.sh
ip_pairs=$(/usr/local/bin/aws ec2 describe-instances \
        --filters "Name=tag:Name,Values=k8s-worker" "Name=instance-state-name,Values=running" \
        --query "Reservations[].Instances[][PrivateIpAddress,PublicIpAddress]" \
        --output text)

[ -z  "$ip_pairs" ] || echo "$ip_pairs" | while read internal_ip external_ip; do
        iptables -C OUTPUT -t nat -p tcp --dport 10250  -d $internal_ip -j DNAT --to-destination $external_ip 2>/dev/null
        if [ $? -eq 1 ]; then
                iptables -t nat -A OUTPUT -p tcp --dport 10250  -d $internal_ip -j DNAT --to-destination $external_ip
                echo "Adding: iptables -t nat -A OUTPUT -p tcp --dport 10250  -d $internal_ip -j DNAT --to-destination $external_ip"
        else
                echo "Skipping: iptables -t nat -A OUTPUT -p tcp --dport 10250  -d $internal_ip -j DNAT --to-destination $external_ip"
        fi
don
