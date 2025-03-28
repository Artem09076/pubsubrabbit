import time

from pika import BlockingConnection, ConnectionParameters
from pika.exchange_type import ExchangeType


def publish_masseges() -> None:
    conn = BlockingConnection(ConnectionParameters(host='rabbitmq'))
    channel = conn.channel()

    channel.exchange_declare(exchange='publisher', exchange_type=ExchangeType.fanout)

    with open('publisher/input.txt', 'r') as file:
        for line in file:
            message = line.rstrip()
            channel.basic_publish(exchange='publisher', routing_key='', body=message)
            print(f'Send: {message}')
            time.sleep(3)

    conn.close()

if __name__ == '__main__':
    publish_masseges()