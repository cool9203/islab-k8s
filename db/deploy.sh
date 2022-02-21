#!/usr/bin/env bash

if [[ ($# == 0)  ||  ("$1" != "uninstall" && $# < 2) ]] ; then
  echo "./deploy [deploy | redeploy [K8S_DATA_DIR]] | [uninstall]"
  exit
fi

K8S_DATA_DIR=$2/islab-db

if [ "$1" = "deploy" ]; then
  yq -i ".spec.volumes[0].hostPath.path = \"${K8S_DATA_DIR}\"" deploy/pod.yaml
  kubectl apply -f deploy/pod.yaml

elif [ "$1" = "redeploy" ]; then
  yq -i ".spec.volumes[0].hostPath.path = \"${K8S_DATA_DIR}\"" deploy/pod.yaml
  kubectl delete -f deploy/pod.yaml

  kubectl apply -f deploy/pod.yaml

elif [ "$1" = "uninstall" ]; then
  kubectl delete -f deploy/pod.yaml

else
  echo "./deploy [deploy | redeploy [K8S_DATA_DIR]] | [uninstall]"
fi
