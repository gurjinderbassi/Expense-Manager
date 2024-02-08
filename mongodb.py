
from pymongo.mongo_client import MongoClient
import os
from dotenv import load_dotenv

load_dotenv(".env")
uri = os.getenv("uri")

# Create a new client and connect to the server
client = MongoClient(uri)

# Send a ping to confirm a successful connection
try:
    client.admin.command('ping')
    print("Pinged your deployment. You successfully connected to MongoDB!")
except Exception as e:
    print(e)

# write data to MongoDB
def insert_period(period, incomes, expenses, comment):
    db = client["budget_app"]
    collection = db["periods"]
    data = {
        "key": period,
        "incomes": incomes,
        "expenses": expenses,
        "comment": comment
    }
    collection.insert_one(data)

# fetch all periods from MongoDB
def fetch_all_periods():
    db = client["budget_app"]
    collection = db["periods"]
    return collection.find()

# get period from MongoDB
def get_period(period):
    db = client["budget_app"]
    collection = db["periods"]
    return collection.find_one({"key": period})