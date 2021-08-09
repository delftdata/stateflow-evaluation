FROM python:3.8

COPY /benchmark/ /benchmark
COPY ./requirements.txt /benchmark/requirements.txt
ADD stateful_dataflows.tar.xz /

WORKDIR /benchmark
RUN pip install -r requirements.txt
RUN pip install ../stateful_dataflows/
