from fastapi import FastAPI, HTTPException
import asyncio
import uvicorn

app = FastAPI(title="service-stub")

@app.post("/api/v1/equipment/cpe/{equipment_id}")
async def provision_equipment(equipment_id: str):
    # emulate long‑running legacy call
    await asyncio.sleep(60)
    # naive demo: even/odd id -> success / not found
    if int(hash(equipment_id)) % 5 == 0:
        raise HTTPException(status_code=404, detail="Not found")
    return {"equipment_id": equipment_id, "status": "ok"}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8001)
