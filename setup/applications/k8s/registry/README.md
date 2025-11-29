# Create an HTTP Secret 

```
cat > .env.secrets << EOF
REGISTRY_HTTP_SECRET=$(openssl rand --base64 32)
EOF
```

# Create ssl certificate
```
openssl \
	req -x509 -newkey rsa:4096 \
	-keyout certs/registry.key \
	-out certs/registry.crt \
	-days 365 -nodes \
	-subj "/CN=k8smaster" \
	-config <(cat <<EOF
[req]
distinguished_name=req
x509_extensions = v3_req
[req_distinguished_name]
[v3_req]
subjectAltName=DNS:k8smaster,DNS:localhost,DNS:image-registry.swag-code.com,IP:127.0.0.1
EOF
)
```

# Update containerd to add new registry

```
# vim /etc/containerd/config.toml
    [plugins."io.containerd.grpc.v1.cri".registry]
      ...
      [plugins."io.containerd.grpc.v1.cri".registry.mirrors]
        [plugins."io.containerd.grpc.v1.cri".registry.mirrors."localhost:5000"]
          endpoint = ["http://localhost:30001"]
```

# Add the certificate to the chain
```
sudo cp certs/registry.crt /usr/local/share/ca-certificates/image-registry.crt
sudo update-ca-certificates
```
