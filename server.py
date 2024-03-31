import argparse
from confundo import Socket

def main(host, port):
    with Socket() as sock:
        sock.settimeout(None)  # Optionally set to None for servers intended to run indefinitely
        sock.bind((host, port))
        print(f"Server listening on {host}:{port}")

        while True:
            print("Waiting for connections...")
            data, addr = sock.recv(1024)
            if data:
                print(f"Received data from {addr}")
                # Process or save data as needed
                break  # This example stops after receiving some data for simplicity

            print("Closing server socket...")
            sock.close()
            print("Server socket closed.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Confundo Protocol Server")
    parser.add_argument("--host", default="0.0.0.0", help="Host to bind the server to")
    parser.add_argument("--port", type=int, default=54000, help="Port number to bind the server to")
    args = parser.parse_args()

    main(args.host, args.port)
