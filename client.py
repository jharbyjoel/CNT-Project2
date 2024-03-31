import argparse
import sys
from confundo import Socket

def main(host, port, file_path):
    try:
        with Socket() as sock:
            sock.settimeout(10)
            print("Connecting to server...")
            sock.connect((host, port))
            
            print("Connection established. Sending file...")
            with open(file_path, "rb") as file:
                data = file.read()
                sock.send(data)
                print("File sent successfully.")
            
            print("Closing connection...")
            sock.close()
            print("Connection closed.")
    except Exception as e:
        print(f"An error occurred: {e}", file=sys.stderr)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Confundo Protocol Client")
    parser.add_argument("host", help="Hostname or IP address of the server")
    parser.add_argument("port", type=int, help="Port number of the server")
    parser.add_argument("file", help="Path to the file to send")
    args = parser.parse_args()

    main(args.host, args.port, args.file)

@import argparse
import sys
from confundo import Socket

def main(host, port, file_path):
    try:
        with Socket() as sock:
            sock.settimeout(10)
            print("Connecting to server...")
            sock.connect((host, port))
            
            print("Connection established. Sending file...")
            with open(file_path, "rb") as file:
                data = file.read()
                sock.send(data)
                print("File sent successfully.")
            
            print("Closing connection...")
            sock.close()
            print("Connection closed.")
    except Exception as e:
        print(f"An error occurred: {e}", file=sys.stderr)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Confundo Protocol Client")
    parser.add_argument("host", help="Hostname or IP address of the server")
    parser.add_argument("port", type=int, help="Port number of the server")
    parser.add_argument("file", help="Path to the file to send")
    args = parser.parse_args()

    main(args.host, args.port, args.file)


