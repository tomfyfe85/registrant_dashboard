import redis
from dotenv import load_dotenv
import os

load_dotenv()   

REDIS_HOST = os.getenv("REDIS_HOST")

r = redis.Redis(host=REDIS_HOST, port=6379, decode_responses=True)
result = r.ping()
print(result)
