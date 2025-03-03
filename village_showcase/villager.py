from message_queue import MessageQueue

class Villager:
    def __init__(self, name, status="idle"):
        self.name = name
        self.status = status

    def handle_message(self, message):
        """处理收到的消息"""
        if message["type"] == "start_conversation":
            self.start_conversation(message)
        elif message["type"] == "conversation_segment":
            self.respond_to_conversation(message)

    def start_conversation(self, message):
        """处理对话开始"""
        print(f"{self.name} is starting a conversation with {message['from']}.")
        MessageQueue.send_message(message['from'], "conversation_segment", self.name,
                                  f"Hello {message['from']}, let's talk!")

    def respond_to_conversation(self, message):
        """处理对话消息"""
        print(f"{self.name} received a message from {message['from']}: {message['message']}")
        MessageQueue.send_message(message['from'], "conversation_segment", self.name,
                                  f"Got your message: {message['message']}")
