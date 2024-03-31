import sys
import socket
import struct
import os
import time

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
    def __init__(self, hostname, port, filename):
        self.hostname = hostname
        self.port = port
        self.filename = filename
        self.seq_num = INITIAL_SEQ_NUM
        self.conn_id = 0  # Will be updated during handshake
        self.cwnd = INITIAL_CWND
        self.ss_thresh = INITIAL_SS_THRESH
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.settimeout(TIMEOUT_INTERVAL)
        self.last_ack_time = time.time()

    def send_packet(self, seq_num, ack_num, conn_id, flags, data=b''):
        header = struct.pack('!IIHHH', seq_num, ack_num, conn_id, 0, flags)
        packet = header + data
        self.sock.sendto(packet, (self.hostname, self.port))

    def receive_packet(self):
        packet, _ = self.sock.recvfrom(MAX_PACKET_SIZE)
        header = packet[:12]
        data = packet[12:]
        seq_num, ack_num, conn_id, _, flags = struct.unpack('!IIHHH', header)
        return seq_num, ack_num, conn_id, flags, data

    def three_way_handshake(self):
        self.send_packet(self.seq_num, 0, 0, 0b010)  # SYN packet
        seq_num, ack_num, conn_id, flags, _ = self.receive_packet()
        if flags & 0b011 != 0b011:
            print("Error: Invalid SYN-ACK packet received")
            sys.exit(1)
        self.conn_id = conn_id
        self.seq_num += 1  # Increment sequence number for next packet
        self.send_packet(self.seq_num, seq_num + 1, conn_id, 0b001)  # ACK packet

    def transfer_file(self):
        with open(self.filename, "rb") as file:
            while True:
                data = file.read(MTU_SIZE)
                if not data:
                    break
                self.send_packet(self.seq_num, 0, self.conn_id, 0b001, data)
                self.seq_num += len(data)
                while True:
                    try:
                        seq_num, ack_num, conn_id, flags, _ = self.receive_packet()
                        if conn_id != self.conn_id:
                            print("Error: Invalid connection ID")
                            sys.exit(1)
                        if ack_num == self.seq_num:
                            break
                    except socket.timeout:
                        print("Timeout: Resending last packet")
                        self.send_packet(self.seq_num, 0, self.conn_id, 0b001, data)
                self.cwnd += len(data)
                if self.cwnd >= self.ss_thresh:
                    self.cwnd += (412 * 412) // self.cwnd

    def close_connection(self):
        self.send_packet(self.seq_num, 0, self.conn_id, 0b100)  # FIN packet
        self.seq_num += 1
        start_time = time.time()
        while time.time() - start_time < FIN_WAIT_TIME:
            try:
                seq_num, ack_num, conn_id, flags, _ = self.receive_packet()
                if flags & 0b001 == 0b001:  # ACK packet
                    break
                elif flags & 0b100 == 0b100:  # FIN packet
                    self.send_packet(self.seq_num, ack_num + 1, self.conn_id, 0b001)  # ACK packet
            except socket.timeout:
                pass
        self.sock.close()

    def run(self):
        try:
            self.three_way_handshake()
            self.transfer_file()
            self.close_connection()
        except Exception as e:
            print("Error:", str(e))
            sys.exit(1)

if __name__ == "__main__":
    if len(sys.argv) != 4:
        sys.stderr.write("ERROR: Invalid number of arguments\n")
        sys.exit(1)

    hostname = sys.argv[1]
    port = int(sys.argv[2])
    filename = sys.argv[3]

    client = ConfundoClient(hostname, port, filename)
    client.run()


