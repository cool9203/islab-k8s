#!/usr/bin/env bash

if [ ! $# == 1 ] ; then
  echo "./deploy [deploy | redeploy | uninstall]"
  exit
fi

WORKDIR=/etc/islab-k8s/httpd

# check and create WORKDIR
if [ ! -d ${WORKDIR} ]; then
  sudo mkdir ${WORKDIR}
fi

sudo cp -r ./html ${WORKDIR}

if [ "$1" = "deploy" ]; then
  kubectl apply -f deploy/pod.yaml
  kubectl apply -f deploy/svc.yaml

elif [ "$1" = "redeploy" ]; then
  kubectl delete -f deploy/pod.yaml
  kubectl delete -f deploy/svc.yaml

  kubectl apply -f deploy/pod.yaml
  kubectl apply -f deploy/svc.yaml

elif [ "$1" = "uninstall" ]; then
  kubectl delete -f deploy/pod.yaml
  kubectl delete -f deploy/svc.yaml

else
  echo "./deploy [deploy | redeploy | uninstall]"
fi
