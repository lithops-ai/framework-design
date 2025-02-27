
import pika

# 获取 RabbitMQ 通道
def get_rabbitmq_channel():
    connection = pika.BlockingConnection(pika.ConnectionParameters('localhost'))
    channel = connection.channel()
    channel.queue_declare(queue='villager_queue')
    return channel
