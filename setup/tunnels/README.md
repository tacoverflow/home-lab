# Instructions

## Server setup 
1. Run this command (as root) in the server (Debian base) to install bore

```bash
curl -s https://raw.githubusercontent.com/tacoverflow/home-lab/refs/heads/main/setup/tunnels/server-bore-installation.sh | bash
```

2. Create a secret to only allow connections from your clients

```bash
echo "put_your_secret_here" > /etc/systemd/system/bore.pass
chmod 600 /etc/systemd/system/bore.pass
chown root:root /etc/systemd/system/bore.pass
```

3. Create the systemd service definition and start the new service

```bash
curl -o /etc/systemd/system/bore-server.service https://raw.githubusercontent.com/tacoverflow/home-lab/refs/heads/main/setup/tunnels/systemd/bore-server.service
systemctl enable bore-server.service
systemctl start bore-server.service
```


## Client setup
1. Run this command in the client (RPi) to install bore

```bash
curl -s https://raw.githubusercontent.com/tacoverflow/home-lab/refs/heads/main/setup/tunnels/client-rpi-bore-installation.sh | bash
```

2. Create a secret to only allow connections from your clients

```bash
echo "put_your_secret_here" > /etc/systemd/system/bore.pass
chmod 600 /etc/systemd/system/bore.pass
chown root:root /etc/systemd/system/bore.pass
```

3. Create the systemd service definition and start the new services, add the ports to the list as needed

```bash
curl -o /etc/systemd/system/bore-client@.service https://raw.githubusercontent.com/tacoverflow/home-lab/refs/heads/main/setup/tunnels/systemd/bore-client%40.service
EXPOSE_PORTS="8888"
for port in EXPOSE_PORTS; do
    systemctl enable bore-server@${port}.service
    systemctl start bore-server@${port}.service
done
```

