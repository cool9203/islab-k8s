#!/usr/bin/env bash

WORKDIR=/mnt/k8s-data

if [ ! $# == 1 ]; then
  echo "Invalid parameter (must be \"deploy\", \"redeploy\" or \"uninstall\")"
  exit
fi

if [ "$1" = "deploy" ]; then
  mkdir ${WORKDIR} -m 777
  cd $(pwd)/backend
  ./deploy.sh deploy ${WORKDIR}
  cd ..
  cd $(pwd)/db
  ./deploy.sh deploy ${WORKDIR}
  cd ..
  cd $(pwd)/web
  ./deploy.sh deploy ${WORKDIR}
  cd ..
  cd $(pwd)/sshd
  ./deploy.sh deploy

elif [ "$1" = "redeploy" ]; then
  #rm -r ${WORKDIR}
  mkdir ${WORKDIR} -m 777
  cd $(pwd)/backend
  ./deploy.sh redeploy ${WORKDIR}
  cd ..
  cd $(pwd)/db
  ./deploy.sh redeploy ${WORKDIR}
  cd ..
  cd $(pwd)/web
  ./deploy.sh redeploy ${WORKDIR}
  cd ..
  cd $(pwd)/sshd
  ./deploy.sh redeploy

elif [ "$1" = "uninstall" ]; then
  #rm -r ${WORKDIR}
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

else
  echo "Invalid parameter: $1 (must be \"deploy\", \"redeploy\" or \"uninstall\")"
fi
