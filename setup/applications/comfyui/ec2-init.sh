# mount persistent efs
sudo yum install -y amazon-efs-utils
sudo mkdir efs
sudo mount -t efs $EFS_ID efs/

# install bore
curl -s https://raw.githubusercontent.com/tacoverflow/home-lab/refs/heads/main/setup/tunnels/client-i686-bore-installation.sh | bash

# create bore secret
echo "$BORE_PASS" | sudo tee /etc/systemd/system/bore.pass
sudo chmod 600 /etc/systemd/system/bore.pass
sudo chown root:root /etc/systemd/system/bore.pass

# create a bore service to connect to server
sudo curl -o /etc/systemd/system/bore-client@.service https://raw.githubusercontent.com/tacoverflow/home-lab/refs/heads/main/setup/tunnels/systemd/bore-client%40.service
EXPOSE_PORTS="comfyui 8188 8188"
echo "$EXPOSE_PORTS" | while read tunnel_name local_port remote_port
do
    echo "BORE_LOCAL_PORT=$local_port" | sudo tee /etc/systemd/system/bore-${tunnel_name}.conf
    echo "BORE_REMOTE_PORT=$remote_port" | sudo tee -a /etc/systemd/system/bore-${tunnel_name}.conf
    sudo systemctl enable bore-client@${tunnel_name}.service
    sudo systemctl start bore-client@${tunnel_name}.service
done
