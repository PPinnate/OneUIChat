from __future__ import annotations

import asyncio


class EventBus:
    def __init__(self):
        self._queues: set[asyncio.Queue] = set()

    async def publish(self, event: dict) -> None:
        for queue in list(self._queues):
            await queue.put(event)

    def subscribe(self) -> asyncio.Queue:
        queue: asyncio.Queue = asyncio.Queue()
        self._queues.add(queue)
        return queue

    def unsubscribe(self, queue: asyncio.Queue) -> None:
        self._queues.discard(queue)
