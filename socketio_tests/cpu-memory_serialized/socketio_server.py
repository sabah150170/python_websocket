import socketio
import asyncio
import uvicorn
import psutil
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
        asyncio.create_task(monitor_usage())  # Start monitoring

    connected_clients += 1

@sio.event
def disconnect(sid):
    print('Client disconnected:', sid)

async def send_messages():
    while True:
        with open('../stock_data.json', 'r') as file:
            data = json.load(file)
        filtered_data = [stock_data for stock_data in data if stock_data["Ticker"] in DATA]

        # Serialize data to MessagePack binary format
        msgpack_data = msgpack.packb(filtered_data, use_bin_type=True)
        
        await sio.emit('data', msgpack_data)  # Emitting data event to all connected clients

async def monitor_usage():
    # Get the current process
    current_process = psutil.Process()

    while True:
        # Get CPU usage of the current process
        cpu_percent = current_process.cpu_percent()
        
        # Get memory usage of the current process
        memory_percent = current_process.memory_percent()

        print(f"CPU Usage: {cpu_percent}%")
        print(f"Memory Usage: {memory_percent}%")

        await sio.emit('monitor', "")  # Emitting data event to all connected clients

        await asyncio.sleep(10)  # Adjust interval as needed

if __name__ == '__main__':
    uvicorn.run(app, host=IP, port=int(PORT))
        
