import socket
import time
import sys

# Check if correct number of arguments are passed
if len(sys.argv) != 3:
    print("Usage: python client.py <message_size> <total_size_option>")
    sys.exit(1)

# Read arguments: message size and total data size option
message_size = int(sys.argv[1])  # Message size in bytes
total_size_option = int(sys.argv[2])  # 1 for 1GB, 2 for 500MB

# Determine the total size based on the option
if total_size_option == 1:
    total_size = 1 * 1024 * 1024 * 1024  # 1GB
elif total_size_option == 2:
    total_size = 500 * 1024 * 1024  # 500MB
else:
    print("Invalid total size option. Use 1 for 1GB or 2 for 500MB.")
    sys.exit(1)

# Create a socket object
client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# Define the server address and port
host = '127.0.0.1'
port = 65432

# Connect to the server
client_socket.connect((host, port))

# Prepare the message of the specified size
message = b'A' * message_size  # Message with the specified size in bytes

# Calculate how many messages to send to reach the total size
num_messages = total_size // message_size  # Number of messages to send

# Start measuring time for statistics
start_time = time.time()
for _ in range(num_messages):
    client_socket.sendall(message)

end_time = time.time()
elapsed_time = end_time - start_time

# Print statistics
print(f"Client sent {num_messages} messages\n "
      f"{total_size} bytes in total\n "
      f"took {elapsed_time:.2f} seconds\n")


# Close the connection
client_socket.close()
