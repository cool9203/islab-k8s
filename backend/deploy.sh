#!/usr/bin/env bash

if [ ! $# == 1 ]; then
  echo "./deploy.sh [deploy | redeploy | uninstall]"
  exit
fi

WORKDIR=/etc/islab-k8s/backend

# check and create WORKDIR
if [ ! -d ${WORKDIR} ]; then
  mkdir ${WORKDIR}
fi

sudo cp -r ./deploy ./data ${WORKDIR}

if [ "$1" = "deploy" ]; then
  kubectl apply -f deploy/service-account.yaml
  kubectl apply -f deploy/cluster-role-binding.yaml
  kubectl apply -f deploy/master.yaml
  kubectl apply -f deploy/worker.yaml
  kubectl apply -f deploy/master-svc.yaml
  kubectl apply -f deploy/gpu-mounter-master.yaml 
  kubectl apply -f deploy/gpu-mounter-worker.yaml 

elif [ "$1" = "redeploy" ]; then
  kubectl delete -f deploy/service-account.yaml
  kubectl delete -f deploy/cluster-role-binding.yaml
  kubectl delete -f deploy/master.yaml
  kubectl delete -f deploy/worker.yaml
  kubectl delete -f deploy/master-svc.yaml
  kubectl delete -f deploy/gpu-mounter-master.yaml
  kubectl delete -f deploy/gpu-mounter-worker.yaml

  kubectl apply -f deploy/service-account.yaml
  kubectl apply -f deploy/cluster-role-binding.yaml
  kubectl apply -f deploy/master.yaml
  kubectl apply -f deploy/worker.yaml
  kubectl apply -f deploy/master-svc.yaml
  kubectl apply -f deploy/gpu-mounter-master.yaml
  kubectl apply -f deploy/gpu-mounter-worker.yaml

elif [ "$1" = "uninstall" ]; then
  kubectl delete -f deploy/service-account.yaml
  kubectl delete -f deploy/cluster-role-binding.yaml
  kubectl delete -f deploy/master.yaml
  kubectl delete -f deploy/worker.yaml
  kubectl delete -f deploy/master-svc.yaml
  kubectl delete -f deploy/gpu-mounter-master.yaml
  kubectl delete -f deploy/gpu-mounter-worker.yaml

else
  echo "./deploy.sh [deploy | redeploy | uninstall]"
fi
