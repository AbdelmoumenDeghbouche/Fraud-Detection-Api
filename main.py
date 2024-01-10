import pandas as pd
from fastapi import FastAPI, Request,HTTPException
from pydantic import BaseModel
from datetime import datetime
from fastapi import FastAPI, Depends, HTTPException
from fastapi.openapi.models import OAuthFlows as OAuthFlowsModel
from fastapi.openapi.models import OAuthFlowAuthorizationCode
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
import httpx

load_dotenv()

app = FastAPI()
if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="localhost", port=8000)
    origins = [
    "http://localhost:3000",  
]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],  
    allow_headers=["*"],  
)
# Load rules from the CSV file using pandas
rules = pd.read_csv('rules_simple.csv')
# Transaction Model
class Transaction(BaseModel):
    distance:int
    age: int
    gender:str
    category: str 
    amount: int
    population: int
    def to_dict(self):
        return dict(self.__dict__)
# Input Normalization Methods
def get_time_period():
    current_time = datetime.now().time()
    if current_time.hour < 12:
        return "Forenoon"
    elif current_time.hour < 17:
        return "Afternoon"
    else:
        return "Evening"
def categorize_distance(distance):
    if distance < 39.51458312511411:
        return "nearby"
    elif distance < 56.4090045083898:
        return "moderate"
    else:
        return "far"
def categorize_population(population):
    if population > 5.640328239467187:
        return "Highly"
    elif 4.910818713222447 <= population <=  5.640328239467187:
        return "Moderately"
    else:
        return "Sparsely"
def categorize_amount(amount):
    if amount > 5.679355014609812:
        return "Highly"
    elif 3.702776454030607 <= amount <= 5.679355014609812:
        return "Moderately"
    else:
        return "Sparsely"
def categorize_age(age):
    if age >= 56:
        return "old"
    elif 40.0 <= age < 56:
        return "middle"
    else:
        return "young"

def normalizeInput(transaction:Transaction):
    noramlizedInput=transaction.to_dict()
    noramlizedInput['transaction']=get_time_period()
    noramlizedInput['age']=categorize_age(noramlizedInput['age'])
    noramlizedInput['amount']=categorize_amount(noramlizedInput['amount'])
    noramlizedInput['population']=categorize_population(noramlizedInput['population'])
    noramlizedInput['distance']=categorize_distance(noramlizedInput['distance'])
    return noramlizedInput
# Getting User Location 
async def get_client_ip(request: Request):
    return request.client.host

async def get_user_location(ip: str = Depends(get_client_ip)):
    async with httpx.AsyncClient() as client:
        response = await client.get(f"https://ipinfo.io/{ip}/json")
        if response.status_code == 200:
            data = response.json()
            return data
        else:
            raise HTTPException(status_code=response.status_code, detail="Failed to fetch location")

# Fraud Detection End-Point
@app.post("/detect/")
async def detect(transaction: Transaction,location: dict = Depends(get_user_location)):
    transactionNormalized=normalizeInput(transaction)
    for _, rule in rules.iterrows():
        if all(pd.isna(v) or transactionNormalized[k] == v for k, v in rule.items()):
            return {"result": "🚨 Fraud Alert! 🚨 Whoa there, Sherlock! We just caught a sneaky attempt at mischief.🕵️‍♂️💼"+location}

    return {"result": "🌟 Your transactions are as clean as a whistle.🎩💸"}