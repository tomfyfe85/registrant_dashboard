from fastapi import FastAPI
from pydantic import BaseModel
from database import get_db 
from cc_registrant_dashboard import Registrant

app = FastAPI()

class StatusUpdate(BaseModel):
    current_status: str

@app.patch("/registrant/registrant_id/{registrant_id}")
async def update_status(registrant_id: int, status_update: StatusUpdate):
   
    updates_dict = status_update.model_dump()
    status = updates_dict['current_status'] 
   
    conn = get_db()
    cur = conn.cursor()
    cur.execute("UPDATE registrants_registrant SET current_status = %s WHERE id = %s RETURNING *", (status, registrant_id))
    row = cur.fetchall()
    conn.commit()
    cur.close()
    conn.close()
    updated_registrant = Registrant(**row)

    return updated_registrant