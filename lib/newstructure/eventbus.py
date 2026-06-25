from collections import defaultdict

class EventBus:
    def __init__(self):
        self.subscribers = defaultdict(list)

    def subscribe(self, event_type, callback):
        if callback not in self.subscribers[event_type]:
           self.subscribers[event_type].append(callback)

    def publish(self, event_type, data=None):
        for cb in self.subscribers[event_type]:
            cb(data)

    def unsubscribe(self, event_type, callback):
        if callback in self.subscribers[event_type]:
            self.subscribers[event_type].remove(callback)            