import asyncio, json, aio_pika, httpx, os
from uuid import UUID
from provisioning_api.models import TaskStatus

RABBIT_URL = os.getenv("RABBIT_URL", "amqp://guest:guest@rabbitmq/")
TASKS_QUEUE = "tasks"
RESULTS_QUEUE = "results"
SERVICE_STUB_URL = os.getenv("SERVICE_STUB_URL", "http://service-stub:8001")

async def handle_message(message: aio_pika.IncomingMessage):
    async with message.process():
        payload = json.loads(message.body)
        task_id = payload["id"]
        equipment_id = payload["equipment_id"]
        async with httpx.AsyncClient(timeout=65) as client:
            try:
                r = await client.post(f"{SERVICE_STUB_URL}/api/v1/equipment/cpe/{equipment_id}")
                status = TaskStatus.COMPLETED
                details = {"code": r.status_code, "content": r.json()}
            except httpx.HTTPStatusError as e:
                status = TaskStatus.FAILED
                details = {"code": e.response.status_code, "content": e.response.text}
            except Exception as e:
                status = TaskStatus.FAILED
                details = {"error": str(e)}

        conn = await aio_pika.connect_robust(RABBIT_URL)
        async with conn:
            ch = await conn.channel()
            await ch.default_exchange.publish(
                aio_pika.Message(body=json.dumps({
                    "task_id": task_id,
                    "status": status,
                    "details": details,
                }).encode()),
                routing_key=RESULTS_QUEUE
            )
async def wait_for_rabbit(url, timeout=30):
    import aio_pika
    for _ in range(timeout):
        try:
            conn = await aio_pika.connect_robust(url)
            await conn.close()
            print("RabbitMQ is up.")
            return
        except Exception:
            await asyncio.sleep(1)
    raise RuntimeError("RabbitMQ not available after timeout")

async def main():
    await wait_for_rabbit(RABBIT_URL)
    conn = await aio_pika.connect_robust(RABBIT_URL)
    async with conn:
        ch = await conn.channel()
        queue = await ch.declare_queue(TASKS_QUEUE, durable=True)
        await queue.consume(handle_message)
        print("Worker started")
        await asyncio.Future()  # run forever


if __name__ == "__main__":
    asyncio.run(main())
