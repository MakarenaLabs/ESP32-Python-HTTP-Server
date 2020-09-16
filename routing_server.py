# MODULES IMPORT

import os, sys
import argparse
import serial
from time import sleep
import multiprocessing
import sys
import requests
import json


# CONST DEFINITION

REQ_ENDPOINT = "http://localhost:5000"

ser = None
route_path = None
max_n_byte = None


# FUNCTIONS

def sendCommand(s, debug=True):

    """
    Parameters
    ----------
    s : str
        String to send
    debug : bool
        Boolean to define debug prints
    """

    global ser

    ser.write(str.encode(s + "\r\n"))
    sleep(0.1)

    ret = ""
    while ser.inWaiting():
        ret = ser.readline().decode("utf-8").replace("\n", "").replace("\r", "")

    if debug:
        print("sent:", s)
        print("response: ", ret)
        print("")

    return ret


def sendPage(link, route):

    """
    Parameters
    ----------
    link : str
        Link to send
    route : str
        Route string
    """

    global route_path
    global max_n_byte

    data = None
    ct = "text/html"

    if ".css" in route or ".js" in route or ".html" in route:
        with open(route_path + route, 'r') as f:
            data = f.read()
    else:
        print("NOT MANAGED:", route)
        data = ""

    # Content-type definition
    if ".css" in route:
        ct = "text/css"
    elif ".js" in route:
        ct = "text/javascript"
    elif ".png" in route:
        ct = "image/png"
    elif ".ico" in route:
        ct = "image/x-icon"

    if ".css" in route or ".js" in route or ".html" in route:
        data = data.replace('\r', '').replace('\n', '').replace('\0', '').strip() + "\\0"
    else:
        data = ""

    # Creation of page to send as command for ESP32 module
    header = 	"HTTP/1.1 200 OK\n"+\
                "Content-Type: " + ct + "\n"+\
                "Connection: Closed\n\n";

    commandSendPage = header
    commandSendPage += data
    if len(commandSendPage) < 2048:
        val = sendCommand('AT+CIPSENDEX=' + link + ',' + str(len(data) + len(header)))
        if val.startswith(">"):
            print(commandSendPage)
            sendCommand(commandSendPage)
            print("Sent")

    else:
        i = 0
        # Sending all page by ESP32 module
        while i*max_n_byte < len(commandSendPage):
            tmp = commandSendPage[i*max_n_byte:(i+1)*max_n_byte]
            #print("remaining "+str(len(commandSendPage)-(i*2048))+" bytes")
            val = sendCommand('AT+CIPSENDEX=' + link + ',' + str(len(tmp)), debug=False)	
            if val.startswith(">"):
                sendCommand(tmp, debug=False)
                i = i+1
            #else:
                #print("There are some errors here!")
                #print(i)
        print("Sent")

    sendCommand('AT+CIPCLOSE=' + link)


def routing(link, route, val, dataPost="", method="GET"):

    """
    Parameters
    ----------
    link : str
        Link to send
    route : str
        Route string
    val : str
        Row from
    dataPost : str
        Data to be sent in POST requests
        default : ""
    method : str
        Requests method.
        default : GET
    """

    if route == "/devices":
        if method == "GET":
            # Get response in json format
            resp = json.dumps(requests.get(REQ_ENDPOINT + '/devices').json())
            print(resp)
            # Creation of body to send by esp32 module
            header = 	"HTTP/1.1 200 OK\n"+\
                "Content-Type: " + "application/json" + "\n"+\
                "Connection: Closed\n\n";
            commandSendPage = header
            commandSendPage += resp
            val = sendCommand('AT+CIPSENDEX=' + link + ',' + str(len(resp) + len(header)))
        elif method == "POST":
            print(dataPost)
            # Creation of POST request. POST of devices configurations (ON/OFF)
            resp = " "
            headers = {'content-type': 'application/json'}
            requests.post(REQ_ENDPOINT + "/devices", data=dataPost, headers=headers)
            # Creation of body to send by esp32 module
            header = 	"HTTP/1.1 200 OK\n"+\
                "Content-Type: " + "application/json" + "\n"+\
                "Connection: Closed\n\n";
            commandSendPage = header
            commandSendPage += resp
            val = sendCommand('AT+CIPSENDEX=' + link + ',' + str(len(resp) + len(header)))
        if val.startswith(">"):
            # Here I can send the page to serial
            print(commandSendPage)
            sendCommand(commandSendPage)
            print("Sent")
        # Closing connection
        sendCommand('AT+CIPCLOSE=' + link)
    

