# init_system.py
import kopf
import pika
import time
import random
import string
import kubernetes
from kubernetes import client, config
import threading
import subprocess
from utils import get_rabbitmq_channel


def start_kopf_controller():
    subprocess.Popen(["python3", "villager_controller.py"])


# 生成随机消息内容
def generate_random_message():
    return ''.join(random.choices(string.ascii_letters + string.digits, k=20))


# 消费者：监听并处理 RabbitMQ 中的消息
def consume_messages():
    def on_message(ch, method, properties, body):
        message = body.decode()
        print(f"Received message: {message}")
        # 模拟回复
        if "Message from" in message:
            sender, receiver = message.split(' to ')
            print(f"{receiver} replies to {sender}")
            # 可以通过消息队列返回消息，模拟回复的过程

    connection = pika.BlockingConnection(pika.ConnectionParameters('localhost'))
    channel = connection.channel()
    channel.queue_declare(queue='villager_queue')
    channel.basic_consume(queue='villager_queue', on_message_callback=on_message, auto_ack=True)

    print('Waiting for messages. To exit press CTRL+C')
    channel.start_consuming()


def create_or_patch_villager(name, status='idle', target=None):
    api_instance = kubernetes.client.CustomObjectsApi()
    villager = {
        "apiVersion": "village.example.com/v1",
        "kind": "Villager",
        "metadata": {"name": name},
        "spec": {"name": name, "status": status, "target": target}
    }

    try:
        # 尝试创建
        api_instance.create_namespaced_custom_object(
            group="village.example.com",
            version="v1",
            namespace="default",
            plural="villagers",
            body=villager
        )
        print(f"Created villager {name}")
    except kubernetes.client.exceptions.ApiException as e:
        if e.status == 409:  # 资源已存在
            # 如果资源已存在，则进行部分更新（patch）
            api_instance.patch_namespaced_custom_object(
                group="village.example.com",
                version="v1",
                namespace="default",
                plural="villagers",
                name=name,
                body={"spec": {"status": status, "target": target}}
            )
            print(f"Patched existing villager {name}")
        else:
            raise  # 其他异常需要处理


# 一键创建 8 个村民
def create_villagers():
    for i in range(1, 9):
        create_or_patch_villager(f"villager{i}")


# 初始化并启动系统的主函数
def initialize_system():
    # 加载 Kubernetes 配置文件
    config.load_kube_config()

    # 创建 8 个村民
    create_villagers()

    # 启动消息消费者线程
    consumer_thread = threading.Thread(target=consume_messages)
    consumer_thread.start()

    threading.Thread(target=start_kopf_controller, daemon=True).start()

    # 这里可以做其他的初始化工作，比如创建 Villager 资源
    time.sleep(2)
    print("System initialized.")


if __name__ == "__main__":
    initialize_system()
