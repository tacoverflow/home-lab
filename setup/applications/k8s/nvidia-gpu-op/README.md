helm install gpu-operator nvidia/gpu-operator --namespace gpu-operator
helm install --wait --generate-name     -n gpu-operator --create-namespace     nvidia/gpu-operator     --version=v25.10.1
helm list -n gpu-operator
helm delete -n gpu-operator gpu-operator-1765321635
k get all -n gpu-operator
