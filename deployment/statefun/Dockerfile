FROM python:3.8

COPY /benchmark/ /benchmark
COPY ./requirements.txt /benchmark/requirements.txt
ADD stateful_dataflows.tgz /

RUN pip install -r benchmark/requirements.txt
RUN pip install ../stateful_dataflows/

EXPOSE 80

ENTRYPOINT ["gunicorn", "-b", "0.0.0.0:80", "-w 4", "-k aiohttp.GunicornWebWorker",  "benchmark.runtime_statefun:app"]
