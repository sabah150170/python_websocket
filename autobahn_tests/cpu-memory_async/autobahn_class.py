import asyncio
import psutil
import json
from autobahn.asyncio.websocket import WebSocketServerProtocol, WebSocketServerFactory

import const

# Define constants
IP = const.IP
PORT = const.PORT
DATA = const.DATA

class MyServerProtocol(WebSocketServerProtocol):
    def onConnect(self, request):
        print(f"Client connecting: {request.peer}")

    def onOpen(self):
        print("WebSocket connection open.")

        # Add the new client to the list of connected clients
        self.factory.clients.add(self)

    def onClose(self, wasClean, code, reason):
        print(f"WebSocket connection closed: {reason}")

        # Remove the client from the list of connected clients
        self.factory.clients.remove(self)

class MyServerFactory(WebSocketServerFactory):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.clients = set()

    async def send_data(self, data, client):
        # Send data to all connected clients
        client.sendMessage(data)

# Function to read data from JSON file and send to clients
async def send_data_to_clients(factory):
    while True:
        with open('../stock_data.json', 'r') as file:
            data = json.load(file)
        filtered_data = [stock_data for stock_data in data if stock_data["Ticker"] in DATA]
        message = json.dumps(filtered_data).encode()

        # Send message to all connected clients asynchronously
        send_tasks = [asyncio.ensure_future(factory.send_data(message, client)) for client in factory.clients]
        await asyncio.gather(*send_tasks)

        # Yield control to the event loop to allow other tasks to run
        await asyncio.sleep(0)

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


if __name__ == '__main__':
    factory = MyServerFactory(f"ws://{IP}:{PORT}")
    factory.protocol = MyServerProtocol

    loop = asyncio.get_event_loop()
    coro = loop.create_server(factory, IP, PORT)
    server = loop.run_until_complete(coro)

    # Start sending data to clients
    asyncio.ensure_future(send_data_to_clients(factory))

    asyncio.ensure_future(monitor_usage(factory))  # Start monitoring

    try:
        loop.run_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.close()
        loop.run_until_complete(server.wait_closed())
        loop.close()

