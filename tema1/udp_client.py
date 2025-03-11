import socket
import time
import sys

# Check if correct number of arguments are passed
if len(sys.argv) != 4:
    print("Usage: python client_udp.py <message_size> <total_size_option> <mode>")
    sys.exit(1)

# Read arguments: message size, total data size option, and mode
message_size = int(sys.argv[1])  # Message size in bytes
total_size_option = int(sys.argv[2])  # 1 for 1GB, 2 for 500MB
mode = sys.argv[3]  # "streaming" or "ack"

# Determine the total size based on the option
if total_size_option == 1:
    total_size = 1 * 1024 * 1024 * 1024  # 1GB
elif total_size_option == 2:
    total_size = 500 * 1024 * 1024  # 500MB
else:
    print("Invalid total size option. Use 1 for 1GB or 2 for 500MB.")
    sys.exit(1)

# Create a UDP socket
client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

# Define the server address and port
host = '127.0.0.1'
port = 65432

# Prepare the message of the specified size
message = b'A' * message_size  # Message with the specified size in bytes

# Calculate how many messages to send to reach the total size
num_messages = total_size // message_size  # Number of messages to send

# Start measuring time for statistics
start_time = time.time()

# Send messages
if mode == "streaming":
    for _ in range(num_messages):
        client_socket.sendto(message, (host, port))

    # Send the "end" message to indicate completion
    client_socket.sendto(b"END", (host, port))

elif mode == "ack":
    for _ in range(num_messages):
        client_socket.sendto(message, (host, port))

        # Wait for acknowledgment from the server
        data, _ = client_socket.recvfrom(3)  # Receive the "ACK" response
        if data != b"ACK":
            print("Error: Did not receive ACK.")
            break

    # Send the "end" message to indicate completion
    client_socket.sendto(b"END", (host, port))

else:
    print("Invalid mode. Use 'streaming' or 'ack'.")
    sys.exit(1)

end_time = time.time()
elapsed_time = end_time - start_time

# Print statistics
print(f"Client sent {num_messages} messages\n "
      f"{total_size} bytes in total\n "
      f"took {elapsed_time:.2f} seconds")

# Close the connection
client_socket.close()
