from flask import Flask, request
import logging as log
import pickle 
import socket

log.basicConfig(format='[FS: %(asctime)s] %(message)s',
                datefmt='%I:%M:%S %p',
                level=log.INFO)

app = Flask(__name__)
BUFFER_SIZE = 1024

@app.route('/')
def blah():
    return " Fibonacci Server (FS)"

def fib(n1):
    if n1 < 0:
        raise ValueError(f"n should be > 0, got n1={n1}")
    elif n1 == 0:
        return 0
    elif n1 == 1 or n1 == 2:
        return 1
    else:
        return fib(n1 - 1) + fib(n1 - 2)

@app.route('/register', methods=['PUT'])
def register():
    body = request.json
    log.info(f"/register got body={body!r}")
    if not body:
        raise ValueError("body is None")
    hostname = body["hostname"]
    fs_ip    = body["fs_ip"]
    as_ip    = body["as_ip"]
    as_port  = body["as_port"]
    ttl      = body["ttl"]
    register_with_as(as_port=as_port,
                     as_ip=as_ip,
                     hostname=hostname,
                     value=fs_ip,
                     type="A",
                     ttl=ttl)
    return "Registration Done!"


@app.route('/fibonacci')
def fibonacci():
    n1 = int(request.args.get('number'))
    log.info(f"/fibonacci got n1={n1}")
    return str(fib(n1))


def register_with_as(as_ip, as_port, hostname, value, type, ttl):
    msg = ((hostname, value, type, ttl))
    msg_bytes = pickle.dumps(msg)
    as_addr = (as_ip, as_port)
    udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    log.info(f"Sending {msg} to {as_addr} via UDP socket")
    udp_socket.sendto(msg_bytes, as_addr)


if __name__ == '__main__':
    app.run(host='0.0.0.0',
            port=9090,
            debug=True)