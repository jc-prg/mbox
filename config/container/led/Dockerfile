FROM python:3
#FROM armv7/armhf-ubuntu

RUN apt-get update && apt-get install -y \
    python3-pip
COPY ./requirements.txt ./requirements.txt

RUN pip3 install -r requirements.txt

WORKDIR /usr/src/app/server
CMD [ "python", "server_led.py" ]
