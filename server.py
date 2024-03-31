import sys
import socket
import struct

from confundo.util import parse_packet, create_packet
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

class ConfundoServer:
    def __init__(self, port):
        self.port = port
        self.seq_num = INITIAL_SEQ_NUM
        self.conn_id = 0
        self.cwnd = INITIAL_CWND
        self.ss_thresh = INITIAL_SS_THRESH
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.bind(('localhost', port))
        self.sock.settimeout(TIMEOUT_INTERVAL)
        self.cc = CwndControl()

    def send_packet(self, seq_num, ack_num, conn_id, flags, data=b''):
        header = struct.pack('!IIHHH', seq_num, ack_num, conn_id, 0, flags)
        packet = header + data
        self.sock.sendto(packet, client_address)

    def receive_packet(self):
        packet, client_address = self.sock.recvfrom(MAX_PACKET_SIZE)
        header = packet[:12]
        data = packet[12:]
        seq_num, ack_num, conn_id, _, flags = struct.unpack('!IIHHH', header)
        return seq_num, ack_num, conn_id, flags, data, client_address

    def three_way_handshake(self):
        seq_num, ack_num, conn_id, flags, _, client_address = self.receive_packet()
        if flags & 0b010 != 0b010:
            print("Error: Invalid SYN packet received")
            sys.exit(1)
        self.conn_id = conn_id
        self.seq_num += 1  # Increment sequence number for next packet
        self.send_packet(self.seq_num, seq_num + 1, conn_id, 0b011)  # SYN-ACK packet
        seq_num, ack_num, conn_id, flags, _, _ = self.receive_packet()
        if flags & 0b001 != 0b001:
            print("Error: Invalid ACK packet received")
            sys.exit(1)

    def receive_file(self):
        with open("received_file.txt", "wb") as file:
            while True:
                seq_num, ack_num, conn_id, flags, data, client_address = self.receive_packet()
                if flags & 0b100 == 0b100:  # FIN packet
                    break
                if conn_id != self.conn_id:
                    print("Error: Invalid connection ID")
                    sys.exit(1)
                file.write(data)
                self.seq_num += len(data)
                self.send_packet(self.seq_num, 0, conn_id, 0b001)  # ACK packet

    def run(self):
        try:
            self.three_way_handshake()
            self.receive_file()
        except Exception as e:
            print("Error:", str(e))
            sys.exit(1)

if __name__ == "__main__":
    if len(sys.argv) != 2:
        sys.stderr.write("ERROR: Invalid number of arguments\n")
        sys.exit(1)

    port = int(sys.argv[1])

    server = ConfundoServer(port)
    server.run()
