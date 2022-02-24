#!/usr/bin/env bash

DOCKERHUB_USER=yogawulala
IMAGE_NAME=k8s-api-server
DOCKERFILE_PATH=./docker 

K8S_DATA_DIR=/mnt/k8s-data/islab-backend

if [ ! $# == 1 ]; then 
    echo "./run.sh [build | push | test]"
    exit
fi 

if [ "$1" = "build" ]; then
    docker build . -f ${DOCKERFILE_PATH}/master/Dockerfile -t ${DOCKERHUB_USER}/${IMAGE_NAME}-master
    docker build . -f ${DOCKERFILE_PATH}/worker/Dockerfile -t ${DOCKERHUB_USER}/${IMAGE_NAME}-worker
    docker build . -f ${DOCKERFILE_PATH}/base/Dockerfile -t ${DOCKERHUB_USER}/${IMAGE_NAME}-base
    ./deploy.sh redeploy ${K8S_DATA_DIR}

elif [ "$1" = "push" ]; then
    docker push ${DOCKERHUB_USER}/${IMAGE_NAME}-master
    docker push ${DOCKERHUB_USER}/${IMAGE_NAME}-worker

elif [ "$1" = "test" ]; then
    python3 -m pytest ./pkg/unit_test.py
    sudo rm -r ./pkg/__pycache__

fi


