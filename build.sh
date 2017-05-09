RUNCMD="ampy --port /dev/ttyUSB0 run build/esp8266_trains.py"

[ ! -d "build" ] && mkdir build

cat esp8266_trains.py | sed -e "s/\${API_KEY}/$(cat apikey.txt)/" > build/esp8266_trains.py

[ "$1" = "run" ] && $RUNCMD
