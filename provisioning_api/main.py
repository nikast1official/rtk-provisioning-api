import asyncio
import json
from fastapi import FastAPI, HTTPException
from uuid import uuid4, UUID
import uvicorn

from .models import Task, TaskStatus
from .task_store import InMemoryTaskStore
from .rabbit import MQ
import aio_pika

RABBIT_URL = "amqp://guest:guest@rabbitmq/"
TASKS_QUEUE = "tasks"
RESULTS_QUEUE = "results"

app = FastAPI(title="provisioning-api")
store = InMemoryTaskStore()
mq = MQ(RABBIT_URL)


@app.post("/api/v1/equipment/cpe/{equipment_id}")
async def enqueue_task(equipment_id: str):
    task = Task(equipment_id=equipment_id)
    store.add(task)
    await mq.publish(TASKS_QUEUE, json.loads(task.model_dump_json()))
    return {
        "task_id": str(task.id),
        "status_url": f"/api/v1/equipment/cpe/{equipment_id}/task/{task.id}"
    }


@app.get("/api/v1/equipment/cpe/{equipment_id}/task/{task_id}")
async def get_status(equipment_id: str, task_id: UUID):
    task = store.get(task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Unknown task")
    return task.dict()


# ---------- consume results ----------

async def wait_for_rabbit(url, timeout=30):
    for i in range(timeout):
        try:
            conn = await aio_pika.connect_robust(url)
            await conn.close()
            print(f"✅ Connected to RabbitMQ on attempt {i + 1}")
            return
        except Exception:
            await asyncio.sleep(1)
    raise RuntimeError("❌ RabbitMQ not available after timeout")


@app.on_event("startup")
async def subscribe_to_results():
    await wait_for_rabbit(RABBIT_URL)

    async def callback(msg):
        body = msg.body.decode()
        data = json.loads(body)
        task_id = UUID(data["task_id"])
        task = store.get(task_id)
        if task:
            task.status = data["status"]
            task.details = data["details"]
        await msg.ack()

    asyncio.create_task(mq.consume(RESULTS_QUEUE, callback))


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)

