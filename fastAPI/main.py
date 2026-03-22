from fastapi import FastAPI
from pydantic import BaseModel
from database import get_db 

app = FastAPI()

class StatusUpdate(BaseModel):
    current_status: str

@app.patch("/registrant/registrant_id/{registrant_id}")
async def update_status(registrant_id: int, status_update: StatusUpdate):
    print(status_update)
    db = get_db()
    print(db, 'hello')
    
    return {"test": "Hello World"}
