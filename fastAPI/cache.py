import redis
from dotenv import load_dotenv
import os
import json

load_dotenv()   

REDIS_HOST = os.getenv("REDIS_HOST")

r = redis.Redis(host=REDIS_HOST, port=6379, decode_responses=True)
result = r.ping()
print(result)

def add_to_buffer(registrant_id, status):
    data = {"registrant_id": registrant_id, "status": status}
    json_data = json.dumps(data)
    
    r.lpush( "status_update_que",json_data)

    
    
     