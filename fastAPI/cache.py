import redis
from dotenv import load_dotenv
import os
import json
import asyncio

load_dotenv()   
REDIS_HOST = os.getenv("REDIS_HOST")
r = redis.Redis(host=REDIS_HOST, port=6379, decode_responses=True)

def add_to_buffer(registrant_id: int, status: str):
    data = {"registrant_id": registrant_id, "status": status}
    json_data = json.dumps(data)
    r.lpush("status_update_que",json_data)

    
async def drain_worker(write_function):
    while True:
      queue_item = r.rpop("status_update_que")
      if queue_item is None:
          continue
      status_change_item = json.loads(queue_item)
      write_function(status_change_item["registrant_id"], status_change_item["status"]) 
      await asyncio.sleep(0.5)
    # test