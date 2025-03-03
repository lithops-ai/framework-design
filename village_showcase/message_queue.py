import pika
import json


class MessageQueue:
    """管理 RabbitMQ 队列"""

    @staticmethod
    def get_channel():
        """获取 RabbitMQ 频道"""
        connection = pika.BlockingConnection(pika.ConnectionParameters("localhost"))
        return connection.channel()

    @staticmethod
    def send_message(receiver, message_type, sender, content=""):
        """发送消息"""
        message = {
            "type": message_type,
            "from": sender,
            "to": receiver,
            "message": content
        }
        channel = MessageQueue.get_channel()
        queue_name = f"{receiver}_queue"
        channel.queue_declare(queue=queue_name, durable=True)
        channel.basic_publish(
            exchange="",
            routing_key=queue_name,
            body=json.dumps(message),
            properties=pika.BasicProperties(delivery_mode=2)  # 消息持久化
        )
        print(f"{sender} sent {message_type} to {receiver}: {content}")
        channel.close()

    @staticmethod
    def bind_villager(villager):
        """为村民绑定 RabbitMQ 监听"""
        channel = MessageQueue.get_channel()
        queue_name = f"{villager.name}_queue"
        channel.queue_declare(queue=queue_name, durable=True)

        def on_message(ch, method, properties, body):
            """处理收到的消息"""
            message = json.loads(body)
            villager.handle_message(message)

        channel.basic_consume(queue=queue_name, on_message_callback=on_message, auto_ack=True)
        print(f"{villager.name} is waiting for messages.")
        channel.start_consuming()

