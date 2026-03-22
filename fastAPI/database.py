from dotenv import load_dotenv
import psycopg2
import os

load_dotenv()

POSTGRES_USER = os.getenv('POSTGRES_USER')
POSTGRES_PASSWORD = os.getenv('POSTGRES_PASSWORD')
POSTGRES_DB = os.getenv('POSTGRES_DB')

def get_db():
    return psycopg2.connect(dbname=POSTGRES_DB, password=POSTGRES_PASSWORD, user=POSTGRES_USER, host="localhost")
 
print(get_db())