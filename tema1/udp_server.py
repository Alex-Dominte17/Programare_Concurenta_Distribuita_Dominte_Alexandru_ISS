import socket
import sys
import time

# Fixed message size for the server (e.g., 704 bytes)

if len(sys.argv) != 3:
    print("Usage: python udp_server.py <message_size> <mode>")
    sys.exit(1)


message_size = int(sys.argv[1])  # Message size in bytes
mode = sys.argv[2]  # "streaming" or "ack"


# Define the host and port
host = '127.0.0.1'
port = 65432

# Create a UDP socket
server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

# Bind the socket to the host and port
server_socket.bind((host, port))

print(f"Server listening on {host}:{port}...")

# Function for handling Streaming Mode
def handle_streaming():
    start_time = time.time()
    total_messages = 0
    total_bytes = 0

    while True:
        # Receive data from the client
        data, client_address = server_socket.recvfrom(message_size)

        if data == b"END":
            print("Server received end message. Stopping.")
            break

        total_messages += 1
        total_bytes += len(data)

    end_time = time.time()
    elapsed_time = end_time - start_time

    print(f"Protocol used: UDP\n"
          f"Server received {total_messages} messages\n "
          f"{total_bytes} bytes in total ")

# Function for handling Ack Mode
def handle_ack():
    start_time = time.time()
    total_messages = 0
    total_bytes = 0

    while True:
        # Receive data from the client
        data, client_address = server_socket.recvfrom(message_size)

        if data == b"END":
            print("Server received end message. Stopping.")
            break

        # Acknowledge the message
        server_socket.sendto(b"ACK", client_address)

        total_messages += 1
        total_bytes += len(data)

    end_time = time.time()
    elapsed_time = end_time - start_time

    print(f"Protocol used: UDP\n" 
          f"Server received {total_messages} messages\n "
          f"{total_bytes} bytes in total ")

# To choose which mode to run, uncomment one of the lines below:
if mode =="streaming":
    handle_streaming()
else:
    handle_ack()

server_socket.close()
