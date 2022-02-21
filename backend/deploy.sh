#!/usr/bin/env bash

if [[ ($# == 0)  ||  ("$1" != "uninstall" && $# < 2) ]] ; then
  echo "./deploy [deploy | redeploy [K8S_DATA_DIR]] | [uninstall]"
  exit
fi

#K8S_DATA_DIR=/etc/api-server-base
K8S_DATA_DIR=$2

if [ "$1" = "deploy" ]; then
  yq -i ".spec.template.spec.volumes[0].hostPath.path = \"${K8S_DATA_DIR}/log\"" deploy/master.yaml
  yq -i ".spec.template.spec.volumes[1].hostPath.path = \"${K8S_DATA_DIR}/src/master/main.py\"" deploy/master.yaml
  yq -i ".spec.template.spec.volumes[2].hostPath.path = \"${K8S_DATA_DIR}/pkg\"" deploy/master.yaml
  yq -i ".spec.template.spec.volumes[3].hostPath.path = \"${K8S_DATA_DIR}/deploy\"" deploy/master.yaml

  yq -i ".spec.template.spec.volumes[0].hostPath.path = \"${K8S_DATA_DIR}/log\"" deploy/worker.yaml
  yq -i ".spec.template.spec.volumes[1].hostPath.path = \"${K8S_DATA_DIR}/src/worker/main.py\"" deploy/worker.yaml
  yq -i ".spec.template.spec.volumes[2].hostPath.path = \"${K8S_DATA_DIR}/pkg\"" deploy/worker.yaml

  kubectl apply -f deploy/service-account.yaml
  kubectl apply -f deploy/cluster-role-binding.yaml
  kubectl apply -f deploy/master.yaml
  kubectl apply -f deploy/worker.yaml
  kubectl apply -f deploy/master-svc.yaml
  sudo cp -r ./ ${K8S_DATA_DIR}

elif [ "$1" = "redeploy" ]; then
  yq -i ".spec.template.spec.volumes[0].hostPath.path = \"${K8S_DATA_DIR}/log\"" deploy/master.yaml
  yq -i ".spec.template.spec.volumes[1].hostPath.path = \"${K8S_DATA_DIR}/src/master/main.py\"" deploy/master.yaml
  yq -i ".spec.template.spec.volumes[2].hostPath.path = \"${K8S_DATA_DIR}/pkg\"" deploy/master.yaml
  yq -i ".spec.template.spec.volumes[3].hostPath.path = \"${K8S_DATA_DIR}/deploy\"" deploy/master.yaml

  yq -i ".spec.template.spec.volumes[0].hostPath.path = \"${K8S_DATA_DIR}/log\"" deploy/worker.yaml
  yq -i ".spec.template.spec.volumes[1].hostPath.path = \"${K8S_DATA_DIR}/src/worker/main.py\"" deploy/worker.yaml
  yq -i ".spec.template.spec.volumes[2].hostPath.path = \"${K8S_DATA_DIR}/pkg\"" deploy/worker.yaml

  kubectl delete -f deploy/service-account.yaml
  kubectl delete -f deploy/cluster-role-binding.yaml
  kubectl delete -f deploy/master.yaml
  kubectl delete -f deploy/worker.yaml
  kubectl delete -f deploy/master-svc.yaml

  kubectl apply -f deploy/service-account.yaml
  kubectl apply -f deploy/cluster-role-binding.yaml
  kubectl apply -f deploy/master.yaml
  kubectl apply -f deploy/worker.yaml
  kubectl apply -f deploy/master-svc.yaml
  sudo cp -r ./ ${K8S_DATA_DIR}

elif [ "$1" = "uninstall" ]; then
  kubectl delete -f deploy/service-account.yaml
  kubectl delete -f deploy/cluster-role-binding.yaml
  kubectl delete -f deploy/master.yaml
  kubectl delete -f deploy/worker.yaml
  kubectl delete -f deploy/master-svc.yaml

else
  echo "./deploy [deploy | redeploy [K8S_DATA_DIR]] | [uninstall]"
fi
