import asyncio
import time
import json
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

    def onClose(self, wasClean, code, reason):
        print(f"WebSocket connection closed: {reason}")

    def onMessage(self, payload, isBinary):
        if isBinary:
            # Deserialize the decompressed data from MessagePack format
            data = msgpack.unpackb(payload, raw=False)

            # Extract the timestamp field from the data
            timestamp = data.get("timestamp")
            print("LATENCY:", time.time() - timestamp, "DATA:", data)
        
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
