import socket
import time
import sys
message_size = int(sys.argv[1])  # Message size in bytes

# Create a socket object
server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# Define the host and port
host = '127.0.0.1'
port = 65432

# Bind the socket to the host and port
server_socket.bind((host, port))

# Enable the server to accept connections (max 5 clients in the waiting queue)
server_socket.listen(5)

print(f"Server listening on {host}:{port}...")

client_socket, client_address = server_socket.accept()
print(f"Connection established with {client_address}")

# Start measuring time for statistics
start_time = time.time()
total_messages = 0
total_bytes = 0

while True:
    # Receive data from the client (each message is 704 bytes)
    data = client_socket.recv(message_size)
    if not data:
        break  # No more data means client is done

    total_messages += 1
    total_bytes += len(data)

end_time = time.time()
elapsed_time = end_time - start_time

print(f"Protocol used: TCP\n"
    f"Server received {total_messages} messages\n "
      f"{total_bytes} bytes in total\n "
     )


# Close the client connection
client_socket.close()
