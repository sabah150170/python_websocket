import asyncio
import psutil
import json
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
        if not isBinary:
            data = json.loads(payload.decode('utf-8'))
    
    async def monitor_usage(self):
        # Get the current process
        current_process = psutil.Process()

        while True:
            # Get CPU usage of the current process
            cpu_percent = current_process.cpu_percent()

            # Get memory usage of the current process
            memory_percent = current_process.memory_percent()

            print(f"CPU Usage: {cpu_percent}%")
            print(f"Memory Usage: {memory_percent}%")

            await asyncio.sleep(60)  # Adjust interval as needed

if __name__ == "__main__":
    factory = WebSocketClientFactory(f"ws://{IP}:{PORT}")
    factory.protocol = MyClientProtocol

    loop = asyncio.get_event_loop()
    coro = loop.create_connection(factory, IP, PORT)
    _, protocol = loop.run_until_complete(coro)

    try:
        asyncio.ensure_future(protocol.monitor_usage())
        loop.run_forever()
    except KeyboardInterrupt:
        pass
    finally:
        loop.close()

