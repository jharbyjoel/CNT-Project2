import socket
import struct
import time

# Constants
MAX_UDP_SIZE = 424
MTU_SIZE = 412
MAX_SEQ_NUM = 50000
INIT_CWND = 412
INIT_SS_THRESH = 12000
INIT_SEQ_NUM = 50000

# Flags
ACK = 0b100
SYN = 0b010
FIN = 0b001

class Socket:
    def __init__(self):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.seq_num = INIT_SEQ_NUM
        self.ack_num = 0
        self.conn_id = 0
        self.cwnd = INIT_CWND
        self.ss_thresh = INIT_SS_THRESH

    def settimeout(self, timeout):
        self.sock.settimeout(timeout)

    def bind(self, address):
        self.sock.bind(address)

    def listen(self, backlog):
        pass

    def accept(self):
        pass

    def connect(self, address):
        self.send(b'', flags=SYN)

    def send(self, data, flags=0):
        packet = self._build_packet(data, flags)
        self.sock.send(packet)

    def recv(self, bufsize):
        return self.sock.recv(bufsize)

    def close(self):
        self.sock.close()

    def _build_packet(self, data, flags):
        header = struct.pack('!IIHBB', self.seq_num, self.ack_num, self.conn_id, 0, flags)
        return header + data



