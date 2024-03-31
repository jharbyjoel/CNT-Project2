import sys
import argparse
import socket
import signal

import confundo

def start():
    try:
        with confundo.Socket() as sock:
            sock.settimeout(10)
            sock.bind(('localhost', 5000))
            sock.listen(1)
            conn, addr = sock.accept()
            with conn:
                print('Connected by', addr)
                while True:
                    data = conn.recv(50000)
                    if not data:
                        break
                    conn.sendall(data)
    except RuntimeError as e:
        sys.stderr.write(f"ERROR: {e}\n")
        sys.exit(1)

if __name__ == '__main__':
    start()
