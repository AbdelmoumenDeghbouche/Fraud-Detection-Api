import pandas as pd
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from datetime import datetime

app = FastAPI()

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
    if distance < 100:
        return "nearby"
    elif distance < 300:
        return "moderate"
    else:
        return "far"
def categorize_population(population):
    if population > 100:
        return "Highly"
    elif 50 <= population <= 100:
        return "Moderately"
    else:
        return "Sparsely"
def categorize_amount(amount):
    if amount > 2000:
        return "Highly"
    elif 1000 <= amount <= 2000:
        return "Moderately"
    else:
        return "Sparsely"
def categorize_age(age):
    if age >= 50:
        return "old"
    elif 30 <= age < 50:
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
# Fraud Detection End-Point
@app.post("/detect/")
async def detect(transaction: Transaction):
    transactionNormalized=normalizeInput(transaction)
    for _, rule in rules.iterrows():
        if all(pd.isna(v) or transactionNormalized[k] == v for k, v in rule.items()):
            return {"result": "🚨 Fraud Alert! 🚨 Whoa there, Sherlock! We just caught a sneaky attempt at mischief.🕵️‍♂️💼"}

    return {"result": "🌟 Your transactions are as clean as a whistle.🎩💸"}