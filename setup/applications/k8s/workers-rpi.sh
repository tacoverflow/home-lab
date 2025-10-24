# disable the swap, required by kubelet
sudo swapoff -a
sudo systemctl stop systemd-zram-setup@zram0.service
sudo systemctl mask systemd-zram-setup@zram0.service
sudo swapoff /dev/zram0

# Enable ipv4 forwarding
# loading kernel modules
sudo modprobe bridge
sudo modprobe br_netfilter
# also load modules on boot
cat <<EOF | sudo tee /etc/modules-load.d/k8s.conf
bridge
br_netfilter
EOF
# Set config to 1, requirement by kubeadm
cat <<EOF | sudo tee /etc/sysctl.d/k8s.conf
net.bridge.bridge-nf-call-iptables = 1
net.bridge.bridge-nf-call-ip6tables = 1
net.ipv4.ip_forward = 1
EOF
# Apply the change
sudo sysctl --system

# Disable appmonitor
# This service monitor and block any call to an app that does not have a rule
sudo systemctl stop apparmor
sudo systemctl disable apparmor

# Install packages
# Update repo list
sudo apt update
# install basic tools
sudo apt install -y apt-transport-https ca-certificates curl gpg
# Create directory `/etc/apt/keyrings` if does not exist
sudo mkdir -p -m 755 /etc/apt/keyrings
# Add kubernetes keyring to gpg and add the repo to the source list
curl -fsSL https://pkgs.k8s.io/core:/stable:/v1.34/deb/Release.key | sudo gpg --dearmor -o /etc/apt/keyrings/kubernetes-apt-keyring.gpg
echo 'deb [signed-by=/etc/apt/keyrings/kubernetes-apt-keyring.gpg] https://pkgs.k8s.io/core:/stable:/v1.34/deb/ /' | sudo tee /etc/apt/sources.list.d/kubernetes.list
# Update repo list again
sudo apt update
# Install packages
sudo apt install -y kubelet kubeadm kubectl containerd
# Set containerd cgroup config as systemd
sudo mkdir -p /etc/containerd
containerd config default | sudo tee /etc/containerd/config.toml
# update this config
sudo sed -i "s/SystemdCgroup = false/SystemdCgroup = true/g"  /etc/containerd/config.toml
# Start container runntime
sudo systemctl enable containerd
sudo systemctl restart containerd

# Hotfix for wrong/missing cni path
sudo ln -s /opt/cni/bin /usr/lib/cni
sudo systemctl restart containerd.service
sudo systemctl restart kubelet.service
