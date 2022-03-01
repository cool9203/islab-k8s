#!/usr/bin/env bash

WORKDIR=/etc/islab-k8s
K8S_DATA_DIR=/mnt/k8s-data

if [ ! $# == 1 ]; then
  echo "Invalid parameter (must be \"client\", \"deploy\", \"redeploy\" or \"uninstall\")"
  exit
fi

# check and create WORKDIR
if [ ! -d ${WORKDIR} ]; then
  sudo mkdir ${WORKDIR}
fi

# check and create WORKDIR
if [ ! -d ${K8S_DATA_DIR} ]; then
  sudo mkdir ${K8S_DATA_DIR} -m 777
fi

sudo cp -r ./client ${WORKDIR}

if [ "$1" = "deploy" ]; then
  cd $(pwd)/backend
  ./deploy.sh deploy
  cd ..
  cd $(pwd)/db
  ./deploy.sh deploy ${K8S_DATA_DIR}
  cd ..
  cd $(pwd)/web
  ./deploy.sh deploy
  cd ..
  cd $(pwd)/sshd
  ./deploy.sh deploy

elif [ "$1" = "redeploy" ]; then
  cd $(pwd)/backend
  ./deploy.sh redeploy
  cd ..
  cd $(pwd)/db
  ./deploy.sh redeploy ${K8S_DATA_DIR}
  cd ..
  cd $(pwd)/web
  ./deploy.sh redeploy
  cd ..
  cd $(pwd)/sshd
  ./deploy.sh redeploy

elif [ "$1" = "uninstall" ]; then
  cd $(pwd)/backend
  ./deploy.sh uninstall
  cd ..
  cd $(pwd)/db
  ./deploy.sh uninstall
  cd ..
  cd $(pwd)/web
  ./deploy.sh uninstall
  cd ..
  cd $(pwd)/sshd
  ./deploy.sh uninstall

elif [ "$1" = "client"  ]; then
  echo "deploy on client success"

else
  echo "Invalid parameter: $1 (must be \"client\", \"deploy\", \"redeploy\" or \"uninstall\")"
fi
