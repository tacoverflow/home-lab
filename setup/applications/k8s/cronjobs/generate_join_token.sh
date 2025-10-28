#! /bin/bash
# Place on /opt/generate_join_token.sh

join_command=$(kubeadm token create --print-join-command --ttl 48h)
aws ssm put-parameter --name "k8s-join-command" --value "$join_command" --type String --overwrite
