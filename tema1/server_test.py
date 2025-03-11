class QuicServerProtocol(QuicConnectionProtocol):
    def __init__(self, *args, mode='st', **kwargs):
        super().__init__(*args, **kwargs)
        self.total_bytes = 0
        self.total_messages = 0
        self.mode = mode
        self.ack_sent = {}

    def quic_event_received(self, event):
        if isinstance(event, StreamDataReceived):
            stream_id = event.stream_id
            self.total_bytes += len(event.data)
            self.total_messages += 1

            if self.mode == 'sw':
                if event.end_stream and stream_id not in self.ack_sent:
                    ack = b"ACK"
                    self._quic.send_stream_data(stream_id, ack, end_stream=True)
                    self.ack_sent[stream_id] = True

        elif isinstance(event, ConnectionTerminated):
            print("Protocol used: QUIC")
            print(f"Mode used: {'Stop and Wait' if self.mode == 'sw' else 'Streaming'}")
            print("Total messages received:", self.total_messages)
            print("Total bytes received:", self.total_bytes)
            sys.exit(0)