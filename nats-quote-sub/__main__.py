import argparse, sys
import asyncio
import os
import signal
from nats.aio.client import Client as NATS
import mysql.connector
from dotenv import load_dotenv
load_dotenv()
import socket
import json
from datetime import datetime

SUBJECT = 'friends_quote'
QUEUE = 'friends_queue'

def write_to_db(data):
    db = mysql.connector.connect(
        host='localhost',
        user=os.getenv('DB_USER'),
        database=os.getenv('DB_NAME'),
        password=os.getenv('DB_PASSWRD'),
    )
    cursor = db.cursor()

    quote_insert = (
        "INSERT INTO quotes (quote_str, post_time, friends_character, ip, nats_subject) "
        "VALUES (%s, %s, %s, %s, %s)"
    )

    quote_str = data['quote']
    character = data['character']
    host = socket.gethostname()
    ip_addr = socket.gethostbyname(host) or 'NA'
    datetime_now = datetime.now()

    data_quote = (quote_str, datetime_now, character, ip_addr, SUBJECT)

    cursor.execute(quote_insert, data_quote)
    db.commit()
    cursor.close()
    db.close()


async def run(loop):
    nats_conn = NATS()

    async def error_cb(e):
        print('Error:', e)

    async def closed_cb():
        print('Connection to NATS is closed.')
        await asyncio.sleep(0.1, loop=loop)
        loop.stop()

    async def reconnected_cb():
        print(f'Connected to NATS at {nats_conn.connected_url.netloc}...')

    async def subscribe_handler(msg):
        subject = msg.subject
        reply = msg.reply
        data = msg.data.decode()
        write_to_db(json.loads(data))

    options = {
        'loop': loop,
        'error_cb': error_cb,
        'closed_cb': closed_cb,
        'reconnected_cb': reconnected_cb
    }

    try:
        options['servers'] = 'nats://127.0.0.1:4222'

        await nats_conn.connect(**options)
    except Exception as e:
        print(e)
        show_usage_and_die()

    print(f'Connected to NATS at {nats_conn.connected_url.netloc}...')
    def signal_handler():
        if nats_conn.is_closed:
            return
        print('Disconnecting...')
        loop.create_task(nats_conn.close())

    for sig in ('SIGINT', 'SIGTERM'):
        loop.add_signal_handler(getattr(signal, sig), signal_handler)

    await nats_conn.subscribe(SUBJECT, QUEUE, subscribe_handler)

if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.run_until_complete(run(loop))
    try:
        loop.run_forever()
    finally:
        loop.close()