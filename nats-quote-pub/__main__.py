import requests
import json
import asyncio
from nats.aio.client import Client as NATS

# General pattern taken from https://github.com/nats-io/nats.py/blob/master/examples/nats-pub/__main__.py
async def run(loop):
    nats_conn = NATS()
    subject = 'friends_quote'

    async def error_cb(e):
        print('Error:', e)

    async def closed_cb():
        print('Connection to NATS is closed.')

    async def reconnected_cb():
        print(f'Connected to NATS at {nats_conn.connected_url.netloc}...')

    async def get_quote():
        url = 'https://friends-quotes-api.herokuapp.com/quotes/random'
        headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/74.0.3729.169 Safari/537.36'
        }

        req = requests.get(url, headers=headers)
        return json.dumps(req.json()).encode()

    quote = await get_quote()

    options = {
        'loop': loop,
        'error_cb': error_cb,
        'closed_cb': closed_cb,
        'reconnected_cb': reconnected_cb
    }

    try:
        options['servers'] = 'nats://nats:4222'

        await nats_conn.connect(**options)
    except Exception as e:
        print(e)

    print(f'Connected to NATS at {nats_conn.connected_url.netloc}...')

    await nats_conn.publish(subject, quote)
    await nats_conn.flush()
    await nats_conn.close()

if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    try:
        loop.run_until_complete(run(loop))
    finally:
        loop.close()
