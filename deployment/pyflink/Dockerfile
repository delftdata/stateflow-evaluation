FROM flink:1.13.0

# install python3 and pip3
RUN apt-get update -y && \
apt-get install -y python3 python3-pip python3-dev && rm -rf /var/lib/apt/lists/*
RUN ln -s /usr/bin/python3 /usr/bin/python

# install Python Flink
RUN pip3 install apache-flink==1.13.0

RUN python --version

COPY venv.zip venv.zip
RUN unzip venv.zip

COPY stateful_dataflows.zip stateflow.zip
RUN unzip stateflow.zip
RUN pip3 install stateful_dataflows/
RUN pip3 install pytest

ENV PYTHON_PATH=~/venv/bin/python
ENV PYFLINK_CLIENT_EXECUTABLE=~/venv/bin/python