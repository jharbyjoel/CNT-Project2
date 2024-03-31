import argparse
import os
import socket
import sys
import time

import confundo

parser = argparse.ArgumentParser("Client")
parser.add_argument("host", help="Hostname or IP address of the server")
parser.add_argument("port", help="Port number of the server", type=int)
parser.add_argument("file", help="Name of the file to transfer")
args = parser.parse_args()

def start():
    try:
        with confundo.Socket() as sock:
            sock.settimeout(10)
            sock.connect((args.host, args.port))

            # Perform three-way handshake
            sock.send_syn()
            syn_ack = sock.receive()
            if syn_ack.is_syn_ack():
                sock.send_ack(syn_ack)

                # Read file and send in segments
                with open(args.file, "rb") as f:
                    while True:
                        data = f.read(confundo.MAX_SEGMENT_SIZE)
                        if not data:
                            break
                        sock.send_data(data)

                # Send FIN packet after file transmission
                sock.send_fin()
                fin_ack = sock.receive()
                if fin_ack.is_ack():
                    # Wait for 2 seconds for incoming FIN packets
                    start_time = time.time()
                    while time.time() - start_time < 2:
                        packet = sock.receive()
                        if packet.is_fin():
                            sock.send_ack(packet)
                    sys.exit(0)  # Gracefully terminate after receiving FIN packet
                else:
                    sys.stderr.write("ERROR: Did not receive expected ACK for FIN\n")
                    sys.exit(1)
            else:
                sys.stderr.write("ERROR: Did not receive expected SYN-ACK\n")
                sys.exit(1)

    except RuntimeError as e:
        sys.stderr.write(f"ERROR: {e}\n")
        sys.exit(1)

if __name__ == '__main__':
    start()


