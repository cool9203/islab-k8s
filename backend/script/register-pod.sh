#!/usr/bin/env bash

if [ ! $# == 6 ]; then
  echo "./register-pod.sh <pod-name> <weeks> <days> <hours> <minutes> <seconds>"
  exit
fi

curl --location \
--request POST 'http://203.64.95.118:30001/gpu/SADD' \
--header 'Content-Type: application/json' \
--data "{\"name\":\"$1\", \"token\":\"islabs102a\", \"weeks\":\"$2\", \"days\":\"$3\", \"hours\":\"$4\", \"minutes\":\"$5\", \"minutes\":\"$6\"}"
