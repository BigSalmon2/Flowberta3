FROM pytorch/pytorch:1.7.0-cuda11.0-cudnn8-devel

RUN apt-get update && \
    apt-get install -y && \
    apt-get install -y apt-utils wget

RUN pip install --upgrade pip
RUN pip install transformers \
    tensorboard \
    wandb

RUN pip install flask && pip install waitress

WORKDIR /gpt2_story/
EXPOSE 80
COPY . .
ENTRYPOINT ["python", "server.py"]