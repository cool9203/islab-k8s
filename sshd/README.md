# islab-k8s/sshd
## deploy
```shell
./deploy.sh [deploy | redeploy]
```

## uninstall
```
./deploy.sh uninstall
```

## set ssh port with `HOST_IP`
in `./deploy/svc.yaml`  
edit spec.ports.nodePort  
example-1: set 30447, should use `<HOST_IP>:30447` to link container.  
this pod usually to ssh jump.  
example-2: `ssh -J <islab-sshd-user-name>@<HOST_IP>:<PORT> <target-container-user-name>@<target-container-ip> -p <target-container-ssh-port>` `<PORT>` like example-1's `30447`.  
