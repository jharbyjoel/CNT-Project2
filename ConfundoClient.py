import socket
import struct
import sys
import os
import time

# Constants
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

# Flags
ACK = 0b001
SYN = 0b010
FIN = 0b100

# Helper functions
def pack_header(seq_num, ack_num, conn_id, flags):
    return struct.pack(HEADER_FORMAT, seq_num, ack_num, conn_id, flags)

def unpack_header(data):
    seq_num, ack_num, conn_id_flags, _ = struct.unpack(HEADER_FORMAT, data[:HEADER_SIZE])
    conn_id = conn_id_flags >> 3
    flags = conn_id_flags & 0b111
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
    
    def increment_seq_num(self, increment=1):
        self.seq_num = (self.seq_num + increment) % (SEQ_NUM_MAX + 1)
    
    def log_packet(self, action, seq_num, ack_num, conn_id, flags):
        flags_str = ' '.join([flag for flag, present in [("ACK", ACK), ("SYN", SYN), ("FIN", FIN)] if flags & present])
        print(f"{action} {seq_num} {ack_num} {conn_id} {self.cwnd} {self.ss_thresh} {flags_str}")
    
    def send_packet(self, flags, payload=b''):
        if flags & FIN:  # FIN takes one byte logically
            self.increment_seq_num()
        header = pack_header(self.seq_num, self.ack_num, self.conn_id << 3 | flags, 0)
        self.sock.sendto(header + payload, self.server_address)
        self.log_packet("SEND", self.seq_num, self.ack_num, self.conn_id, flags)
        if payload or flags & SYN:  # Increment for SYN or data payload
            self.increment_seq_num(len(payload))

    def send_packet_with_retransmission(self, flags, payload=b''):
        attempts = 0
        while attempts < 3:  # Limit retransmission attempts
            self.send_packet(flags, payload)
            if self.recv_ack():
                return True
            attempts += 1
        return False

    def recv_ack(self):
        try:
            data, _ = self.sock.recvfrom(MTU)
            seq_num, ack_num, conn_id, flags = unpack_header(data)
            if flags & ACK and conn_id == self.conn_id:
                self.ack_num = ack_num
                self.log_packet("RECV", seq_num, ack_num, conn_id, flags)
                return True
        except socket.timeout:
            print("ERROR: Timeout waiting for ACK", file=sys.stderr)
        return False
    def establish_connection(self):
        # Correctly initiates the three-way handshake by sending a SYN packet
        self.send_packet(SYN)
        try:
            while True:  # Waiting for SYN|ACK
                data, _ = self.sock.recvfrom(MTU)
                seq_num, ack_num, conn_id, flags = unpack_header(data)
                if flags & SYN and flags & ACK:  # SYN|ACK received
                    self.conn_id = conn_id
                    self.ack_num = seq_num + 1
                    self.send_packet(ACK)  # Completing handshake
                    break
        except socket.timeout:
            print("ERROR: Connection timeout during handshake", file=sys.stderr)
            sys.exit(1)

    def transfer_file(self):
        with open(self.filename, 'rb') as f:
            chunk = f.read(PAYLOAD_SIZE)
            while chunk:
                if not self.send_packet_with_retransmission(ACK, chunk):
                    print("ERROR: File transmission failed", file=sys.stderr)
                    return  # Exit on failure to retransmit
                chunk = f.read(PAYLOAD_SIZE)
        # After file is fully sent, send FIN packet
        self.send_packet(FIN)

    def terminate_connection(self):
        # Waits for 2 seconds for any incoming FIN packets, responding with ACK
        self.sock.settimeout(FIN_WAIT_TIME)
        end_time = time.time() + FIN_WAIT_TIME
        while time.time() < end_time:
            try:
                data, _ = self.sock.recvfrom(MTU)
                _, _, conn_id, flags = unpack_header(data)
                if flags & FIN and conn_id == self.conn_id:  # Respond to FIN
                    self.send_packet(ACK)
                    break  # Exit after responding to the first FIN
            except socket.timeout:
                break  # No more FIN packets received within the wait period
        self.sock.close()  # Closing the socket after the FIN-WAIT period

    def run(self):
        self.establish_connection()
        self.transfer_file()
        self.terminate_connection()

if __name__ == "__main__":
    if len(sys.argv) != 4:
        print("Usage: python3 client.py <HOSTNAME-OR-IP> <PORT> <FILENAME>", file=sys.stderr)
        sys.exit(1)
    client = ConfundoClient(sys.argv[1], int(sys.argv[2]), sys.argv[3])
    client.run()

    
