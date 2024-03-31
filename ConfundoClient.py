import socket
import struct
import sys
import os
import time

# Constants Variables
HEADER_FORMAT = "!IIHB"
HEADER_SIZE = 12
MTU = 424
PAYLOAD_SIZE = MTU - HEADER_SIZE
SEQ_NUM_MAX = 50000
INITIAL_SEQ_NUM = 50000
CWND_INITIAL = 412
SS_THRESH_INITIAL = 12000
RETRANSMISSION_TIMEOUT = 0.5
FIN_WAIT_TIME = 2
CONNECTION_TIMEOUT = 10

# Header flag
ACK = 0b001
SYN = 0b010
FIN = 0b100

# Helper functions for packing and unpacking headers
def pack_header(seq_num, ack_num, conn_id, flags):
    return struct.pack(HEADER_FORMAT, seq_num, ack_num, conn_id << 3 | flags, 0)

def unpack_header(data):
    seq_num, ack_num, flags, _ = struct.unpack(HEADER_FORMAT, data[:HEADER_SIZE])
    conn_id = flags >> 3
    flags = flags & 0b111
    return seq_num, ack_num, conn_id, flags

class ConfundoClient:
    def __init__(self, server_ip, server_port, filename):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.server_address = (server_ip, server_port)
        self.filename = filename
        self.seq_num = INITIAL_SEQ_NUM
        self.ack_num = 0
        self.conn_id = 0
        self.cwnd = CWND_INITIAL
        self.ss_thresh = SS_THRESH_INITIAL
        self.sock.settimeout(CONNECTION_TIMEOUT)
    
    def send_packet(self, flags, payload=b''):
        header = pack_header(self.seq_num, self.ack_num, self.conn_id, flags)
        self.sock.sendto(header + payload, self.server_address)
        print(f"SEND {self.seq_num} {self.ack_num} {self.conn_id} {self.cwnd} {self.ss_thresh} {flags}")

    def recv_ack(self):
        while True:
            try:
                data, _ = self.sock.recvfrom(MTU)
                seq_num, ack_num, conn_id, flags = unpack_header(data)
                # Basic validation
                if conn_id != self.conn_id or not flags & ACK:
                    continue  # Skip invalid or non-ACK packets
                self.ack_num = seq_num + len(data) - HEADER_SIZE
                return ack_num
            except socket.timeout:
                break  # Handle retransmission or failure
    
    def establish_connection(self):
        self.send_packet(SYN)
        self.conn_id = self.recv_ack()  # SYN-ACK should carry the server's conn_id
        self.send_packet(ACK)

    def transfer_file(self):
        with open(self.filename, 'rb') as f:
            while (chunk := f.read(PAYLOAD_SIZE)):
                self.send_packet(ACK, chunk)
                if not self.recv_ack():
                    break  # Handle retransmission or adjust cwnd based on congestion control logic
                # Congestion control (simplified)
                if self.cwnd < self.ss_thresh:
                    self.cwnd += PAYLOAD_SIZE  # Slow start
                else:
                    self.cwnd += int(PAYLOAD_SIZE**2 / self.cwnd)  # Congestion avoidance

    def terminate_connection(self):
        self.send_packet(FIN)
        self.recv_ack()  # Wait for ACK of FIN
        time.sleep(FIN_WAIT_TIME)  # Wait for possible FIN from the server
        self.sock.close()

    def run(self):
        try:
            self.establish_connection()
            self.transfer_file()
            self.terminate_connection()
        except Exception as e:
            print(f"ERROR: {e}", file=sys.stderr)
            self.sock.close()

if __name__ == "__main__":
    if len(sys.argv) != 4:
        print("Usage: python3 client.py <HOSTNAME-OR-IP> <PORT> <FILENAME>", file=sys.stderr)
        sys.exit(1)
    client = ConfundoClient(sys.argv[1], int(sys.argv[2]), sys.argv[3])
    client.run()
