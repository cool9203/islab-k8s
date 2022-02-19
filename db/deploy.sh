#!/usr/bin/env bash

if [ ! $# == 1 ]; then
  echo "Invalid parameter (must be \"deploy\", \"redeploy\" or \"uninstall\")"
  exit
fi

if [ "$1" = "deploy" ]; then
  kubectl apply -f deploy/pod.yaml

elif [ "$1" = "redeploy" ]; then
  kubectl delete -f deploy/pod.yaml

  kubectl apply -f deploy/pod.yaml

elif [ "$1" = "uninstall" ]; then
  kubectl delete -f deploy/pod.yaml

else
  echo "Invalid parameter: $1 (must be \"deploy\", \"redeploy\" or \"uninstall\")"
fi
