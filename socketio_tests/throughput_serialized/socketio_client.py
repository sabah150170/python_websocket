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
start_time = 0 
message_counter = 0

@sio.event
def connect():
    print('Connected to server')
    print("Starting timer and counter...")
    global start_time, message_counter
    start_time = time.time()
    message_counter = 0  # Reset message counter

@sio.event
def disconnect():
    print('Disconnected from server')
    global start_time, message_counter

    # Calculate loop iterations per second
    elapsed_time = time.time() - start_time
    iterations_per_second = message_counter / elapsed_time
    print(f"Loop iterations per second: {iterations_per_second}") 

@sio.on('data')
def on_data(data):
    # Deserialize the decompressed data from MessagePack format
    unpacked_data = msgpack.unpackb(data, raw=False)

    global message_counter 
    message_counter += 1


if __name__ == '__main__':
    sio.connect(f"http://{IP}:{PORT}", transports=['websocket'])

    # Keep the client running indefinitely
    sio.wait()

