FROM nvidia/cuda:10.2-cudnn8-devel
ENV PATH /usr/local/bin:$PATH
ENV LANG C.UTF-8
RUN apt-get update && \
    apt-get install -y && \
    apt-get install -y apt-utils wget

RUN apt-get install -y python3.6
RUN ln -s /usr/bin/python3.6 /usr/bin/python

RUN apt-get install -y python3-pip
RUN pip3 install --upgrade pip
RUN pip install torch torchvision
RUN pip install transformers
RUN pip install flask && pip install waitress

WORKDIR /gpt2_story/
COPY . .
ENTRYPOINT ["python", "server.py"]