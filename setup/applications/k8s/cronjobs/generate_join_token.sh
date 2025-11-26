#! /bin/bash -xe
# Add this to root contab
# 0 0 * * * /bin/bash -x /opt/generate_join_token.sh >> /tmp/cron.out 2>&1

# Place on /opt/generate_join_token.sh
echo "start"
curl https://swag-code.com:6443 -k -s -m 1 -o /dev/null || systemctl restart bore-client@k8s-control-plane-endpoint.service
sleep 1
join_command=$(kubeadm token create --print-join-command --ttl 48h)
echo "join: $join_command"
output=$(/usr/local/bin/aws ssm put-parameter --name "k8s-join-command" --value "$join_command" --type String --overwrite)
echo "output: $output"
echo "end"
