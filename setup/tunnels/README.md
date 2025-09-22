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
echo "put_your_secret_here" | sudo tee /etc/systemd/system/bore.pass
sudo chmod 600 /etc/systemd/system/bore.pass
sudo chown root:root /etc/systemd/system/bore.pass
```

3. Create the systemd service definition and start the new services, add the ports to the list as needed

```bash
sudo curl -o /etc/systemd/system/bore-client@.service https://raw.githubusercontent.com/tacoverflow/home-lab/refs/heads/main/setup/tunnels/systemd/bore-client%40.service
EXPOSE_PORTS="test-webpage 8081 8888
cam2ip 56000 56000
syncthing-tunnel 8384 8384"
echo "$EXPOSE_PORTS" | while read tunnel_name local_port remote_port
do
    echo "BORE_LOCAL_PORT=$local_port" | sudo tee /etc/systemd/system/bore-${tunnel_name}.conf
    echo "BORE_REMOTE_PORT=$remote_port" | sudo tee -a /etc/systemd/system/bore-${tunnel_name}.conf
    sudo systemctl enable bore-client@${tunnel_name}.service
    sudo systemctl start bore-client@${tunnel_name}.service
done
```

