FROM ubuntu:20.04

ENV TZ=Europe/Berlin
ENV DEBIAN_FRONTEND=noninteractive
RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone

RUN apt-get -y update && apt-get install -y python3 python3-distutils python3-pip python3-apt

# install required PYTHON3 modules
# ---------------------------
COPY ./requirements.txt ./requirements.txt
RUN pip install -r requirements.txt


# install and configure VLC
# ---------------------------
RUN apt-get install -y vlc #--fix-missing
RUN useradd -m vlcuser
RUN rm -rf /var/lib/apt/lists/*

RUN apt -y update && apt -y install iputils-ping

WORKDIR /usr/src/app
CMD [ "/usr/bin/python3", "./server/server.py" ]
