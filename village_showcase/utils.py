import random



# 英文名字列表（可以根据需要增加更多名字）
english_names = [
    "James", "John", "Robert", "Michael", "William", "David", "Richard",
    "Joseph", "Charles", "Thomas", "Christopher", "Daniel", "Matthew",
    "Anthony", "Mark", "Donald", "Steven", "Paul", "Andrew", "Joshua"
]


used_names = set()  # 用于记录已使用的名字


def generate_random_name():
    while True:
        # 随机生成名字
        name = random.choice(english_names).lower()

        # 检查名字是否已被使用
        if name not in used_names:
            used_names.add(name)
            return name
        # 如果名字重复，重新生成