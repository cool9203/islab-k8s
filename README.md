# islab-k8s

## Note and Document  
[normal](https://hackmd.io/@yogawulala/rybib53YY)  
[slide](https://hackmd.io/@yogawulala/rybib53YY#/)  

## how to deploy on control plane
```
# path in ~/
mkdir k8s && cd k8s
git clone https://github.com/cool9203/islab-k8s.git
./deploy.sh deploy
```

## how to deploy on client node
```
# path in ~/
mkdir k8s && cd k8s
git clone https://github.com/cool9203/islab-k8s.git
./deploy.sh client
```

## deploy require module
1. yq, if not have, need change `./db/dpeloy/pod.yaml line 28` at want chnage db data save path.  

## used submodule
1. [GPUMounter](https://github.com/pokerfaceSad/GPUMounter), now use this [version](https://github.com/cool9203/GPUMounter/commit/5ca4e5cf16d7dbd3fdfc2b4d12f9b828ab897648). use [./backend/deploy/gpu-mounter-master.yaml](https://github.com/cool9203/islab-k8s/blob/master/backend/deploy/gpu-mounter-master.yaml) [./backend/deploy/gpu-mounter-svc.yaml](https://github.com/cool9203/GPUMounter/blob/master/deploy/gpu-mounter-svc.yaml) and [./backend/deploy/gpu-mounter-worker.yaml](https://github.com/cool9203/islab-k8s/blob/master/backend/deploy/gpu-mounter-worker.yaml)  
