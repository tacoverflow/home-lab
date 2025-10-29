# Get the scripts
```bash
sudo curl -o /opt/generate_join_token.sh https://raw.githubusercontent.com/tacoverflow/home-lab/refs/heads/main/setup/applications/k8s/cronjobs/generate_join_token.sh
sudo crontab -e
# 0 0 * * * /bin/bash -x /opt/generate_join_token.sh >> /tmp/cron.out 2>&1
```
