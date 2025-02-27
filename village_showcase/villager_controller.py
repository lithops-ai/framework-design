# -*- coding: utf-8 -*-
# villager_controller.py
import kopf
import pika
import time
import random
import string
from utils import get_rabbitmq_channel


# 生成随机消息内容
def generate_random_message():
    return ''.join(random.choices(string.ascii_letters + string.digits, k=20))


# 村民创建或更新事件处理
@kopf.on.create('village.example.com', 'v1', 'villagers')
@kopf.on.update('village.example.com', 'v1', 'villagers')
def handle_villager(event, spec, name, namespace, logger, **kwargs):
    status = spec.get('status', 'idle')
    target = spec.get('target', None)

    if status == 'idle':
        logger.info(f"Villager {name} is idle.")
        channel = get_rabbitmq_channel()
        channel.basic_publish(exchange='',
                              routing_key='villager_queue',
                              body=name)
        logger.info(f"Sent idle state for {name} to RabbitMQ.")

    elif status == 'talking' and target:
        logger.info(f"Villager {name} is talking to {target}.")
        message = f"Message from {name} to {target}: {generate_random_message()}"
        channel = get_rabbitmq_channel()
        channel.basic_publish(exchange='',
                              routing_key='villager_queue',
                              body=message)
        logger.info(f"Sent message from {name} to {target}.")
        time.sleep(2)  # 模拟对话的交流时间
        logger.info(f"{target} replied to {name}")


# 村民删除事件
@kopf.on.delete('village.example.com', 'v1', 'villagers')
def delete_villager(event, name, namespace, logger, **kwargs):
    logger.info(f"Villager {name} deleted.")
