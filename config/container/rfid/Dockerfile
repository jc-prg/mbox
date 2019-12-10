FROM python:3
#FROM armv7/armhf-ubuntu

RUN apt-get update && apt-get install -y \
    python3-pip


# install required PYTHON modules
# ---------------------------
COPY ./requirements.txt ./requirements.txt

RUN pip3 install -r requirements.txt

WORKDIR /tmp

# SPI- / MFRC522-Modules
# ---------------------------
#RUN git clone https://github.com/mxgxw/MFRC522-python.git

RUN git clone https://github.com/lthiery/SPI-Py.git
WORKDIR /tmp/SPI-Py
RUN git checkout 8cce26b9ee6e69eb041e9d5665944b88688fca68
RUN python setup.py install

#WORKDIR /tmp/MFRC522-python
#CMD [ "python", "Read.py" ]

WORKDIR /usr/src/app/server
CMD [ "python", "server_rfid.py" ]
