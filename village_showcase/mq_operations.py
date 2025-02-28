import pika
import requests
from requests.auth import HTTPBasicAuth

# RabbitMQ 的 HTTP API 地址
RABBITMQ_API_URL = 'http://localhost:15672/api/queues'
# 设置用户名和密码（默认是 guest/guest）
auth = HTTPBasicAuth('guest', 'guest')

# 获取队列列表
response = requests.get(RABBITMQ_API_URL, auth=auth)

if response.status_code == 200:
    queues = response.json()  # 获取所有队列的名称
    print(f"Found {len(queues)} queues.")

    # 建立 pika 连接
    connection = pika.BlockingConnection(pika.ConnectionParameters('localhost'))
    channel = connection.channel()

    for queue in queues:
        queue_name = queue['name']
        try:
            # 删除队列
            channel.queue_delete(queue=queue_name)
            print(f"Deleted queue: {queue_name}")
        except Exception as e:
            print(f"Failed to delete queue {queue_name}: {e}")

    connection.close()
else:
    print(f"Failed to fetch queues: {response.status_code}")
