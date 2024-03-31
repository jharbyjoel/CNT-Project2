import socket
import struct
import time
import random

# Constants
SYN = 0x01
ACK = 0x02
FIN = 0x04
HEADER_FORMAT = "!IIB"
HEADER_SIZE = 9
MTU = 424
PAYLOAD_SIZE = MTU - HEADER_SIZE
SEQ_NUM_MAX = 50000
INITIAL_CWND = PAYLOAD_SIZE
SS_THRESH = 12000  # Slow start threshold

class Socket:
    def __init__(self):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.remote_addr = None
        self.seq_num = random.randint(0, SEQ_NUM_MAX)
        self.ack_num = 0
        self.cwnd = INITIAL_CWND
        self.ssthresh = SS_THRESH
        self.send_base = 0
        self.timeout = 1.0  # Initial retransmission timeout value
        self.unacknowledged_packets = {}

    def settimeout(self, timeout):
        self.sock.settimeout(timeout)

    def connect(self, address):
        # Connection establishment logic remains unchanged
        pass

    def _packetize(self, data):
        # Split data into segments according to CWND and create packets
        segments = [data[i:i+PAYLOAD_SIZE] for i in range(0, len(data), PAYLOAD_SIZE)]
        packets = []
        for segment in segments:
            packet = struct.pack(HEADER_FORMAT, self.seq_num, 0, ACK) + segment
            packets.append(packet)
            self.seq_num = (self.seq_num + len(segment)) % SEQ_NUM_MAX
        return packets

    def send(self, data):
        packets = self._packetize(data)
        for packet in packets:
            self._send_and_wait_ack(packet)

    def _send_and_wait_ack(self, packet):
        while True:
            self.sock.sendto(packet, self.remote_addr)
            self.unacknowledged_packets[self.seq_num] = (packet, time.time())
            try:
                while True:
                    received_packet, _ = self.sock.recvfrom(MTU)
                    ack_num = struct.unpack(HEADER_FORMAT, received_packet[:HEADER_SIZE])[1]
                    if ack_num in self.unacknowledged_packets:
                        del self.unacknowledged_packets[ack_num]
                        # Adjust CWND according to congestion control algorithm
                        if self.cwnd < self.ssthresh:
                            self.cwnd += PAYLOAD_SIZE  # Slow start phase
                        else:
                            self.cwnd += int(PAYLOAD_SIZE**2 / self.cwnd)  # Congestion avoidance
                        return  # Move to the next packet
            except socket.timeout:
                # Retransmission due to timeout
                self.ssthresh = max(self.cwnd // 2, 1 * PAYLOAD_SIZE)  # Update ssthresh
                self.cwnd = INITIAL_CWND  # Reset CWND to initial size
                # Resend all unacknowledged packets
                for seq, (pkt, _) in self.unacknowledged_packets.items():
                    self.sock.sendto(pkt, self.remote_addr)

    def close(self):
        # Connection termination logic remains unchanged
        pass

    # Additional methods (__enter__, __exit__, etc.) remain unchanged