def mainServer():
    isParsingPost = False
    dataPost = ""
    link = ""
    route = ""
    method = ""
    while True:
        while ser.inWaiting():
            # Get data from serial, line by line
            val = ser.readline().decode("utf-8").replace("\n","").replace("\r","")
            print("[logs]", val)
            # Check content of data
            if "POST" in val:
                # Here the request is a POST
                method = "POST"
                isParsingPost = True
                link = val.split(",")[1]
                route = val.split(" ")[1]		
            elif "}" in val and isParsingPost:
                # Here I have to parse POST request
                isParsingPost = False
                dataPost = val
                print("ROUTE: ->", route)
                routing(link, route, val, dataPost, method)
            elif "+IPD," in val and "HTTP/1.1" in val and not isParsingPost:
                # Here the request is a GET
                method = "GET"
                link = val.split(",")[1]
                route = val.split(" ")[1]
                print("ROUTE: ->", route)
                
                # Routing to index page
                if route == "/":
                    route += "index.html"
                
                if "." in route:
                    # Here page is sent by esp32
                    sendPage(link, route)
                else:
                    routing(link, route, val)

# MAIN FUNCTION

def main(args):

    global ser
    global route_path
    global max_n_byte

    ser = serial.Serial(args.serial, args.baudrate, timeout=args.serial_timeout)
    route_path = args.route_path
    max_n_byte = args.max_n_bytes

    sendCommand('AT')
    sendCommand('AT+GMR')

    sendCommand('AT+CWMODE=2') #SET SoftAP (NO Station Mode)
    sendCommand('AT+CIPMUX=1') #DISABLE Multiple connections
    sendCommand('AT+CIPSERVERMAXCONN=1') #SET max connection at the same time
    sendCommand('AT+CIPSERVER=1') #ENABLE TCP Server (default port: 333)
    sendCommand('AT+CIPDINFO=1') #ENABLE deep connection infos (IP, links, etc...)
    sendCommand('AT+CWSAP="AZURE_BL_PMOD_DEMO","",1,0')  #SET AP name, psw, broadcastable and psw encryption (0=none)
    sendCommand('AT+CWDHCP=1,1') #SET DHCP on Station
    sendCommand('AT+CWDHCP=1,2') #SET DHCP on SoftAP

    queue = multiprocessing.JoinableQueue(maxsize = 1)
    worker = multiprocessing.Process(name="SerialReader", target=mainServer, args=())
    worker.start()

    while True:
        d = None


if __name__ == "__main__":

    parser = argparse.ArgumentParser(description='DESCRIPTION TODO')
    parser.add_argument('--serial', '-s', action='store', default='/dev/ttyUSB0', dest='serial',
                        help='serial port')
    parser.add_argument('--baudrate', '-b', action='store', default='115200', dest='baudrate', type=int,
                        help='baudrate')
    parser.add_argument('--serial_timeout', '-st', action='store', default='0.100', dest='serial_timeout', type=float,
                        help='serial timeout')
    parser.add_argument('--route_path', '-r', action='store', dest='route_path', required=True,
                        help='dashboard route path')
    parser.add_argument('--max_n_bytes', '-mb', action='store', default='2048', dest='max_n_bytes', type=int,
                        help='max number of bytes to send every time')

    args = parser.parse_args()

    main(args)






