FROM python:3
#FROM ubuntu:18.04

ENV DEBIAN_FRONTEND noninteractive
ENV uid 1000
ENV gid 1000

RUN apt-get update

# install required PYTHON3 modules
# ---------------------------
COPY ./requirements.txt ./requirements.txt

#RUN apt-get install -y python3
RUN apt-get install -y python3-pip
RUN pip3 install -r requirements.txt

# install and configure VLC
# ---------------------------
RUN useradd -m vlc; \
    apt-get install -y vlc; \
    rm -rf /var/lib/apt/lists/*

#COPY start-vlc.sh /tmp/
#ENTRYPOINT ["/tmp/start-vlc.sh"]

WORKDIR /usr/src/app
CMD [ "python", "./server/server.py" ]
