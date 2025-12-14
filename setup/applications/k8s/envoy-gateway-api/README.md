# Installing it
```
kubectl apply --server-side -f https://github.com/envoyproxy/gateway/releases/latest/download/install.yaml
# OR
kubectl apply --server-side=true -k .
```

# Check status
```
kubectl -n envoy-gateway-system get po,svc,deploy
```
