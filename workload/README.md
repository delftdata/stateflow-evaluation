```bash
sudo luarocks install luasocket

export PYFLINK_CLIENT_EXECUTABLE=/usr/bin/python3.8
./bin/flink run -pyexec /usr/bin/local/python3.8 --python ~/Documents/stateflow-evaluation/benchmark/runtime.py --parallelism 4
./flink run \
  --target local \
  -m localhost:8081 \
  -pyarch venv.zip \
  -pyexec venv.zip/venv/bin/python \
  --parallelism 1 \
  --python ~/Documents/stateflow-evaluation/benchmark/runtime.py \
  --jarfile ~/Documents/stateflow-evaluation/benchmark/bin/combined.jar

```

sudo ./wrk -t 4 -c 10 -d 30s -R 10 -s "./hotel.lua" -L "http://localhost:8001"