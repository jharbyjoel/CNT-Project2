import sys
import socket
import struct
import os
import time

from confundo.cwnd_control import CwndControl

# Constants
MAX_PACKET_SIZE = 424
MTU_SIZE = 412
INITIAL_CWND = 412
INITIAL_SS_THRESH = 12000
INITIAL_SEQ_NUM = 50000
TIMEOUT_INTERVAL = 0.5
FIN_WAIT_TIME = 2
MAX_SEQ_NUM = 50000

class ConfundoClient:
    def __init__(self, server_ip, server_port, file_name):
        self.server_ip = server_ip
        self.server_port = server_port
        self.file_name = file_name
        self.seq_num = INITIAL_SEQ_NUM
        self.conn_id = 0
        self.cwnd = INITIAL_CWND
        self.ss_thresh = INITIAL_SS_THRESH
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.settimeout(TIMEOUT_INTERVAL)
        self.cc = CwndControl()

    def send_packet(self, seq_num, ack_num, conn_id, flags, data=b''):
        header = struct.pack('!IIHHH', seq_num, ack_num, conn_id, 0, flags)
        packet = header + data
        self.sock.sendto(packet, (self.server_ip, self.server_port))

    def receive_packet(self):
        packet, _ = self.sock.recvfrom(MAX_PACKET_SIZE)
        header = packet[:12]
        data = packet[12:]
        seq_num, ack_num, conn_id, _, flags = struct.unpack('!IIHHH', header)
        return seq_num, ack_num, conn_id, flags, data

    def three_way_handshake(self):
        self.send_packet(self.seq_num, 0, self.conn_id, 0b010)  # SYN packet
        seq_num, ack_num, conn_id, flags, _ = self.receive_packet()
        if flags & 0b011 != 0b011:
            print("Error: Invalid SYN-ACK packet received")
            sys.exit(1)
        self.conn_id = conn_id
        self.seq_num += 1  # Increment sequence number for next packet
        self.send_packet(self.seq_num, seq_num + 1, conn_id, 0b001)  # ACK packet

    def send_file(self):
        with open(self.file_name, "rb") as file:
            while True:
                data = file.read(MTU_SIZE)
                if not data:
                    break
                self.send_packet(self.seq_num, 0, self.conn_id, 0b000, data)
                self.seq_num += len(data)

    def send_fin(self):
        self.send_packet(self.seq_num, 0, self.conn_id, 0b100)  # FIN packet

    def receive_ack(self):
        seq_num, ack_num, conn_id, flags, _ = self.receive_packet()
        if flags & 0b001 != 0b001:
            print("Error: Invalid ACK packet received")
            sys.exit(1)

    def wait_for_fin(self):
        start_time = time.time()
        while time.time() - start_time < FIN_WAIT_TIME:
            seq_num, ack_num, conn_id, flags, _ = self.receive_packet()
            if flags & 0b100 == 0b100:  # FIN packet
                break
            self.send_packet(self.seq_num, 0, self.conn_id, 0b001)  # ACK packet

    def run(self):
        try:
            self.three_way_handshake()
            self.send_file()
            self.send_fin()
            self.receive_ack()
            self.wait_for_fin()
        except Exception as e:
            print("Error:", str(e))
            sys.exit(1)

if __name__ == "__main__":
    if len(sys.argv) != 4:
        sys.stderr.write("ERROR: Invalid number of arguments\n")
        sys.exit(1)

    server_ip = sys.argv[1]
    server_port = int(sys.argv[2])
    file_name = sys.argv[3]

    client = ConfundoClient(server_ip, server_port, file_name)
    client.run()
