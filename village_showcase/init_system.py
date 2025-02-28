# init_system.py
import logging
import pika
import time
import random
import string
import kubernetes
from kubernetes import config, client
import threading
import subprocess

import kopf
from utils import generate_random_name

logger = logging.getLogger(__name__)


# 获取 RabbitMQ 通道
def get_rabbitmq_channel():
    connection = pika.BlockingConnection(pika.ConnectionParameters('localhost'))
    channel = connection.channel()
    return channel


VILLAGER_STATE = {}


# def start_kopf_controller():
#     subprocess.Popen(["python3", "villager_controller.py"])


# 生成随机消息内容
def generate_random_message():
    return ''.join(random.choices(string.ascii_letters + string.digits, k=20))


def generate_random_personality():
    # 随机生成村民的个性特征
    return {
        "extroversion": random.uniform(0, 1),  # 外向性
        "neuroticism": random.uniform(0, 1),  # 神经质
        "agreeableness": random.uniform(0, 1),  # 宜人性
        "openness": random.uniform(0, 1)  # 开放性
    }


def generate_random_preferences():
    # 随机生成村民的偏好
    topics = ["weather", "food", "politics", "sports", "music"]
    preferred_topics = random.sample(topics, k=2)  # 随机选取两个偏好话题
    disliked_topics = random.sample([topic for topic in topics if topic not in preferred_topics], k=2)  # 排除已经选择的偏好
    return {
        "preferred_topics": preferred_topics,
        "disliked_topics": disliked_topics
    }


def generate_random_memory():
    # 初始时没有记忆，记忆是动态变化的
    return {
        "conversations": [],
        "preferences": {
            "preferred_topics": random.sample(["weather", "food", "politics", "sports", "music"], k=2),
            "disliked_topics": random.sample(["weather", "food", "politics", "sports", "music"], k=2)
        }
    }


def create_or_patch_villager(status='idle', target=None):
    # 随机生成一个名字
    all_villagers = VILLAGER_STATE.keys()
    if len(all_villagers) >= 8: return
    name = generate_random_name()

    api_instance = kubernetes.client.CustomObjectsApi()
    villager = {
        "apiVersion": "village.example.com/v1",
        "kind": "Villager",
        "metadata": {"name": name},
        "spec": {
            "name": name,
            "status": status,
            "target": target,
            "personality": generate_random_personality(),
            "preferences": generate_random_preferences(),
            "memory": generate_random_memory()
        }
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
        VILLAGER_STATE[name] = 'idle'
    except kubernetes.client.exceptions.ApiException as e:
        if e.status == 409:  # 资源已存在
            # 如果资源已存在，则进行部分更新（patch）
            api_instance.patch_namespaced_custom_object(
                group="village.example.com",
                version="v1",
                namespace="default",
                plural="villagers",
                name=name,
                body={
                    "spec": {
                        "status": status,
                        "target": target,
                        "personality": generate_random_personality(),
                        "preferences": generate_random_preferences(),
                        "memory": generate_random_memory()
                    }
                }
            )
            print(f"Patched existing villager {name}")
        else:
            raise  # 其他异常需要处理


def create_villagers():
    while len(VILLAGER_STATE.keys()) < 8:
        create_or_patch_villager()


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


def check_existing_villagers():
    # 获取API客户端
    api = client.CustomObjectsApi()

    # 获取所有的 'villager' 类型对象
    group = 'village.example.com'  # CRD的API group
    version = 'v1'  # CRD的API version
    namespace = 'default'  # 如果是有命名空间，可以指定
    plural = 'villagers'  # CRD的资源名称（复数形式）

    # 查询所有 'villager' 对象
    villagers = api.list_namespaced_custom_object(
        group=group,
        version=version,
        namespace=namespace,
        plural=plural
    )

    # 打印获取的对象信息
    print(f"当前集群中有 {len(villagers['items'])} 个 villager 对象.")
    for villager in villagers['items']:
        print(f"Villager: {villager['metadata']['name']}, 状态: {villager['spec']['status']}")
        VILLAGER_STATE[villager['metadata']['name']] = villager['spec']['status']


# 初始化并启动系统的主函数
# 启动消息消费者线程时传递参数
def initialize_system():
    # 加载 Kubernetes 配置文件
    config.load_kube_config()
    check_existing_villagers()
    # 创建 8 个村民
    create_villagers()


    print("Villagers initialized.")


    # 启动每个村民的消息消费线程
    for villager_name in VILLAGER_STATE.keys():
        consumer_thread = threading.Thread(target=consume_messages, args=(villager_name,))
        consumer_thread.start()
    print("consumer threads initialized")

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


@kopf.timer("villager.village.example.com", interval=10)  # 每10秒检查一次
def villager_dialogue(spec, name, logger, **kwargs):
    villager = name
    try:
        state = VILLAGER_STATE[villager]
        print(f"Checking villager {villager} with current state: {state}")

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
                logger.info(f"Set state of {villager} and {selected_villager} to 'talking'")

            else:
                logger.info(f"No non-idle villagers available for {villager} to talk to.")
        else:
            logger.info(f"{villager} is already {state}, skipping.")

    except Exception as e:
        logger.error(f"Error occurred while processing villager {villager}: {e}")
        # 也可以根据需要决定是否抛出异常、重试或执行其他操作


if __name__ == "__main__":
    initialize_system()
    kopf.run()
