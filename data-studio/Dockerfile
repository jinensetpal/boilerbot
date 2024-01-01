FROM python:3.11-slim

ARG FUNCTION_DIR="/var/task/"
ARG DEBIAN_FRONTEND="noninteractive"
ENV PYTHONPATH=${FUNCTION_DIR}

RUN apt update
RUN apt install build-essential -y

RUN pip install --upgrade pip wheel setuptools

RUN mkdir -p ${FUNCTION_DIR}
COPY . ${FUNCTION_DIR}

RUN pip install -r ${FUNCTION_DIR}requirements.txt

WORKDIR ${FUNCTION_DIR}

EXPOSE 8000
CMD [ "gunicorn", "-w", "4", "main:app", "--bind", "0.0.0.0:8000"]
