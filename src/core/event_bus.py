# src/core/event_bus.py
from collections import defaultdict
from typing import Callable, Any

class EventBus:
    def __init__(self):
        self.listeners = defaultdict(list)

    def subscribe(self, event_type: str, listener: Callable):
        self.listeners[event_type].append(listener)

    async def publish(self, event_type: str, *args, **kwargs):
        for listener in self.listeners[event_type]:
            await listener(*args, **kwargs)

event_bus = EventBus()