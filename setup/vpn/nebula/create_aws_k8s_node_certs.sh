#!/bin/bash

base_path=$(pwd)

mkdir -p nodes
cd nodes

for i in {3..254}; do
  IP="10.0.0.$i"
  mkdir -p $IP
  cd $IP
  nebula-cert sign -ca-key ${base_path}/ca/ca.key -ca-crt ${base_path}/ca/ca.crt -name "host" -ip "$IP/24" -groups "k8s-worker"
  cd ..
done
