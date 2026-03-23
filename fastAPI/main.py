from fastapi import FastAPI
from pydantic import BaseModel
from database import get_db 

app = FastAPI()

class StatusUpdate(BaseModel):
    current_status: str

@app.patch("/registrant/registrant_id/{registrant_id}")
async def update_status(registrant_id: int, status_update: StatusUpdate):
    place_holders = ""
    values = []
    
    updates_dict = status_update.current_status.models_dump()

    for k, v in updates_dict.items():
        place_holders += str(k) + " = %s, "
        values.append(v)
    
    print(place_holders, values)
    
    conn = get_db()
    cur = conn.cursor()
    updated_registrant = cur.execute(f"INSERT INTO Resgistrant VALUES ({place_holders[:-2]})" % set(values))
    
    conn.commit()
    cur.close()
    conn.close()
    # print(registrant) 
    return updated_registrant
