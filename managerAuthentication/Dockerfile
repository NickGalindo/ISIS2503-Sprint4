FROM ubuntu:latest

ENV DEBIAN_FRONTEND=noninteractive

RUN apt-get update -y && \
    apt-get upgrade -y && \
    apt-get install -y software-properties-common && \
    add-apt-repository ppa:deadsnakes/ppa && \
    apt-get update -y && \
    apt-get install -y python3.11 python3.11-dev python3.11-distutils build-essential && \
    apt-get update --fix-missing && \
    apt-get clean

RUN apt-get install -y python3.11-venv python3-pip

WORKDIR /code

COPY ./requirements.txt /code/requirements.txt

RUN python3.11 -m pip install --no-cache-dir --upgrade -r /code/requirements.txt

COPY . /code/app

WORKDIR /code/app

CMD ["python3.11", "-m", "uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8003"]

