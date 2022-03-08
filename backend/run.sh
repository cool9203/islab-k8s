#!/usr/bin/env bash

DOCKERHUB_USER=yogawulala
IMAGE_NAME=k8s-api-server
DOCKERFILE_PATH=./docker 

if [ ! $# == 1 ]; then 
    echo "./run.sh [build | push | unit_test]"
    exit
fi 

if [ "$1" = "build" ]; then
    docker build . -f ${DOCKERFILE_PATH}/master/Dockerfile -t ${DOCKERHUB_USER}/${IMAGE_NAME}-master
    docker build . -f ${DOCKERFILE_PATH}/worker/Dockerfile -t ${DOCKERHUB_USER}/${IMAGE_NAME}-worker
    ./deploy.sh redeploy

elif [ "$1" = "push" ]; then
    docker push ${DOCKERHUB_USER}/${IMAGE_NAME}-master
    docker push ${DOCKERHUB_USER}/${IMAGE_NAME}-worker

fi


