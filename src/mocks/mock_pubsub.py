import json
from typing import Dict, List, Callable, Any

class MockPubSubMessage:
    def __init__(self, data: bytes, attributes: Dict[str, str] = None):
        self.data = data
        self.attributes = attributes or {}

    @property
    def text(self) -> str:
        return self.data.decode("utf-8")

    def to_dict(self) -> Dict[str, Any]:
        return json.loads(self.text)

class MockPubSubBroker:
    _instance = None
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(MockPubSubBroker, cls).__new__(cls)
            cls._instance.topics = {}
            cls._instance.subscribers = {}
        return cls._instance

    def publish(self, topic_path: str, data: bytes, **attributes) -> str:
        if topic_path not in self.topics:
            self.topics[topic_path] = []
        msg = MockPubSubMessage(data, attributes)
        self.topics[topic_path].append(msg)
        
        # Trigger immediate subscribers if any
        if topic_path in self.subscribers:
            for cb in self.subscribers[topic_path]:
                cb(msg)
        return "msg-" + str(len(self.topics[topic_path]))

    def subscribe(self, topic_path: str, callback: Callable[[MockPubSubMessage], None]):
        if topic_path not in self.subscribers:
            self.subscribers[topic_path] = []
        self.subscribers[topic_path].append(callback)

class MockPublisherClient:
    def __init__(self):
        self.broker = MockPubSubBroker()

    def topic_path(self, project: str, topic: str) -> str:
        return f"projects/{project}/topics/{topic}"

    def publish(self, topic_path: str, data: bytes, **attrs):
        class Future:
            def __init__(self, msg_id):
                self._id = msg_id
            def result(self):
                return self._id
        msg_id = self.broker.publish(topic_path, data, **attrs)
        return Future(msg_id)

class MockSubscriberClient:
    def __init__(self):
        self.broker = MockPubSubBroker()

    def subscription_path(self, project: str, subscription: str) -> str:
        return f"projects/{project}/subscriptions/{subscription}"
