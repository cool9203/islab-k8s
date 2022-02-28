FROM python:3.8 as build-env
WORKDIR app
COPY ./requirements.txt ./
RUN pip install -r requirements.txt

COPY ./src/master/main.py ./main.py
COPY ./pkg ./pkg

RUN pyinstaller -F ./main.py

FROM ubuntu:20.04
WORKDIR app
COPY --from=build-env /app/dist/main ./main

RUN apt-get update
RUN apt-get install -y curl
RUN curl -fsSLo /usr/share/keyrings/kubernetes-archive-keyring.gpg https://packages.cloud.google.com/apt/doc/apt-key.gpg
RUN echo "deb [signed-by=/usr/share/keyrings/kubernetes-archive-keyring.gpg] https://apt.kubernetes.io/ kubernetes-xenial main" | tee /etc/apt/sources.list.d/kubernetes.list
RUN apt-get update
RUN apt-get install -y kubectl=1.23.1-00
RUN apt-mark hold kubectl

CMD ["/bin/bash"]
