# Benchmark deployment details
To deploy the benchmark we picked an EC2 instance, but this could be any compute instance. Its easiest if the instance
has some default installations, so we picked an Ubuntu distribution. Then we installed `wrk2`:
```bash
https://github.com/giltene/wrk2.git
sudo apt update
sudo apt-get install build-essential
sudo apt-get install libssl-dev
sudo apt-get install zlib1g-dev
cd wrk2
make
```
This will build a `wrk` executable. Finally we install a `lua` dependency:
```
sudo apt-get update -y
sudo apt-get install -y luarocks
sudo luarocks install luasocket
```

## Experiments
First, copy all `.lua` files to the `wrk2` folder on your instance. Then, we run two kind of experiments:
1. A low throughput experiment, where we benchmark the runtime per endpoint. The commands for that are:
```bash
./wrk -t 4 -c 10 -d 30s -R 10 -s './hotel_user.lua' -L '{LOADBALANCER_URL}'
./wrk -t 4 -c 10 -d 30s -R 10 -s './hotel_search.lua' -L '{LOADBALANCER_URL}'
./wrk -t 4 -c 10 -d 30s -R 10 -s './hotel_recommend.lua' -L '{LOADBALANCER_URL}'
./wrk -t 4 -c 10 -d 30s -R 10 -s './hotel_reserve.lua' -L '{LOADBALANCER_URL}'
```
This will send 10rps for 30 seconds, per endpoint, and report the latency for different percentiles.
2. We keep increasing the throughput `[100, 200, 300, 400, 500, 600, 700]` and measure latency for 60 seconds.
```bash
./wrk -t 8 -c 200 -d 60s -R 100 -s './hotel.lua' -L '{LOADBALANCER_URL}'
./wrk -t 8 -c 300 -d 60s -R 200 -s './hotel.lua' -L '{LOADBALANCER_URL}'
./wrk -t 8 -c 400 -d 60s -R 300 -s './hotel.lua' -L '{LOADBALANCER_URL}'
./wrk -t 8 -c 500 -d 60s -R 400 -s './hotel.lua' -L '{LOADBALANCER_URL}'
./wrk -t 8 -c 600 -d 60s -R 500 -s './hotel.lua' -L '{LOADBALANCER_URL}'
./wrk -t 8 -c 700 -d 60s -R 600 -s './hotel.lua' -L '{LOADBALANCER_URL}'
./wrk -t 8 -c 800 -d 60s -R 700 -s './hotel.lua' -L '{LOADBALANCER_URL}'
```

**Note** For AWS we ran everything _twice_ to deal with hot/cold starts. 
