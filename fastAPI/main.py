from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI()

class StatusUpdate(BaseModel):
    current_status: str

@app.patch("/registrant/registrant_id/{registrant_id}")
async def update_status(registrant_id: int, status_update: StatusUpdate):
    print(status_update)
    return {"test": "Hello World"}
