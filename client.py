import argparse
import os
import socket
import sys

# Assuming confundo is the module where your protocol implementation resides
import confundo

parser = argparse.ArgumentParser(description="Confundo Protocol Client")
parser.add_argument("file", help="Path to the file to send")
args = parser.parse_args()

def start():
    server_ip = "131.94.128.43"
    server_port = 54000

    try:
        with confundo.Socket() as sock:
            sock.settimeout(10)
            # Connecting to the provided server
            sock.connect((server_ip, server_port))

            with open(args.file, "rb") as f:
                while True:
                    data = f.read(50000)  # Adjust the chunk size as needed
                    if not data:
                        break  # End of file
                    sock.sendall(data)  # Ensure this matches your protocol's method for sending data

            # Assume there's a method to properly close the connection as per your protocol
            # This might involve sending a FIN packet and waiting for an ACK, for example
            sock.close_connection()
    except Exception as e:
        sys.stderr.write(f"ERROR: {e}\n")
        sys.exit(1)

if __name__ == '__main__':
    start()

