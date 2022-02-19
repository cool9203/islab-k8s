FROM ubuntu:18.04
MAINTAINER yoga

ARG PASSWORD

RUN apt-get update
RUN apt-get install -y openssh-server

RUN mkdir /var/run/sshd
RUN echo 'root:${PASSWORD}' | chpasswd

RUN sed -i 's/#*PermitRootLogin prohibit-password/PermitRootLogin yes/g' /etc/ssh/sshd_config
RUN sed -i 's@session\s*required\s*pam_loginuid.so@session optional pam_loginuid.so@g' /etc/pam.d/sshd
ENV NOTVISIBLE="in users profile"
RUN echo "export VISIBLE=now" >> /etc/profile
CMD ["/usr/sbin/sshd", "-D"]
