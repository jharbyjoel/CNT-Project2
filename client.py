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

CHUNK_SIZE = 1024  # Adjust as needed
CWND = 412  # Initial congestion window size
SS_THRESH = 64  # Initial slow start threshold
MAX_CHUNKS = 3  # Maximum number of chunks to send before waiting for acknowledgments

def start():
    try:
        with confundo.Socket() as sock:
            sock.settimeout(10)
            sock.connect((args.host, int(args.port)))

            # Perform 3-way handshake
            sock.sendSynPacket()  # Send SYN packet
            sock.expectSynAck()  # Expect SYN-ACK response

            total_sent = 0
            seqNum = sock.seqNum  # Initialize sequence number
            while True:
                data = b''
                for _ in range(MAX_CHUNKS):
                    chunk = f.read(CHUNK_SIZE)
                    if not chunk:
                        break
                    data += chunk

                if not data:
                    break  # End of file reached

                # Send data with the current sequence number
                sent = sock.send(data, seqNum)
                total_sent += sent
                seqNum += sent  # Update sequence number for next segment

                # Update congestion window size
                if CWND < SS_THRESH:
                    CWND += 412  # Slow start
                else:
                    CWND += (412 * 412) // CWND  # Congestion avoidance

                # Wait for ACK
                while True:
                    try:
                        pkt = sock._recv()
                        if pkt and pkt.isAck:
                            break  # Received ACK for the chunk
                    except socket.timeout:
                        sys.stderr.write("ERROR: Timeout waiting for ACK\n")
                        # Adjust congestion window and slow start threshold after timeout
                        SS_THRESH = CWND // 2
                        CWND = 412
                        # Retransmit data after the last acknowledged byte
                        f.seek(total_sent)
                        break

            # Gracefully terminate the connection
            sock.close()
    except (RuntimeError, socket.error) as e:
        sys.stderr.write(f"ERROR: {e}\n")
        sys.exit(1)

if __name__ == '__main__':
    start()
