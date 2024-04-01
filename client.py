import argparse
import os
import socket
import sys
import time

import confundo

parser = argparse.ArgumentParser("Parser")
parser.add_argument("host", help="Set Hostname")
parser.add_argument("port", help="Set Port Number", type=int)
parser.add_argument("file", help="Set File Directory")
args = parser.parse_args()

def start():
    try:
        with confundo.Socket() as sock:
            sock.settimeout(10)
            sock.connect((args.host, int(args.port)))

            # Perform 3-way handshake
            sock.sendSynPacket()  # Send SYN packet
            sock.expectSynAck()  # Expect SYN-ACK response

            with open(args.file, "rb") as f:
                data = f.read(50000)
                while data:
                    total_sent = 0
                    while total_sent < len(data):
                        sent = sock.send(data[total_sent:])
                        total_sent += sent
                    data = f.read(50000)

            # Gracefully terminate the connection
            sock.close()
    except (RuntimeError, socket.timeout, socket.error) as e:
        sys.stderr.write(f"ERROR: {e}\n")
        sys.exit(1)

if __name__ == '__main__':
    start()
