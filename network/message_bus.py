from collections import defaultdict
from typing import List, Callable
from core.message import Message

class MessageBus:
    def __init__(self):
        self.subscribers = defaultdict(list)

    def subscribe(self, agent_id: str, callback: Callable):
        self.subscribers[agent_id].append(callback)

    def publish(self, message: Message):
        if message.receiver_id is None:
            for agent_id, callbacks in self.subscribers.items():
                if agent_id != message.sender_id:
                    for cb in callbacks:
                        cb(message)
        else:
            if message.receiver_id in self.subscribers:
                for cb in self.subscribers[message.receiver_id]:
                    cb(message)
