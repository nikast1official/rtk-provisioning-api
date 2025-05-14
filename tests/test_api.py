
import pytest
import httpx
import asyncio

BASE = "http://localhost:8000"

@pytest.mark.asyncio
async def test_create_and_check():
    async with httpx.AsyncClient() as client:
        # создаём задачу
        resp = await client.post(f"{BASE}/api/v1/equipment/cpe/TEST123")
        assert resp.status_code == 200
        data = resp.json()
        task_id = data["task_id"]

        # ждём обработки
        await asyncio.sleep(65)

        # получаем статус
        resp2 = await client.get(f"{BASE}/api/v1/equipment/cpe/TEST123/task/{task_id}")
        assert resp2.status_code == 200
        status = resp2.json()["status"]
        assert status in ("Completed", "Failed")
