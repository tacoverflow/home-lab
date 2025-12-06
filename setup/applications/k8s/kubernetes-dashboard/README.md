# Install nginx ingress controller with helm
```
helm install nginx-ingress oci://ghcr.io/nginx/charts/nginx-ingress --version 2.3.1 --create-namespace --namespace nginx-ingress
# delete with: helm delete nginx-ingress --namespace nginx-ingress
```

# Install dashboard with helm

```
helm repo add kubernetes-dashboard https://kubernetes.github.io/dashboard/
helm upgrade --install kubernetes-dashboard kubernetes-dashboard/kubernetes-dashboard --create-namespace --namespace kubernetes-dashboard
kubectl edit svc -n kubernetes-dashboard kubernetes-dashboard-kong-proxy
# Change type: ClusterIp to NodePort 
```

# Apply the ingress


# Create ssl certificate
```
openssl \
        req -x509 -newkey rsa:4096 \
        -keyout certs/kubernetes-dashboard.key \
        -out certs/kubernetes-dashboard.crt \
        -days 365 -nodes \
        -subj "/CN=k8smaster" \
        -config <(cat <<EOF
[req]
distinguished_name=req
x509_extensions = v3_req
[req_distinguished_name]
[v3_req]
subjectAltName=DNS:localhost,DNS:lab.swag-code.com,IP:127.0.0.1
EOF
)
```

# Add the certificate to the chain
```
sudo cp certs/kubernetes-dashboard.crt /usr/local/share/ca-certificates/kubernetes-dashboard.crt
sudo update-ca-certificates
```

# Create a access token
```
kubectl create token dashboard-user -n kubernetes-dashboard
```
