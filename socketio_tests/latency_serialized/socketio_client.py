import socketio
import time
import json
import msgpack

import const

# Define constants
IP = const.IP
PORT = const.PORT

sio = socketio.Client()

# Global variable to keep track of the stats
latency = 0 
message_counter = 0

@sio.event
def connect():
    print('Connected to server')
    print("Starting timer and counter...")
    global start_time, message_counter
    latency = 0
    message_counter = 0  # Reset message counter

@sio.event
def disconnect():
    print('Disconnected from server')
    global latency, message_counter

    # Calculate avg latency per message
    latency_per_message = latency / message_counter
    print(f"Avg latency per message: {latency_per_message}")  

@sio.on('data')
def on_data(data):
    # Deserialize the decompressed data from MessagePack format
    unpacked_data = msgpack.unpackb(data, raw=False)

    # Extract the timestamp field from the data
    global message_counter, latency 
    timestamp = unpacked_data.get("timestamp")
    latency += time.time() - timestamp
    message_counter += 1    

if __name__ == '__main__':
    sio.connect(f"http://{IP}:{PORT}", transports=['websocket'])

    # Keep the client running indefinitely
    sio.wait()

