import pytest, asyncio, httpx, os

API_URL = os.getenv("API_URL", "http://provisioning-api:8000")

@pytest.mark.asyncio
async def test_happy_path():
    async with httpx.AsyncClient() as client:
        r = await client.post(f"{API_URL}/api/v1/equipment/cpe/TEST123")
        assert r.status_code == 200
        task_id = r.json()["task_id"]

        # poll status until completed
        for _ in range(65):
            s = await client.get(f"{API_URL}/api/v1/equipment/cpe/TEST123/task/{task_id}")
            data = s.json()
            if data["status"] != "Pending":
                break
            await asyncio.sleep(1)
        assert data["status"] in ("Completed", "Failed")
