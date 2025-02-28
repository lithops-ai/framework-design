import kopf
import random
import pika
import time
import logging
import threading
from utils import consume_messages, VILLAGER_STATE

logger = logging.getLogger(__name__)


# 获取 RabbitMQ channel
def get_rabbitmq_channel():
    connection = pika.BlockingConnection(pika.ConnectionParameters(host='localhost'))
    channel = connection.channel()
    return channel


# 发送消息给指定的村民
def send_message_to_villager(villager_name, message):
    channel = get_rabbitmq_channel()
    queue_name = f"{villager_name}_queue"

    # 显式声明队列，确保队列存在
    channel.queue_declare(queue=queue_name, durable=True)

    # 发送消息
    channel.basic_publish(
        exchange='',
        routing_key=queue_name,
        body=message,
        properties=pika.BasicProperties(
            delivery_mode=2,  # 将消息标记为持久化
        )
    )
    logger.info(f"Sent message to {villager_name}: {message}")
    channel.close()


# 定时检查每个村民的状态
@kopf.timer("villager.village.example.com", interval=10)  # 每10秒检查一次
def villager_dialogue(spec, name, logger, **kwargs):
    villager = name
    state = VILLAGER_STATE[villager]

    if state == "idle":
        # 随机选择一个非空闲的村民进行对话
        non_idle_villagers = [v for v, s in VILLAGER_STATE.items() if s != "talking" and v != villager]

        if non_idle_villagers:
            # 随机选择一个非空闲村民
            selected_villager = random.choice(non_idle_villagers)
            logger.info(f"{villager} is about to start talking to {selected_villager}")

            # 发送开始聊天消息
            send_message_to_villager(villager, f"start_talking_to_{selected_villager}")
            send_message_to_villager(selected_villager, f"start_talking_to_{villager}")

            # 设置村民为 talking 状态
            VILLAGER_STATE[villager] = "talking"
            VILLAGER_STATE[selected_villager] = "talking"



# 监听村民队列，处理消息
def listen_to_villager_queue(villager_name):
    channel = get_rabbitmq_channel()
    queue_name = f"{villager_name}_queue"

    def callback(ch, method, properties, body):
        message = body.decode()
        logger.info(f"{villager_name} received message: {message}")

        if "start_talking_to" in message:
            other_villager = message.split("_to_")[1]
            logger.info(f"{villager_name} started talking to {other_villager}")

            # 模拟对话
            time.sleep(2)  # 模拟聊天时间

            # 完成对话后，变回 idle 状态
            VILLAGER_STATE[villager_name] = "idle"
            VILLAGER_STATE[other_villager] = "idle"
            logger.info(f"{villager_name} and {other_villager} finished talking.")

            # 通知其他村民对话结束
            send_message_to_villager(villager_name, "conversation_end")
            send_message_to_villager(other_villager, "conversation_end")

    channel.basic_consume(queue=queue_name, on_message_callback=callback, auto_ack=True)
    channel.start_consuming()

# 启动控制器监听每个村民的队列
def start_listening():
    for i in range(1, 9):
        threading.Thread(target=consume_messages, args=(f"villager{i}",), daemon=True).start()


if __name__ == "__main__":
    # 启动 kopf 事件处理器
    kopf.run()

    # 启动村民的消息监听
    start_listening()
