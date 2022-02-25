# islab-k8s

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

## used submoudle
1. [GPUMounter](https://github.com/pokerfaceSad/GPUMounter), now use this [version](https://github.com/cool9203/GPUMounter/commit/5ca4e5cf16d7dbd3fdfc2b4d12f9b828ab897648). use in [./backend/deploy/gpu-mounter-master.yaml](https://github.com/cool9203/islab-k8s/blob/master/backend/deploy/gpu-mounter-master.yaml) and [./backend/deploy/gpu-mounter-worker.yaml](https://github.com/cool9203/islab-k8s/blob/master/backend/deploy/gpu-mounter-worker.yaml)  
