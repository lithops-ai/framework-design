import threading
import logging
import json
from kubernetes import config, client
import kopf
from villager import Villager
from message_queue import MessageQueue
from utils import *

VILLAGER_STATE = {}  # 仅用于进程内记录，不再作为最终状态

logger = logging.getLogger(__name__)

# 获取 Kubernetes API 客户端
config.load_kube_config()
api_instance = client.CustomObjectsApi()


# 复用的 API 客户端
def get_api_instance():
    return api_instance


class Village:
    """管理村民和消息系统"""

    def __init__(self, total_num=3):
        self.villagers = {}
        self.total_num = total_num

    def load_existing_villagers(self):
        """从 K8s 加载村民"""
        villagers = api_instance.list_namespaced_custom_object(
            group="village.example.com",
            version="v1",
            namespace="default",
            plural="villagers"
        )

        for villager_data in villagers['items']:
            name = villager_data['metadata']['name']
            status = villager_data['status']['status'] if 'status' in villager_data else 'idle'
            self.villagers[name] = Villager(name, status)
            print(f"Loaded Villager: {name}, 状态: {status}")

    def create_new_villager(self):
        """创建新的村民"""
        name = generate_random_name()
        if name in self.villagers:
            return

        api_instance = get_api_instance()
        villager = {
            "apiVersion": "village.example.com/v1",
            "kind": "Villager",
            "metadata": {"name": name},
            "spec": {
                "name": name,
                "status": "idle",
                "target": None,
                "personality": generate_random_personality(),
                "preferences": generate_random_preferences(),
                "memory": generate_random_memory()
            }
        }

        api_instance.create_namespaced_custom_object(
            group="village.example.com",
            version="v1",
            namespace="default",
            plural="villagers",
            body=villager
        )
        print(f"Created new villager: {name}")
        self.villagers[name] = Villager(name, "idle")

    def ensure_minimum_villagers(self, min_count=3):
        """确保最少有 min_count 个村民"""
        while len(self.villagers) < min_count:
            self.create_new_villager()

    def bind_villagers_to_queues(self):
        """给所有村民绑定消息队列"""
        for villager in self.villagers.values():
            thread = threading.Thread(target=MessageQueue.bind_villager, args=(villager,), daemon=True)
            thread.start()
