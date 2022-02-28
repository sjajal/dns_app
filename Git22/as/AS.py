import time
import os
import logging as log
import socket
import pickle
import json


log.basicConfig(format='[%(asctime)s %(filename)s:%(lineno)d] %(message)s',
                datefmt='%I:%M:%S %p',
                level=log.DEBUG)

HOST_IP = "0.0.0.0"
SERVER_PORT = 53533



def save_dns_record(name, value, type, ttl):
    
    if not os.path.exists(AUTH_SERVER_DB_FILE):
        with open(AUTH_SERVER_DB_FILE, "w") as f:
            json.dump({}, f, indent=4)

    with open(AUTH_SERVER_DB_FILE, "r") as f:
        existing_records = json.load(f)

    ttl_ts = time.time() + int(ttl)

    existing_records[name] = (value, ttl_ts, ttl)

    with open(AUTH_SERVER_DB_FILE, "w") as f:
        json.dump(existing_records, f, indent=4)
        log.debug(f"Saving DNS record for {name} {(value, ttl_ts, ttl)}")

AUTH_SERVER_DB_FILE = "/tmp/auth_db.json"
TYPE = "A"
BUFFER_SIZE = 1024



def get_dns_record(name):
    with open(AUTH_SERVER_DB_FILE, "r") as f:
        existing_records = json.load(f)

    if name not in existing_records:
        log.info(f"No DNS record found for {name}")
        return

    value, ttl_ts, ttl = existing_records[name]
    log.debug(f"Got DNS records for {name}: {existing_records[name]}")
    log.debug(f"Curr time={time.time()} ttl_ts={ttl_ts}")
    if time.time() > ttl_ts:
        log.info(f"TTL expired for {name}")
        return None
    return (TYPE, name, value, ttl_ts, ttl)


def main():
    udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    udp_socket.bind((HOST_IP, SERVER_PORT))
    log.info(f"UDP server up and listening on "
             f"{socket.gethostbyname(socket.gethostname())}:{SERVER_PORT}")

    while (True):
        msg_bytes, client_addr = udp_socket.recvfrom(BUFFER_SIZE)
        msg = pickle.loads(msg_bytes)
        log.info(f"Message from Client: {msg!r}")
        if len(msg) == 4:
            name, value, type, ttl = pickle.loads(msg_bytes)
            save_dns_record(name=name, type=type, value=value, ttl=ttl)
        elif len(msg) == 2:
            type, name = msg
            dns_record = get_dns_record(name)
            if dns_record:
                (_, name, value, _, ttl) = dns_record
                response = (type, name, value, ttl)
            else:
               
                response = ""
            response_bytes = pickle.dumps(response)
            
            udp_socket.sendto(response_bytes, client_addr)
        else:
            msg = f"Expected msg of len 4 or 2, got :{msg!r}"
            log.error(msg)
            udp_socket.sendto(msg, client_addr)


if __name__ == '__main__':
    log.info("Starting up authoritative server")
    main()