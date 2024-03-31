import argparse
import os
import socket
import sys

import confundo

parser = argparse.ArgumentParser("Server")
parser.add_argument("port", help="Port number to listen on", type=int)
args = parser.parse_args()

def start():
    try:
        with confundo.Socket() as sock:
            sock.bind(("0.0.0.0", args.port))
            sock.listen()

            # Accept incoming connections
            conn, addr = sock.accept()
            with conn:
                print("Connected by", addr)

                # Perform three-way handshake
                syn_packet = conn.recv()
                if syn_packet.is_syn():
                    conn.send_syn_ack()

                    # Receive file data
                    with open("received_file.txt", "wb") as f:
                        while True:
                            data_packet = conn.recv()
                            if not data_packet:
                                break
                            f.write(data_packet.get_payload())

                    # Send ACK for FIN packet
                    fin_packet = conn.recv()
                    if fin_packet.is_fin():
                        conn.send_ack(fin_packet)
                    else:
                        sys.stderr.write("ERROR: Did not receive expected FIN packet\n")
                        sys.exit(1)

                else:
                    sys.stderr.write("ERROR: Did not receive expected SYN packet\n")
                    sys.exit(1)

    except RuntimeError as e:
        sys.stderr.write(f"ERROR: {e}\n")
        sys.exit(1)

if __name__ == '__main__':
    start()

