FROM python:3.8 as build-env
WORKDIR app
COPY ./requirements.txt ./
RUN pip install -r requirements.txt

COPY ./src/worker/main.py ./main.py
COPY ./pkg ./pkg

RUN pyinstaller -F ./main.py

FROM ubuntu:20.04
WORKDIR app
COPY --from=build-env /app/dist/main ./main

CMD ["/bin/bash"]
