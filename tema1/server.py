import argparse
import asyncio
from aioquic.asyncio import QuicConnectionProtocol, serve
from aioquic.quic.configuration import QuicConfiguration
from aioquic.quic.events import StreamDataReceived, ConnectionTerminated
import time

# Global mode variable
mode = 'streaming'  # Default mode

class QUICServerProtocol(QuicConnectionProtocol):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.stream_data = {}
        self.start_time = time.time()
        self.total_messages = 0
        self.total_bytes = 0
        self.ack_sent = {}

    def quic_event_received(self, event):
        if mode == 'ack':
            if isinstance(event, StreamDataReceived):
                self.total_bytes += len(event.data)
                stream_id = event.stream_id

                # Track each stream separately
                if stream_id not in self.stream_data:
                    self.stream_data[stream_id] = {"complete": False, "size": 0}

                # Add current chunk size to total for this stream
                self.stream_data[stream_id]["size"] += len(event.data)

                # Mark stream as complete when end_stream flag is set
                if event.end_stream:
                    self.stream_data[stream_id]["complete"] = True
                    self.total_messages += 1

                    # Only send ACK for complete streams
                    if mode == 'ack' and stream_id not in self.ack_sent:
                        ack = b"ACK"
                        self._quic.send_stream_data(stream_id, ack, end_stream=True)
                        self.ack_sent[stream_id] = True

                    # Log the complete message
                    # print(f"Complete message received on stream {stream_id}, "
                    #       f"size: {self.stream_data[stream_id]['size']} bytes")

            elif isinstance(event, ConnectionTerminated):
                end_time = time.time()
                total_time = end_time - self.start_time
                print(f"Protocol used: QUIC, Server: Total messages: {self.total_messages}, Total bytes: {self.total_bytes}")
        else:
            if isinstance(event, StreamDataReceived):
                self.total_bytes += len(event.data)
                print(len(event.data))
                stream_id = event.stream_id
                self.total_messages += 1
            elif isinstance(event, ConnectionTerminated):
                end_time = time.time()
                total_time = end_time - self.start_time
                print(f"Protocol used: QUIC, Server: Total messages: {self.total_messages}, Total bytes: {self.total_bytes}")


async def run_server():
    global mode  # Access the global mode variable

    configuration = QuicConfiguration(is_client=False)
    configuration.load_cert_chain("cert.pem", "key.pem")
    configuration.max_data = 10 * 1024 * 1024  # 10 MB
    configuration.max_stream_data = 5 * 1024 * 1024  # 5 MB
    configuration.max_stream_receive_window = 2 * 1024 * 1024  # 2 MB
    configuration.max_receive_udp_payload_size = 65536  # Maximum UDP payload size

    server = await serve(
        host="localhost",
        port=4433,
        configuration=configuration,
        create_protocol=QUICServerProtocol,
    )

    print(f"QUIC server is running on localhost:4433 in {mode} mode")
    await asyncio.Event().wait()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="QUIC client that sends data in chunks.")
    parser.add_argument("mode", choices=["streaming", "ack"], help="Mode of operation.")
    args = parser.parse_args()

    mode = args.mode  # Set mode to 'ack' for this run
    asyncio.run(run_server())
