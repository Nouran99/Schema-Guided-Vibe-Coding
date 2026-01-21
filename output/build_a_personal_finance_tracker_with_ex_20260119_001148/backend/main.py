from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from datetime import date
from typing import List, Optional
from pydantic import BaseModel

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class Category(BaseModel):
    id: int
    name: str
    budget: float

class Transaction(BaseModel):
    id: int
    amount: float
    type: str
    category_id: int
    date: date
    description: str

categories_db = {}
transactions_db = {}
next_cat_id = 1
next_txn_id = 1

@app.get("/api/categories", response_model=List[Category])
def get_categories():
    return list(categories_db.values())

@app.post("/api/categories", response_model=Category)
def create_category(category: Category):
    global next_cat_id
    category.id = next_cat_id
    categories_db[next_cat_id] = category
    next_cat_id += 1
    return category

@app.put("/api/categories/{id}", response_model=Category)
def update_category(id: int, budget: float):
    if id not in categories_db:
        raise HTTPException(status_code=404, detail="Category not found")
    categories_db[id].budget = budget
    return categories_db[id]

@app.get("/api/transactions", response_model=List[Transaction])
def get_transactions(start_date: Optional[date] = None, end_date: Optional[date] = None):
    txn_list = list(transactions_db.values())
    if start_date:
        txn_list = [t for t in txn_list if t.date >= start_date]
    if end_date:
        txn_list = [t for t in txn_list if t.date <= end_date]
    return txn_list

@app.post("/api/transactions", response_model=Transaction)
def create_transaction(transaction: Transaction):
    global next_txn_id
    transaction.id = next_txn_id
    transactions_db[next_txn_id] = transaction
    next_txn_id += 1
    return transaction

@app.put("/api/transactions/{id}", response_model=Transaction)
def update_transaction(id: int, transaction: Transaction):
    if id not in transactions_db:
        raise HTTPException(status_code=404, detail="Transaction not found")
    transaction.id = id
    transactions_db[id] = transaction
    return transaction

@app.delete("/api/transactions/{id}")
def delete_transaction(id: int):
    if id not in transactions_db:
        raise HTTPException(status_code=404, detail="Transaction not found")
    del transactions_db[id]
    return {"message": "Transaction deleted"}

@app.get("/api/budget-progress")
def get_budget_progress():
    progress = []
    for cat_id, cat in categories_db.items():
        spent = sum(t.amount for t in transactions_db.values() if t.category_id == cat_id and t.type == "expense")
        progress.append({"category_id": cat_id, "category_name": cat.name, "budget": cat.budget, "spent": spent})
    return progress