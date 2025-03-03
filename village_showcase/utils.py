import random
import pika
import string


# 英文名字列表（可以根据需要增加更多名字）
english_names = [
    "James", "John", "Robert", "Michael", "William", "David", "Richard",
    "Joseph", "Charles", "Thomas", "Christopher", "Daniel", "Matthew",
    "Anthony", "Mark", "Donald", "Steven", "Paul", "Andrew", "Joshua"
]


used_names = set()  # 用于记录已使用的名字

# 获取 RabbitMQ 通道
def get_rabbitmq_channel():
    connection = pika.BlockingConnection(pika.ConnectionParameters('localhost'))
    channel = connection.channel()
    return channel

def generate_random_name():
    while True:
        # 随机生成名字
        name = random.choice(english_names).lower()

        # 检查名字是否已被使用
        if name not in used_names:
            used_names.add(name)
            return name
        # 如果名字重复，重新生成



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
