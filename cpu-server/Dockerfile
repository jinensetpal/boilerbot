FROM python:3.11-slim

ARG FUNCTION_DIR="/var/task/"
ARG DEBIAN_FRONTEND="noninteractive"
ENV PYTHONPATH=${FUNCTION_DIR}

RUN apt update
RUN apt install build-essential -y

RUN pip install --upgrade pip wheel setuptools dvc==3.37.0

RUN mkdir -p ${FUNCTION_DIR}
COPY requirements.txt ${FUNCTION_DIR}
RUN pip install -r ${FUNCTION_DIR}requirements.txt

COPY . ${FUNCTION_DIR}
WORKDIR ${FUNCTION_DIR}src

EXPOSE 8000
ENTRYPOINT [ "../run.sh" ]
