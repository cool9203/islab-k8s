#!/usr/bin/env bash

DOCKERHUB_USER=yogawulala
IMAGE_NAME=islab-sshd
DOCKERFILE_PATH=./docker/Dockerfile
PASSWORD=i913

if [ ! $# == 1 ]; then
  echo "Invalid parameter (must be \"build\")"
  exit
fi

if [ "$1" = "build" ]; then
  docker build . -f ${DOCKERFILE_PATH} -t ${DOCKERHUB_USER}/${IMAGE_NAME} --build-arg PASSWORD=${PASSWORD}

else
  echo "Invalid parameter (must be \"build\")"
fi
