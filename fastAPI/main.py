from fastapi import FastAPI
from pydantic import BaseModel
from database import get_db 

app = FastAPI()

class StatusUpdate(BaseModel):
    current_status: str

@app.patch("/registrant/registrant_id/{registrant_id}")
async def update_status(registrant_id: int, status_update: StatusUpdate):
      
    updates_dict = status_update.model_dump()
    status = updates_dict['current_status'] 
    
    conn = get_db()
    cur = conn.cursor()
    # updated_registrant = cur.execute("UPDATE registrants_registrant SET current_status = %s WHERE id = %s", (status, registrant_id))
    updated_registrant = cur.execute("UPDATE registrants_registrant (current_status) VALUES(%s) WHERE id = %s", (status, registrant_id))

    conn.commit()
    cur.close()
    conn.close()
    # print(registrant) 
    return updated_registrant
