# Get the scripts
```bash
sudo curl -o /opt/generate_join_token.sh https://raw.githubusercontent.com/tacoverflow/home-lab/refs/heads/main/setup/applications/k8s/cronjobs/generate_join_token.sh
sudo curl -o /opt/iptables_aws_reroute_hack.sh https://raw.githubusercontent.com/tacoverflow/home-lab/refs/heads/main/setup/applications/k8s/cronjobs/iptables_aws_reroute_hack.sh
sudo curl -o /opt/iptables_aws_reroute_hack_cleanup.sh https://raw.githubusercontent.com/tacoverflow/home-lab/refs/heads/main/setup/applications/k8s/cronjobs/iptables_aws_reroute_hack_cleanup.sh
sudo crontab -e
# 0 0 * * * /bin/bash -x /opt/generate_join_token.sh > /tmp/cron.out 2>&1
# 1 0 * * * /bin/bash -x /opt/iptables_aws_reroute_hack_cleanup.sh >> /tmp/cron.out 2>&1
# * * * * * /bin/bash -x /opt/iptables_aws_reroute_hack.sh
```
