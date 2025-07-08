
import logging
from collections import defaultdict
from typing import Callable, Any, Awaitable, Dict, List

logger = logging.getLogger(__name__)

# Type hint for an async callback
AsyncCallback = Callable[..., Awaitable[None]]

class EventBus:
    """
    A simple asynchronous event bus for pub/sub communication.
    """
    def __init__(self):
        self._subscribers: Dict[str, List[AsyncCallback]] = defaultdict(list)

    def subscribe(self, event: str, callback: AsyncCallback):
        """
        Subscribes a callback to a specific event.

        Args:
            event: The name of the event to subscribe to.
            callback: The asynchronous function to call when the event is published.
        """
        self._subscribers[event].append(callback)
        logger.info(f"Callback {callback.__name__} subscribed to event '{event}'")

    async def publish(self, event: str, *args, **kwargs: Any):
        """
        Publishes an event, calling all subscribed callbacks.

        Args:
            event: The name of the event to publish.
            *args: Positional arguments to pass to the callbacks.
            **kwargs: Keyword arguments to pass to the callbacks.
        """
        if event not in self._subscribers:
            logger.warning(f"Event '{event}' published, but has no subscribers.")
            return

        logger.info(f"Publishing event '{event}' to {len(self._subscribers[event])} subscribers.")
        for callback in self._subscribers[event]:
            try:
                await callback(*args, **kwargs)
            except Exception as e:
                logger.error(f"Error in event '{event}' callback {callback.__name__}: {e}", exc_info=True)

