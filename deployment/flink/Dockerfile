FROM flink:1.13.0
# install python3 and pip3
RUN apt-get update -y && \
apt-get install -y python3.7 python3-pip python3.7-dev && rm -rf /var/lib/apt/lists/*
RUN ln -s /usr/bin/python3 /usr/bin/python
RUN pip3 install --upgrade pip

# install Python Flink
RUN pip3 install apache-flink==1.13.0