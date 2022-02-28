import requests
import socket
import pickle

from flask import Flask, request

import logging as log
log.basicConfig(format='[US: %(asctime)s] %(message)s',
                datefmt='%I:%M:%S %p',
                level=log.INFO)

app = Flask(__name__)


BUFFER_SIZE = 2048

@app.route('/')
def hello_world():
    return 'This is User Server (US)'

@app.route('/fibonacci', methods=["GET"])
def fibonacci():
    # Fibonacci Server hostname
    hostname = request.args.get('hostname')
    fs_port  = int(request.args.get('fs_port'))
    # Fibonacci number to calculate
    number   = int(request.args.get('number'))
    # Authorative server IP, port
    as_ip    = request.args.get('as_ip')
    as_port  = int(request.args.get('as_port'))
    fs_ip = get_fs_ip_from_as(hostname=hostname,
                              as_ip=as_ip,
                              as_port=as_port)

def get_fs_ip_from_as(hostname, as_ip, as_port):
    log.info(f"Getting FS {hostname!r} IP from AS {as_ip}:{as_port}")
    # fs_ip = "localhost"
    as_addr = (as_ip, int(as_port))
    SERVER_UDP_SOCKET = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    hostname = hostname.replace('"', '')
    msg_bytes = pickle.dumps(("A", hostname))
    as_ip = as_ip.replace('"', '')
    SERVER_UDP_SOCKET.sendto(msg_bytes, (as_ip, int(as_port)))
    response, _ = SERVER_UDP_SOCKET.recvfrom(BUFFER_SIZE)
    response = pickle.loads(response)
    type, hostname, fs_ip, ttl = response
    log.info(f"Resolved fs {hostname!r} to IP {fs_ip}")
    return fs_ip

app.run(host='0.0.0.0',
        port=8080,
        debug=True)