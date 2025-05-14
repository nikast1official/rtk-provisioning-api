import asyncio
import aio_pika
import json

class MQ:
    def __init__(self, url: str):
        self.url = url
        self._connection: aio_pika.RobustConnection | None = None
        self._channel: aio_pika.Channel | None = None

    async def _ensure(self):
        if self._connection is None:
            self._connection = await aio_pika.connect_robust(self.url)
            self._channel = await self._connection.channel()

    async def publish(self, queue: str, message: dict):
        await self._ensure()
        q = await self._channel.declare_queue(queue, durable=True)
        await self._channel.default_exchange.publish(
            aio_pika.Message(body=json.dumps(message).encode()),
            routing_key=q.name
        )

    async def consume(self, queue: str, cb):
        await self._ensure()
        q = await self._channel.declare_queue(queue, durable=True)
        await q.consume(cb, no_ack=False)
