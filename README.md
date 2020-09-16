# ESP32 Python Routing Server

This tool provides a simple routing server to communicate by ESP32 module.

## Prerequisites
 - Python v3.6
 - Simple frontend html file (max 2048 bytes)

## How to start
To start program use the following command:
```
sudo python3 routing_server.py -b 390625 -r /home/xilinx/azure-iot-dashboard-mini/
```

Connection to ESP32 module is provided on endpoint
```
192.168.4.1:333
```

## How to use
This tool is written in ```Python3``` and with ```--help``` parameter provides a list of arguments (optional and required) to set, with their default values:
```
usage: routing_server.py [-h] [--serial SERIAL] [--baudrate BAUDRATE]
                         [--serial_timeout SERIAL_TIMEOUT] --route_path
                         ROUTE_PATH [--max_n_bytes MAX_N_BYTES] [--test]

DESCRIPTION TODO

optional arguments:
  -h, --help            show this help message and exit
  --serial SERIAL, -s SERIAL
                        serial port
  --baudrate BAUDRATE, -b BAUDRATE
                        baudrate
  --serial_timeout SERIAL_TIMEOUT, -st SERIAL_TIMEOUT
                        serial timeout
  --route_path ROUTE_PATH, -r ROUTE_PATH
                        dashboard route path
  --max_n_bytes MAX_N_BYTES, -mb MAX_N_BYTES
                        max number of bytes to send every time
  --test                setting test environment
```

### Description of arguments
There is only one argument required:
 - ```--route_path, -r```: route path of frontend file to serve. This field is required.

The others are optional and have a default value:
 - ```--serial, -s```: the communication serial port (default ```/dev/ttyUSB0```)
 - ```--baudrate, -b```: communication baudrate (default ```115200```)
 - ```---serial_timeout, -st```: serial timeout (default ```0.100```)
 - ```--max_n_bytes, -mb```: max number of bytes to send (default ```2048```)

# Credits
MakarenaLabs - [staff@makarenalabs.com](mailto:staff@makarenalabs.com)