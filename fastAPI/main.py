from fastapi import FastAPI
from pydantic import BaseModel
from database import get_db 
from psycopg2.extras import RealDictCursor
from cache import add_to_buffer, drain_worker

app = FastAPI()

class StatusUpdate(BaseModel):
    current_status: str

class Registrant(BaseModel):
    id: int
    name: str
    email: str
    company_fk_id: int
    event_id: int
    guest_type: str
    current_status: str

def write_to_postgres(registrant_id: int, status_update: StatusUpdate):
    status = status_update.current_status 
    conn = get_db()
    cur = conn.cursor(cursor_factory=RealDictCursor)
    cur.execute("UPDATE registrants_registrant SET current_status = %s WHERE id = %s RETURNING *", (status, registrant_id))
    
    row = cur.fetchone()
    
    conn.commit()
    cur.close()
    conn.close()
    updated_registrant = Registrant(**row)

@asynccontextmanager
async def lifespan(app: FastAPI):
    drain_worker
    yield

@app.patch("/registrant/registrant_id/{registrant_id}")
async def update_status(registrant_id: int, status_update: StatusUpdate):
    status = status_update.current_status 
    add_to_buffer(registrant_id, status)
    return {"status": "queued", "registrant_id": registrant_id}
  
drain_worker()

