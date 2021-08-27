FROM ubuntu:18.04

ENV DEBIAN_FRONTEND=noninteractive

RUN apt-get -y update && apt-get install -y python3 python3-distutils python3-pip python3-apt

COPY ./requirements.txt ./requirements.txt

RUN pip3 install -r requirements.txt

WORKDIR /usr/src/app/server
CMD [ "python3", "server_led.py" ]
