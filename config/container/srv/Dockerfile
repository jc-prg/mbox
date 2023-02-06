FROM ubuntu:18.04

ENV DEBIAN_FRONTEND=noninteractive

RUN apt-get -y update #&& apt-get -y upgrade
RUN apt-get install -y python3 python3-distutils python3-pip python3-apt apt-utils
RUN python3 -m pip install -U setuptools
RUN python3 -m pip install -U wheel

# install required PYTHON3 modules
# ---------------------------
COPY ./requirements.txt ./requirements.txt
RUN pip3 install -r requirements.txt

# install and configure VLC
# ---------------------------
# RUN apt -y update
RUN apt install -y vlc #--fix-missing
RUN useradd -m vlcuser
RUN rm -rf /var/lib/apt/lists/*

# RUN apt -y update && apt -y install iputils-ping
RUN apt -y install iputils-ping
RUN apt -y install locales
#RUN apt -y install locales locales-all

ENV PYTHONIOENCODING=utf-8
ENV LANG=en_US.UTF-8
ENV LANGUAGE=en_US:en
ENV LC_ALL=en_US.UTF-8

WORKDIR /usr/src/app
CMD [ "/usr/bin/python3", "./server/server.py" ]
