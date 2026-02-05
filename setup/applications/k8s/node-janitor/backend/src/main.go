package main

import (
    "context"
    "fmt"
    "log"
    "net/http"
    "os"

    metav1 "k8s.io/apimachinery/pkg/apis/meta/v1"
    "k8s.io/client-go/kubernetes"
    "k8s.io/client-go/rest"
)

func main() {
    http.HandleFunc("/self-destruct", func(w http.ResponseWriter, r *http.Request) {
        nodeName := os.Getenv("NODE_NAME")
        
        // 1. Create the in-cluster config
        config, _ := rest.InClusterConfig()
        clientset, _ := kubernetes.NewForConfig(config)

        // 2. Delete this node
        err := clientset.CoreV1().Nodes().Delete(context.TODO(), nodeName, metav1.DeleteOptions{})
        if err != nil {
            http.Error(w, err.Error(), 500)
            return
        }
        fmt.Fprintf(w, "Node %s marked for deletion", nodeName)
    })
    log.Fatal(http.ListenAndServe(":8080", nil))
}

