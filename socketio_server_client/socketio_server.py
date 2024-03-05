import socketio
import asyncio
import uvicorn
import time
import json
import hashlib
import aiohttp
import msgpack

import const

# Define constants
IP = const.IP
PORT = const.PORT
symbols = const.TICKER

sio = socketio.AsyncServer(async_mode='asgi', transports=['websocket'])
app = socketio.ASGIApp(sio)

# Global variable to keep track of the number of connected clients
connected_clients = 0

checksums = dict(map(lambda symbol: (symbol, 0), symbols))

async def get_stock_info(session, symbol):
    url = f'https://query1.finance.yahoo.com/v8/finance/chart/{symbol}'
    params = {
        'region': 'US',
        'lang': 'en-US',
        'includePrePost': 'false',
        'interval': '2m',
        'useYfid': 'true',
        'range': '1d',
        'corsDomain': 'finance.yahoo.com',
        '.tsrc': 'finance'
    }
    headers = {
        'sec-ch-ua': '"Not_A Brand";v="8", "Chromium";v="120", "Google Chrome";v="120"',
        'Referer': 'https://finance.yahoo.com/quote/AAPL?.tsrc=fin-srch',
        'sec-ch-ua-mobile': '?0',
        'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'sec-ch-ua-platform': '"Linux"'
    }

    async with session.get(url, params=params, headers=headers) as response:
        if response.status == 200:
            return await response.json()
        else:
            print(f"Failed to fetch data for {symbol}. Status code: {response.status}")
            return None

def calculate_checksum(data):
    # Calculate the MD5 checksum of the JSON data
    data_json = json.dumps(data, sort_keys=True).encode('utf-8')
    return hashlib.md5(data_json).hexdigest()

async def get_stocks_info():
    async with aiohttp.ClientSession() as session:
        results = {}
        for symbol in symbols:
            result = await get_stock_info(session, symbol)
            if result:
                chart_data = result.get("chart", {}).get("result", [{}])[0]
                meta_data = chart_data.get("meta", {})
                if meta_data:
                    stock_info = {
                        "open_price": meta_data.get("previousClose"),
                        "close_price": meta_data.get("regularMarketPrice"),
                    }
                    checksum = calculate_checksum(stock_info)
                    if checksums[symbol] != checksum:
                        checksums[symbol] = checksum
                        results[symbol] = stock_info
                else:
                    print(f"No meta data found for {symbol}.")
            else:
                print(f"No data available for {symbol}.")

    return results

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
        r = await get_stocks_info()
        if r:
            # Add timestamp to the data
            data_with_timestamp = {"timestamp": time.time(), "data": r}

            # Serialize data to MessagePack binary format
            msgpack_data = msgpack.packb(data_with_timestamp, use_bin_type=True)
            
            await sio.emit('data', msgpack_data)  # Emitting data event to all connected clients

if __name__ == '__main__':
    uvicorn.run(app, host=IP, port=int(PORT))