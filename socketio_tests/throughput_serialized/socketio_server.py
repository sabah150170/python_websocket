import socketio
import asyncio
import uvicorn
import time
import json
import msgpack

import const

# Define constants
IP = const.IP
PORT = const.PORT
CLIENT_NUMBER = const.CLIENT_NUMBER
DATA = const.DATA

sio = socketio.AsyncServer(async_mode='asgi', transports=['websocket'])
app = socketio.ASGIApp(sio)

# Global variable to keep track of the number of connected clients
connected_clients = 0
start_time = 0 
response_counter = 0

@sio.event
def connect(sid, environ):
    print('Client connected:', sid)

    global connected_clients, start_time, response_counter
    if connected_clients == 0:
        # Start sending messages if all clients are connected
        asyncio.create_task(send_messages())

    connected_clients += 1
    # Check if ... clients are connected
    if connected_clients == CLIENT_NUMBER:
        print("Starting timer and counter...")
        start_time = time.time()
        response_counter = 0  # Reset response counter

@sio.event
def disconnect(sid):
    print('Client disconnected:', sid)

    # Calculate response counts per second
    elapsed_time = time.time() - start_time
    responses_per_second = response_counter / elapsed_time
    print(f"Responses per second: {responses_per_second}")

async def send_messages():
    while True:
        with open('../stock_data.json', 'r') as file:
            data = json.load(file)
        filtered_data = [stock_data for stock_data in data if stock_data["Ticker"] in DATA]

        # Serialize data to MessagePack binary format
        msgpack_data = msgpack.packb(filtered_data, use_bin_type=True)
        
        await sio.emit('data', msgpack_data)  # Emitting data event to all connected clients

        global response_counter
        response_counter += 1  # Increment response counter

if __name__ == '__main__':
    uvicorn.run(app, host=IP, port=int(PORT))
        