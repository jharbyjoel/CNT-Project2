import socket
import random
import struct
import confundo

MAX_PACKET_SIZE = 424

def start():
    # Create a socket
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    # Bind the socket to a specific port
    server_address = ('', 54000)  # Empty string for localhost
    server_socket.bind(server_address)

    print('Server is listening on port 54000...')

    while True:
        # Receive data from the client
        data, client_address = server_socket.recvfrom(MAX_PACKET_SIZE)
        print('Received data from:', client_address)

        try:
            # Parse the received data
            seq_num, ack_num, conn_id, flags, payload = parse_packet(data)
            print('Received packet:', seq_num, ack_num, conn_id, flags)

            # Handle different types of packets
            if flags & confundo.SYN:  # SYN packet
                handle_syn(server_socket, client_address, seq_num, conn_id)
            elif flags & confundo.FIN:  # FIN packet
                handle_fin(server_socket, client_address, seq_num, conn_id)
            elif flags & confundo.ACK:  # ACK packet
                handle_ack(server_socket, client_address, ack_num, conn_id)
            elif payload:  # Data packet
                handle_data(server_socket, client_address, seq_num, ack_num, conn_id, payload)
        except Exception as e:
            print('Error:', e)

def parse_packet(data):
    header = data[:12]
    payload = data[12:]
    seq_num, ack_num, conn_id, _, flags = struct.unpack('!IIHHH', header)
    return seq_num, ack_num, conn_id, flags, payload

def send_packet(server_socket, client_address, seq_num, ack_num, conn_id, flags, payload=b''):
    header = struct.pack('!IIHHH', seq_num, ack_num, conn_id, 0, flags)
    packet = header + payload
    server_socket.sendto(packet, client_address)

def handle_syn(server_socket, client_address, seq_num, conn_id):
    # Generate a random connection ID for the client
    conn_id = generate_connection_id()

    # Send a SYN-ACK packet back to the client
    ack_num = seq_num + 1  # Expected sequence number from the client
    flags = confundo.SYN | confundo.ACK
    send_packet(server_socket, client_address, seq_num, ack_num, conn_id, flags)

    # Wait for an ACK packet from the client to confirm connection establishment

def handle_ack(server_socket, client_address, ack_num, conn_id):
    # Confirm connection establishment and start data transfer
    print("Connection established with client:", client_address)

def handle_fin(server_socket, client_address, seq_num, conn_id):
    # Send an ACK packet back to the client
    ack_num = seq_num + 1
    flags = confundo.ACK
    send_packet(server_socket, client_address, seq_num, ack_num, conn_id, flags)

    # Close the connection gracefully
    server_socket.close()
    print("Connection closed with client:", client_address)

def handle_data(server_socket, client_address, seq_num, ack_num, conn_id, payload):
    # Process the received data (for example, print it)
    print("Received data:", payload.decode())

    # Send an ACK packet back to the client
    flags = confundo.ACK
    send_packet(server_socket, client_address, seq_num, ack_num, conn_id, flags)

def generate_connection_id():
    return random.randint(1, 65535)

if __name__ == '__main__':
    start()

