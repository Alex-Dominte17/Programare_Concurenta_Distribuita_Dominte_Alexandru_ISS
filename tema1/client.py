import asyncio
import sys
import time
import argparse
from aioquic.asyncio import connect, QuicConnectionProtocol
from aioquic.quic.configuration import QuicConfiguration
from aioquic.quic.events import StreamDataReceived

configuration = QuicConfiguration(is_client=True)
configuration.verify_mode = False  # Disable certificate verification for local testing
configuration.max_data = 10 * 1024 * 1024  # 10 MB
configuration.max_stream_data = 5 * 1024 * 1024  # 5 MB
configuration.max_stream_receive_window = 2 * 1024 * 1024  # 2 MB
configuration.max_receive_udp_payload_size = 65536


async def stop_and_wait(chunk_size,total_size, start_time):
    async with connect("localhost", 4433, configuration=configuration,
                       create_protocol=QuicClientProtocol) as client:

        size = 1024 * 1024 * 50
        total_messages = 0
        total_bytes = 0
        while total_bytes < size:
            stream_id = client._quic.get_next_available_stream_id()
            to_send = min(chunk_size, size - total_bytes)
            ack_future = asyncio.get_running_loop().create_future()
            client.ack_futures[stream_id] = ack_future
            client._quic.send_stream_data(stream_id, bytes(to_send), True)
            client.transmit()
            # print("total bytes:", total_bytes)

            try:
                await asyncio.wait_for(ack_future, timeout=1)
            except asyncio.TimeoutError:
                print("ERROR receiving ACK")
                sys.exit(1)
            total_bytes += to_send
            total_messages += 1
    end_time = time.time()
    print(
        f"Stream closed. Total messages: {total_messages}, Total bytes: {total_bytes}, Total time: {end_time - start_time:.2f} seconds.")


async def streaming(chunk_size,total_size, start_time):
    async with connect("localhost", 4433, configuration=configuration, create_protocol=QuicClientProtocol) as protocol:
        print("Connected.")
        quic = protocol._quic
        stream_id = quic.get_next_available_stream_id()

        data_chunk = bytes(total_size)  # 1MB test data
        total_messages = 0
        total_bytes = 0

        print(f"Sending {len(data_chunk)} bytes in {chunk_size} byte chunks...")

        for i in range(0, len(data_chunk), chunk_size):
            chunk = data_chunk[i:i + chunk_size]
            end_stream = (i + chunk_size >= len(data_chunk))
            quic.send_stream_data(stream_id, chunk, end_stream=end_stream)
            protocol.transmit()
            total_messages += 1
            total_bytes += len(chunk)
            await asyncio.sleep(0)

        end_time = time.time()
        print(
            f"Client: Total messages: {total_messages}, Total bytes: {total_bytes}, Total time: {end_time - start_time:.2f} seconds.")

        await asyncio.sleep(1)


class QuicClientProtocol(QuicConnectionProtocol):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.ack_futures = {}

    def quic_event_received(self, event):
        if isinstance(event, StreamDataReceived):
            if event.data == b"ACK":
                fut = self.ack_futures.get(event.stream_id)
                if fut and not fut.done():
                    fut.set_result(True)


async def quic_client(chunk_size, total_size, mode):
    if total_size == 1:
        total_size = 1024 * 1024 * 1024
    else:
        total_size = 1024 * 1024 * 500
    print("Connecting to server...")
    start_time = time.time()
    if mode == 'ack':
        await stop_and_wait(chunk_size,total_size, start_time)
    else:
        await streaming(chunk_size,total_size, start_time)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="QUIC client that sends data in chunks.")
    parser.add_argument("chunk_size", type=int, help="Chunk size in bytes.")
    parser.add_argument("total_size", choices=[1, 2], type=int, help="Mode of operation.")

    parser.add_argument("mode", choices=["streaming", "ack"], help="Mode of operation.")
    args = parser.parse_args()

    asyncio.run(quic_client(args.chunk_size, args.total_size, args.mode))
