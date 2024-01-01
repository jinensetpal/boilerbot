FROM python:3.11-slim

ARG FUNCTION_DIR="/var/task/"
ARG DEBIAN_FRONTEND="noninteractive"
ENV PYTHONPATH=${FUNCTION_DIR}

RUN apt update
RUN apt install build-essential -y

RUN pip install --upgrade pip wheel setuptools dvc

RUN mkdir -p ${FUNCTION_DIR}
COPY requirements.txt ${FUNCTION_DIR}
RUN pip install -r ${FUNCTION_DIR}requirements.txt

COPY . ${FUNCTION_DIR}
RUN dvc pull -r http
WORKDIR ${FUNCTION_DIR}src

ENV TRANSFORMERS_CACHE=/.cache/huggingface/hub
ENV TORCH_HOME=/.cache/torch/


EXPOSE 8000
ENTRYPOINT [ "uvicorn" ]
CMD [ "main:app", "--host", "0.0.0.0", "--port", "8000" ]
