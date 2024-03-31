import socket
import struct
import time
import random

# Constants for packet flags
SYN = 0x01
ACK = 0x02
FIN = 0x04

# Packet format: | SEQ_NUM (4 bytes) | ACK_NUM (4 bytes) | FLAGS (1 byte) | DATA |
PACKET_FORMAT = "!IIB"
HEADER_SIZE = 9  # 4 bytes for SEQ, 4 for ACK, 1 for flags
MTU = 424
PAYLOAD_SIZE = MTU - HEADER_SIZE
SEQ_NUM_MAX = 50000

class Socket:
    def __init__(self):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)  # Use UDP
        self.seq_num = random.randint(1, 1000)  # Initial sequence number
        self.ack_num = 0  # Acknowledgment number
        self.remote_addr = None
        self.cwnd = PAYLOAD_SIZE  # Initial congestion window size
        self.ss_thresh = 12000  # Initial slow start threshold

    def settimeout(self, timeout):
        self.sock.settimeout(timeout)

    def connect(self, address):
        self.remote_addr = address
        # Send SYN packet
        self._send_control_packet(SYN)
        # Receive SYN-ACK
        self._recv_control_packet()
        # Complete handshake by sending ACK
        self._send_control_packet(ACK)

    def send(self, data):
        # Segment data and send in accordance with CWND
        start = 0
        while start < len(data):
            end = min(start + self.cwnd, len(data))
            segment = data[start:end]
            self._send_data_packet(segment)
            start += len(segment)
            if start < len(data):
                # Simulate congestion control: slow start
                self.cwnd = min(self.cwnd * 2, self.ss_thresh)

    def close(self):
        # Send FIN packet
        self._send_control_packet(FIN)
        self.sock.close()

    def _send_control_packet(self, flags):
        packet = struct.pack(PACKET_FORMAT, self.seq_num, 0, flags)
        self.sock.sendto(packet, self.remote_addr)
        if flags != ACK:  # Increment SEQ_NUM for SYN and FIN packets
            self.seq_num = (self.seq_num + 1) % SEQ_NUM_MAX

    def _send_data_packet(self, data):
        flags = 0  # No control flags for data packets
        packet = struct.pack(PACKET_FORMAT, self.seq_num, 0, flags) + data
        self.sock.sendto(packet, self.remote_addr)
        # For simplicity, not implementing ACK handling and retransmissions for data packets here

    def _recv_control_packet(self):
        while True:
            packet, addr = self.sock.recvfrom(MTU)
            seq_num, ack_num, flags = struct.unpack(PACKET_FORMAT, packet[:HEADER_SIZE])
            # Handle received packet based on flags (for simplicity, assuming packets arrive in order)
            if flags & SYN and flags & ACK:  # SYN-ACK received
                self.seq_num = ack_num  # Set SEQ_NUM to received ACK_NUM for handshake completion
                return
            elif flags & FIN:  # Connection termination request
                self._send_control_packet(ACK)  # Send ACK for FIN
                return

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()


