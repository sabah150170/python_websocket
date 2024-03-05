import asyncio
import json
import time
import msgpack
import hashlib
import aiohttp
from autobahn.asyncio.websocket import WebSocketServerProtocol, WebSocketServerFactory

import const

# Define constants
IP = const.IP
PORT = const.PORT
symbols = const.TICKER

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

    def send_data(self, data):
        # Send data to all connected clients
        for client in self.clients:
            # Add timestamp to the data
            data_with_timestamp = {"timestamp": time.time(), "data": data}

            # Serialize data to MessagePack binary format
            msgpack_data = msgpack.packb(data_with_timestamp, use_bin_type=True)

            client.sendMessage(msgpack_data, isBinary=True)

# Function to read data from JSON file and send to clients
async def send_data_to_clients(factory):
    while True:
        r = await get_stocks_info()
        if r:
            # Serialize the data to JSON and send it to all clients
            factory.send_data(r)

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
        server.close()
        loop.run_until_complete(server.wait_closed())
        loop.close()
