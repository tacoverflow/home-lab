# Instructions

## Server setup 
1. Run this command (as root) in the server (Debian base) to install bore

```bash
curl -s https://raw.githubusercontent.com/tacoverflow/home-lab/refs/heads/main/setup/tunnels/server-bore-installation.sh | bash
```

2. Create a secret to only allow connections from your clients

```bash
echo "put_your_secret_here" > /tmp/bore.pass
chmod 600 /etc/bore.pass
chown root:root /etc/bore.pass
```

3. Create the systemd service definition and start the new service

```bash
echo "put_your_secret_here" > /tmp/bore.pass
chmod 600 /etc/bore.pass
chown root:root /etc/bore.pass
```


## Client setup
Run this command in the client (RPi) to install bore

```bash
curl -s https://raw.githubusercontent.com/tacoverflow/home-lab/refs/heads/main/setup/tunnels/client-rpi-bore-installation.sh | bash
```

