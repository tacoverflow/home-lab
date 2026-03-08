1. Use WSL2 to create a new ubuntu disto with custom name
```
wsl -d Ubuntu --name k8s-worker
```

2. Install the [nvidia cuda toolkit](https://developer.nvidia.com/cuda-downloads?target_os=Linux&target_arch=x86_64&Distribution=Ubuntu&target_version=24.04&target_type=deb_network) inside WSL
```
wget https://developer.download.nvidia.com/compute/cuda/repos/ubuntu2404/x86_64/cuda-keyring_1.1-1_all.deb
sudo dpkg -i cuda-keyring_1.1-1_all.deb
sudo apt-get update
sudo apt-get -y install cuda-toolkit-13-1
```
3. Test nvidia cuda toolkit
```
nvidia-smi
```

4.Install the [nvidia container toolkit](https://docs.nvidia.com/datacenter/cloud-native/container-toolkit/latest/install-guide.html) inside WSL
```
sudo apt-get update && sudo apt-get install -y --no-install-recommends \
   ca-certificates \
   curl \
   gnupg2

curl -fsSL https://nvidia.github.io/libnvidia-container/gpgkey | sudo gpg --dearmor -o /usr/share/keyrings/nvidia-container-toolkit-keyring.gpg \
  && curl -s -L https://nvidia.github.io/libnvidia-container/stable/deb/nvidia-container-toolkit.list | \
    sed 's#deb https://#deb [signed-by=/usr/share/keyrings/nvidia-container-toolkit-keyring.gpg] https://#g' | \
    sudo tee /etc/apt/sources.list.d/nvidia-container-toolkit.list

sudo sed -i -e '/experimental/ s/^#//g' /etc/apt/sources.list.d/nvidia-container-toolkit.list

sudo apt-get update

export NVIDIA_CONTAINER_TOOLKIT_VERSION=1.18.2-1
  sudo apt-get install -y \
      nvidia-container-toolkit=${NVIDIA_CONTAINER_TOOLKIT_VERSION} \
      nvidia-container-toolkit-base=${NVIDIA_CONTAINER_TOOLKIT_VERSION} \
      libnvidia-container-tools=${NVIDIA_CONTAINER_TOOLKIT_VERSION} \
      libnvidia-container1=${NVIDIA_CONTAINER_TOOLKIT_VERSION}
```

5. Configure WSL and install containerd, kubelet, kubeadm and join the cluster
```
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
# IMPORTANT!!! This is the line that allow us to use the GPU
sudo nvidia-ctk runtime configure --runtime=containerd
# Start container runntime
sudo systemctl enable containerd
sudo systemctl restart containerd

# Hotfix for wrong/missing cni path
sudo ln -s /opt/cni/bin /usr/lib/cni
sudo systemctl restart containerd.service
echo "KUBELET_EXTRA_ARGS=\"--node-ip=$NEBULA_IP\"" > /etc/default/kubelet
sudo systemctl restart kubelet.service

# Run join command
# sudo kubeadm join 10.0.0.2:6443 --token 99...vi --discovery-token-ca-cert-hash sha256:69e...28a --node-name worker-2-gpu
```
