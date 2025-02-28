import kopf
import random
import pika
import time
import logging

# 日志设置
logger = logging.getLogger(__name__)

# 初始化村民状态
VILLAGER_STATE = {f"villager{i}": "idle" for i in range(1, 9)}


# 连接到 RabbitMQ
def get_rabbitmq_channel():
    connection = pika.BlockingConnection(pika.ConnectionParameters(host='localhost'))
    channel = connection.channel()
    return channel


# 发送消息给村民
def send_message_to_villager(villager_name, message):
    channel = get_rabbitmq_channel()
    queue_name = f"{villager_name}_queue"
    channel.basic_publish(exchange='',
                          routing_key=queue_name,
                          body=message)
    logger.info(f"Sent message to {villager_name}: {message}")
    channel.close()


# 启动村民的聊天行为，检查是否处于 idle 状态，如果是，寻找一个非空闲的村民聊天
@kopf.timer("village.example.com", period=10)  # 每10秒检查一次
def villager_dialogue(spec, name, logger, **kwargs):
    for villager, state in VILLAGER_STATE.items():
        if state == "idle":
            # 随机选择一个非空闲的村民进行对话
            non_idle_villagers = [v for v, s in VILLAGER_STATE.items() if s == "talking" and v != villager]

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
        listen_to_villager_queue(f"villager{i}")


if __name__ == "__main__":
    import kopf

    # 启动对话控制器
    kopf.run(villager_dialogue)  # 启动定时任务

    # 启动每个村民的监听
    start_listening()
