ARG CUDA_VERSION
ARG UBUNTU_VERSION
ARG PASSWORD

FROM nvidia/cuda:${CUDA_VERSION}-base-ubuntu${UBUNTU_VERSION}
MAINTAINER yoga

RUN apt-get update
RUN apt-get install -y openssh-server
RUN apt-get install -y python3.6 python3-pip python3-dev

RUN echo "root:${PASSWORD}" | chpasswd

RUN mkdir /var/run/sshd

RUN echo "PasswordAuthentication yes" >> /etc/ssh/sshd_config
RUN echo "PermitRootLogin yes" >> /etc/ssh/sshd_config
RUN sed -i 's@session\s*required\s*pam_loginuid.so@session optional pam_loginuid.so@g' /etc/pam.d/sshd
ENV NOTVISIBLE="in users profile"
RUN echo "export VISIBLE=now" >> /etc/profile
EXPOSE 22

COPY ./test-requirement.txt test-requirement.txt
RUN pip3 install -r test-requirement.txt

CMD ["/usr/sbin/sshd", "-D"]
