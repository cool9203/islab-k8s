# ./islab-k8s/backend


# debug
## log path
```
#master log path:
/etc/islab-k8s/log/master.log

#worker log path:
/etc/islab-k8s/log/worker.log

#gpu-mounter log path
/etc/islab-k8s/log/GPUMounter-master.log
/etc/islab-k8s/log/GPUMounter-worker.log
```

## change log path
- https://github.com/cool9203/islab-k8s/blob/master/deploy/worker.yaml#L46
- https://github.com/cool9203/islab-k8s/blob/master/deploy/worker.yaml#L46

# how to add service to master or worker

## step 1

add `<name>.py` in [this](https://github.com/cool9203/islab-k8s/tree/master/pkg/api), using [this template](https://github.com/cool9203/islab-k8s/blob/master/pkg/api/test.py).

## step 2
add `<name>.py` to [master](https://github.com/cool9203/islab-k8s/blob/master/pkg/api/master.py#L5) or [worker](https://github.com/cool9203/islab-k8s/blob/master/pkg/api/worker.py#L5)

## step 3
deploy.  
```sh
sudo ./run.sh run
or
sudo ./deploy.sh redeploy
```

## step 4
test.  

# master call worker service example
https://github.com/cool9203/islab-k8s/blob/master/pkg/api/test-worker.py#L20-L25  
if change port, `8080` need edit to changed port.  
