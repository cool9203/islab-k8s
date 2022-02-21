#!/usr/bin/env bash

K8S_DATA_DIR=/mnt/k8s-data/app

if [ ! $# == 1 ]; then
  echo "Invalid parameter (must be \"deploy\", \"redeploy\" or \"uninstall\")"
  exit
fi

if [ "$1" = "deploy" ]; then
  kubectl apply -f deploy/local-storage.yaml
  kubectl apply -f deploy/service-account.yaml
  kubectl apply -f deploy/cluster-role-binding.yaml
  kubectl apply -f deploy/master.yaml
  kubectl apply -f deploy/worker.yaml
  kubectl apply -f deploy/master-svc.yaml
  kubectl apply -f gpu-mounter-worker.yaml
  kubectl apply -f gpu-mounter-master.yaml
  cp ./setting.txt ${K8S_DATA_DIR}/setting.txt
  cp -r ./src ${K8S_DATA_DIR}
  cp -r ./pkg ${K8S_DATA_DIR}

elif [ "$1" = "redeploy" ]; then
  kubectl delete -f deploy/service-account.yaml
  kubectl delete -f deploy/cluster-role-binding.yaml
  kubectl delete -f deploy/master.yaml
  kubectl delete -f deploy/worker.yaml
  kubectl delete -f deploy/master-svc.yaml
  kubectl delete -f gpu-mounter-worker.yaml
  kubectl delete -f gpu-mounter-master.yaml

  kubectl apply -f deploy/local-storage.yaml
  kubectl apply -f deploy/service-account.yaml
  kubectl apply -f deploy/cluster-role-binding.yaml
  kubectl apply -f deploy/master.yaml
  kubectl apply -f deploy/worker.yaml
  kubectl apply -f deploy/master-svc.yaml
  kubectl apply -f gpu-mounter-worker.yaml
  kubectl apply -f gpu-mounter-master.yaml
  cp ./setting.txt ${K8S_DATA_DIR}/setting.txt
  cp -r ./src ${K8S_DATA_DIR}
  cp -r ./pkg ${K8S_DATA_DIR}

elif [ "$1" = "uninstall" ]; then
  kubectl delete -f deploy/local-storage.yaml
  kubectl delete -f deploy/service-account.yaml
  kubectl delete -f deploy/cluster-role-binding.yaml
  kubectl delete -f deploy/master.yaml
  kubectl delete -f deploy/worker.yaml
  kubectl delete -f deploy/master-svc.yaml
  kubectl delete -f gpu-mounter-worker.yaml
  kubectl delete -f gpu-mounter-master.yaml

elif [ "$1" = "test" ]; then
  kubectl delete -f deploy/master.yaml
  kubectl delete -f deploy/worker.yaml

  kubectl apply -f deploy/master.yaml
  kubectl apply -f deploy/worker.yaml

else
  echo "Invalid parameter: $1 (must be \"deploy\", \"redeploy\" or \"uninstall\")"
fi
