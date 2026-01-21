from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from datetime import datetime
from typing import List, Optional
import uuid

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

calculations = {}

class CalculationRequest(BaseModel):
    operand1: float
    operand2: float
    operation: str

class CalculationResponse(BaseModel):
    id: str
    operand1: float
    operand2: float
    operation: str
    result: float
    created_at: datetime

@app.post("/api/calculate", response_model=CalculationResponse)
def calculate(request: CalculationRequest):
    if request.operation == "add":
        result = request.operand1 + request.operand2
    elif request.operation == "subtract":
        result = request.operand1 - request.operand2
    elif request.operation == "multiply":
        result = request.operand1 * request.operand2
    elif request.operation == "divide":
        if request.operand2 == 0:
            raise HTTPException(status_code=400, detail="Division by zero")
        result = request.operand1 / request.operand2
    else:
        raise HTTPException(status_code=400, detail="Invalid operation")
    
    calc_id = str(uuid.uuid4())
    calc = CalculationResponse(
        id=calc_id,
        operand1=request.operand1,
        operand2=request.operand2,
        operation=request.operation,
        result=result,
        created_at=datetime.now()
    )
    calculations[calc_id] = calc
    return calc

@app.get("/api/calculations", response_model=List[CalculationResponse])
def get_calculations():
    return list(calculations.values())

@app.get("/api/calculations/{id}", response_model=CalculationResponse)
def get_calculation(id: str):
    if id not in calculations:
        raise HTTPException(status_code=404, detail="Calculation not found")
    return calculations[id]

@app.delete("/api/calculations/{id}")
def delete_calculation(id: str):
    if id not in calculations:
        raise HTTPException(status_code=404, detail="Calculation not found")
    del calculations[id]
    return {"message": "Calculation deleted"}

@app.delete("/api/calculations")
def clear_calculations():
    calculations.clear()
    return {"message": "All calculations cleared"}
