docker build . -f ./Dockerfile -t yogawulala/islab-client-test --build-arg CUDA_VERSION=11.2.2 --build-arg UBUNTU_VERSION=18.04 --build-arg PASSWORD=i913
docker push yogawulala/islab-client-test
