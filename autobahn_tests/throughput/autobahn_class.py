import asyncio
import json
import time
from autobahn.asyncio.websocket import WebSocketServerProtocol, WebSocketServerFactory

import const

# Define constants
IP = const.IP
PORT = const.PORT
CLIENT_NUMBER = const.CLIENT_NUMBER
DATA = const.DATA

class MyServerProtocol(WebSocketServerProtocol):
    def onConnect(self, request):
        print(f"Client connecting: {request.peer}")

    def onOpen(self):
        print("WebSocket connection open.")

        # Add the new client to the list of connected clients
        self.factory.clients.add(self)

        # Check if ... clients are connected
        if len(self.factory.clients) == CLIENT_NUMBER:
            print("Starting timer and counter...")
            self.factory.start_time = time.time()
            self.factory.response_counter = 0  # Reset response counter

    def onClose(self, wasClean, code, reason):
        print(f"WebSocket connection closed: {reason}")

        # Remove the client from the list of connected clients
        self.factory.clients.remove(self)

class MyServerFactory(WebSocketServerFactory):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.clients = set()
        self.response_counter = 0  # Initialize response counter
        self.start_time = time.time()

    def send_data(self, data):
        # Send data to all connected clients
        for client in self.clients:
            client.sendMessage(data)
        self.response_counter += 1  # Increment response counter

# Function to read data from JSON file and send to clients
async def send_data_to_clients(factory):
    while True:
        with open('../stock_data.json', 'r') as file:
            data = json.load(file)
        filtered_data = [stock_data for stock_data in data if stock_data["Ticker"] in DATA]

        # Serialize the data to JSON and send it to all clients
        factory.send_data(json.dumps(filtered_data).encode())

        # Yield control to the event loop to allow other tasks to run
        await asyncio.sleep(0)

if __name__ == '__main__':
    factory = MyServerFactory(f"ws://{IP}:{PORT}")
    factory.protocol = MyServerProtocol

    loop = asyncio.get_event_loop()
    coro = loop.create_server(factory, IP, PORT)
    server = loop.run_until_complete(coro)

    # Start sending data to clients
    asyncio.ensure_future(send_data_to_clients(factory))

    try:
        loop.run_forever()
    except KeyboardInterrupt:
        pass
    finally:
        # Calculate response counts per second
        elapsed_time = time.time() - factory.start_time
        responses_per_second = factory.response_counter / elapsed_time
        print(f"Responses per second: {responses_per_second}")
        
        server.close()
        loop.run_until_complete(server.wait_closed())
        loop.close()

        
