FROM python:2
#FROM ubuntu:18.04

ENV DEBIAN_FRONTEND noninteractive
ENV uid 1000
ENV gid 1000

RUN apt-get update

# install required PYTHON modules
# ---------------------------
COPY ./requirements.txt ./requirements.txt

RUN apt-get install -y python-pip
RUN pip install -r requirements.txt

WORKDIR /tmp

# SPI- / MFRC522-Modules
# ---------------------------
RUN git clone https://github.com/lthiery/SPI-Py.git
RUN git clone https://github.com/mxgxw/MFRC522-python.git

WORKDIR /tmp/SPI-Py
RUN python setup.py install

WORKDIR /tmp/MFRC522-python
RUN python Read.py

WORKDIR /usr/src/app
CMD [ "python", "./server/server_buttons.py" ]
