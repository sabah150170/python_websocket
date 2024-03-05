import socketio
import time
import json
import msgpack

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

    # Extract the timestamp field from the data
    timestamp = unpacked_data.get("timestamp")
    print("LATENCY:", time.time() - timestamp, "DATA:", unpacked_data) 

if __name__ == '__main__':
    sio.connect(f"http://{IP}:{PORT}", transports=['websocket'])

    # Keep the client running indefinitely
    sio.wait()

