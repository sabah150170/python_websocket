import socketio
import time
import json
import msgpack
import psutil 

import const

# Define constants
IP = const.IP
PORT = const.PORT

sio = socketio.Client()

@sio.event
def connect():
    print('Connected to server')   

@sio.event
def disconnect():
    print('Disconnected from server')

@sio.on('data')
def on_data(data):
    # Deserialize the decompressed data from MessagePack format
    unpacked_data = msgpack.unpackb(data, raw=False)    

@sio.on('monitor')
def on_data(data):
    # Get the current process
    current_process = psutil.Process()

    # Get memory usage of the current process
    memory_percent = current_process.memory_percent()
    print(f"Memory Usage: {memory_percent}%")

if __name__ == '__main__':
    sio.connect(f"http://{IP}:{PORT}", transports=['websocket'])

    # Keep the client running indefinitely
    sio.wait()
