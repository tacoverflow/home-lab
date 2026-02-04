# Install Nebula
```
sudo apt install nebula
```
Or go to the repo and get the bins
[https://github.com/slackhq/nebula](https://github.com/slackhq/nebula)
```
#! /bin/bash
case $(arch) in
    x86_64)
        URL="https://github.com/slackhq/nebula/releases/download/v1.10.2/nebula-linux-amd64.tar.gz"
        ;;
    aarch64)
        URL="https://github.com/slackhq/nebula/releases/download/v1.10.2/nebula-linux-arm-7.tar.gz"
        ;;
    *)
        URL=""
        ;;
esac
wget -nc $URL
tar -xvf nebula-*.tar.gz
sudo mv ./nebula ./nebula-cert /usr/local/bin/
```

# Create the network cetificates
- Create CA the certs
```
mkdir ca
cd ca
nebula-cert ca -name "MyHybridCluster"
ls
# ca.crt ca.key
cd ..
```
- Create the Lighthouse certs (the public relay)
```
nebula-cert sign -name "lighthouse" -ip "10.0.0.1/24"
```

- Create the Home Master certs
```
nebula-cert sign -name "home-master" -ip "10.0.0.2/24" -groups "k8s-control"
```
- Create the AWS Worker
```
nebula-cert sign -name "aws-worker" -ip "10.0.0.X/24" -groups "k8s-worker"
```

## To create the certs for all the aws nodes
```
./create_aws_k8s_node_certs.sh
aws s3 cp --recursive nodes s3://persistent-data-ef4ba2/nebula/nodes
aws s3 cp ca/ca.crt s3://persistent-data-ef4ba2/nebula/ca.crt
```
