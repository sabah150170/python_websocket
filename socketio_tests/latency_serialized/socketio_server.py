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
DATA = const.DATA

sio = socketio.AsyncServer(async_mode='asgi', transports=['websocket'])
app = socketio.ASGIApp(sio)

# Global variable to keep track of the number of connected clients
connected_clients = 0

@sio.event
def connect(sid, environ):
    print('Client connected:', sid)

    global connected_clients, start_time, response_counter
    if connected_clients == 0:
        # Start sending messages if all clients are connected
        asyncio.create_task(send_messages())

    connected_clients += 1

@sio.event
def disconnect(sid):
    print('Client disconnected:', sid)

async def send_messages():
    while True:
        with open('../stock_data.json', 'r') as file:
            data = json.load(file)
        filtered_data = [stock_data for stock_data in data if stock_data["Ticker"] in DATA]

        # Add timestamp to the data
        data_with_timestamp = {"timestamp": time.time(), "data": filtered_data}

        # Serialize data to MessagePack binary format
        msgpack_data = msgpack.packb(data_with_timestamp, use_bin_type=True)
        
        await sio.emit('data', msgpack_data)  # Emitting data event to all connected clients

if __name__ == '__main__':
    uvicorn.run(app, host=IP, port=int(PORT))
        