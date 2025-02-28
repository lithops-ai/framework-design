import kopf
import pika
import time
import random
import string
import kubernetes
from kubernetes import client, config
import threading
import subprocess
from utils import consume_messages

def start_kopf_controller():
    subprocess.Popen(["python3", "villager_controller.py"])

# 生成随机消息内容
def generate_random_message():
    return ''.join(random.choices(string.ascii_letters + string.digits, k=20))


def create_or_patch_villager(name, status='idle', target=None):
    api_instance = kubernetes.client.CustomObjectsApi()
    villager = {
        "apiVersion": "village.example.com/v1",
        "kind": "Villager",
        "metadata": {"name": name},
        "spec": {"name": name, "status": status, "target": target}
    }

    try:
        api_instance.create_namespaced_custom_object(
            group="village.example.com",
            version="v1",
            namespace="default",
            plural="villagers",
            body=villager
        )
        print(f"Created villager {name}")
    except kubernetes.client.exceptions.ApiException as e:
        if e.status == 409:
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
            raise

# def create_village():
#     api_instance = kubernetes.client.CustomObjectsApi()
#     village = {
#         "apiVersion": "village.example.com/v1",
#         "kind": "Village",
#         "metadata": {"name": "village1"},
#         "spec": {"name": "village1", "status": "active"}
#     }
#
#     try:
#         api_instance.create_namespaced_custom_object(
#             group="village.example.com",
#             version="v1",
#             namespace="default",
#             plural="villages",
#             body=village
#         )
#         print("Created village: village1")
#     except kubernetes.client.exceptions.ApiException as e:
#         if e.status == 409:  # 如果资源已存在
#             print("Village already exists")
#         else:
#             raise


def create_villagers():
    for i in range(1, 9):
        create_or_patch_villager(f"villager{i}")


# 初始化并启动系统的主函数
# 启动消息消费者线程时传递参数
def initialize_system():
    # 加载 Kubernetes 配置文件
    config.load_kube_config()

    # # 创建 Village 实例
    # create_village()

    # 创建 8 个村民
    create_villagers()

    # 启动每个村民的消息消费线程
    for i in range(1, 9):
        villager_name = f"villager{i}"
        consumer_thread = threading.Thread(target=consume_messages, args=(villager_name,))
        consumer_thread.start()

    threading.Thread(target=start_kopf_controller, daemon=True).start()

    # 这里可以做其他的初始化工作，比如创建 Villager 资源
    time.sleep(2)
    print("System initialized.")



if __name__ == "__main__":
    initialize_system()
