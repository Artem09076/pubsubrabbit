import sys

from pika import  BlockingConnection
from pika.connection import ConnectionParameters
from pika.exchange_type import ExchangeType
from redis import Redis

redis_client = Redis(
    host='redis',
    socket_timeout=5,
    socket_connect_timeout=5,
    retry_on_timeout=True,
    max_connections=20,
    health_check_interval=30
    )

def callback(channel, method, properties, body: bytes):
    filename = sys.argv[1] if len(sys.argv) > 1 else 'output.txt'
    with open(f'consumer/{filename}', 'a') as file:
        message = body.decode()
        message_id = hash(message)
        if redis_client.exists(f'message_id:{message_id}'):
            return
        if not redis_client.setnx(f'message_id:{message_id}', 'processing'):
            return
        
        file.write(body.decode() + '\n')
        redis_client.setex(f"message_res:{message_id}", 3600, 'Processed')
        redis_client.set(f"message_status:{message_id}", "processed")


def consume_messages():
    conn = BlockingConnection(ConnectionParameters(host='rabbitmq'))
    channel = conn.channel()
    channel.exchange_declare(exchange='publisher', exchange_type=ExchangeType.fanout)
    channel.queue_declare(queue='task_queue', durable=True)
    channel.queue_bind(exchange='publisher', queue='task_queue')
    channel.basic_consume(queue='task_queue', on_message_callback=callback, auto_ack=True)

    channel.start_consuming()

if __name__ == '__main__':
    consume_messages()