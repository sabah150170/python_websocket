import asyncio
import time
import msgpack
from autobahn.asyncio.websocket import WebSocketClientProtocol, WebSocketClientFactory

import const

# Define constants
IP = const.IP
PORT = const.PORT

class MyClientProtocol(WebSocketClientProtocol):
    def onConnect(self, response):
        print(f"Server connected: {response.peer}")

    def onOpen(self):
        print("WebSocket connection open")
        print("Starting timer and counter...")
        self.start_time = time.time()
        self.message_counter = 0  # Reset message counter

    def onClose(self, wasClean, code, reason):
        print(f"WebSocket connection closed: {reason}")

        # Calculate loop iterations per second
        elapsed_time = time.time() - self.start_time
        iterations_per_second = self.message_counter / elapsed_time
        print(f"Loop iterations per second: {iterations_per_second}")     

    def onMessage(self, payload, isBinary):
        if isBinary:
            # Deserialize the decompressed data from MessagePack format
            data = msgpack.unpackb(payload, raw=False)
            
            self.message_counter += 1

if __name__ == "__main__":
    factory = WebSocketClientFactory(f"ws://{IP}:{PORT}")
    factory.protocol = MyClientProtocol

    loop = asyncio.get_event_loop()
    coro = loop.create_connection(factory, IP, PORT)
    _, protocol = loop.run_until_complete(coro)

    try:
        loop.run_forever()
    except KeyboardInterrupt:
        pass
    finally:
        loop.close()
