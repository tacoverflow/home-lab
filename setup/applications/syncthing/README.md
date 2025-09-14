# Install syncthing

```bash
sudo apt install -y syncthing
# Enable and start the syncthing service, also check the status
sudo systemctl enable syncthing@${USER}.service
sudo systemctl start syncthing@${USER}.service
sudo systemctl status syncthing@${USER}.service
# Set the host ip to 0.0.0.0 in the syncthing config to allow access from externals ips
vi ~/.config/syncthing/config.xml
# <gui enabled="true" tls="false" debugging="false">
#    <address>0.0.0.0:8384</address>
# ...
sudo systemctl restart syncthing@${USER}.service
sudo systemctl status syncthing@${USER}.service
```
