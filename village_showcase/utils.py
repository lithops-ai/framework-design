import time
import random
import pika


VILLAGER_STATE = {f"villager{i}": "idle" for i in range(1, 9)}

# 获取 RabbitMQ 通道
def get_rabbitmq_channel():
    connection = pika.BlockingConnection(pika.ConnectionParameters('localhost'))
    channel = connection.channel()
    channel.queue_declare(queue='villager_queue')
    return channel


# 消费消息函数
def consume_messages(villager_name):
    channel = get_rabbitmq_channel()
    queue_name = f"{villager_name}_queue"

    # 显式声明队列，确保队列存在，且是持久化的
    channel.queue_declare(queue=queue_name, durable=True)

    def on_message(ch, method, properties, body):
        message = body.decode()
        print(f"{villager_name} received message: {message}")

        if "start_talking_to" in message:
            # 从消息中提取目标村民
            other_villager = message.split("_to_")[1]
            print(f"{villager_name} started talking to {other_villager}")

            # 模拟对话，时间随机
            time.sleep(random.randint(1, 5))  # 模拟对话时间

            # 完成对话，恢复为 idle 状态
            VILLAGER_STATE[villager_name] = "idle"
            VILLAGER_STATE[other_villager] = "idle"
            print(f"{villager_name} finished talking to {other_villager}")

            # 你可以在这里发送“对话结束”的消息给其他村民，或者进行其他逻辑

    # 开始消费消息
    channel.basic_consume(queue=queue_name, on_message_callback=on_message, auto_ack=True)
    print(f"{villager_name} is waiting for messages.")
    channel.start_consuming()
