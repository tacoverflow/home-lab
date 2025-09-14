# Install syncthing

```bash
sudo apt install -y syncthing
# Find the config file path with this
# sudo syncthing -paths
# Configuration file:
#         /root/.config/syncthing/config.xml
sudo vi /root/.config/syncthing/config.xml
# <gui enabled="true" tls="false" debugging="false">
#    <address>PUT_YOUR_IP_OR_DOMAIN_HERE:8384</address>
# ...
sudo systemctl enable syncthing@root.service
sudo systemctl status syncthing@root.service
#
```
