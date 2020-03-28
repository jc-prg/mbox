FROM python:3.7

ENV DEBIAN_FRONTEND noninteractive
ENV uid 1000
ENV gid 1000

RUN apt-get update

# install required PYTHON3 modules
# ---------------------------
COPY ./requirements.txt ./requirements.txt
RUN pip install -r requirements.txt

# install and configure VLC
# ---------------------------
RUN useradd -m vlc; \
    apt-get install -y vlc \
    rm -rf /var/lib/apt/lists/*

WORKDIR /usr/src/app
CMD [ "python", "./server/server.py" ]
