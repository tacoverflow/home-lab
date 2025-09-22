# Webcam streaming using cam2ip

Setup steps:

1. Make sure htpasswd is installed

```bash
sudo apt install apache2-utils
```
  
2. Create a htpasswd file, this file contains the hashed passwords used for auth

```bash
sudo htpasswd -c /etc/systemd/system/cam2ip.pass YOUR_USER
# a prompt will ask for a password and after that the file will be create with the hased password
```

3. Create the systemd service

```bash
sudo curl -o /etc/systemd/system/cam2ip.service https://raw.githubusercontent.com/tacoverflow/home-lab/refs/heads/main/setup/cam2ip/systemd/cam2ip.service
sudo systemctl enable cam2ip.service
sudo systemctl start cam2ip.service
```
