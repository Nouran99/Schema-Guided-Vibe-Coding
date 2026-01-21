from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

products_db = {}
suppliers_db = {}
stock_movements_db = {}

class Product(BaseModel):
    name: str
    description: str = ""
    unit_price: float
    low_stock_threshold: int = 10
    primary_supplier_id: Optional[int] = None

class Supplier(BaseModel):
    name: str
    contact_info: str = ""

class StockMovement(BaseModel):
    product_id: int
    movement_type: str
    quantity: int
    supplier_id: Optional[int] = None
    notes: str = ""

def calculate_stock(product_id: int) -> int:
    movements = [m for m in stock_movements_db.values() if m["product_id"] == product_id]
    stock = 0
    for m in movements:
        if m["movement_type"] == "purchase":
            stock += m["quantity"]
        else:
            stock -= m["quantity"]
    return stock

def check_low_stock(product_id: int) -> bool:
    if product_id not in products_db:
        return False
    stock = calculate_stock(product_id)
    threshold = products_db[product_id]["low_stock_threshold"]
    return stock <= threshold

@app.get("/api/products")
def get_products(name: Optional[str] = None, supplier_id: Optional[int] = None, low_stock: Optional[bool] = None):
    products = list(products_db.values())
    for p in products:
        p["current_stock"] = calculate_stock(p["id"])
        p["low_stock_alert"] = check_low_stock(p["id"])
    if name:
        products = [p for p in products if name.lower() in p["name"].lower()]
    if supplier_id:
        products = [p for p in products if p["primary_supplier_id"] == supplier_id]
    if low_stock is not None:
        products = [p for p in products if p["low_stock_alert"] == low_stock]
    return products

@app.get("/api/products/{product_id}/stock")
def get_product_stock(product_id: int):
    if product_id not in products_db:
        raise HTTPException(status_code=404, detail="Product not found")
    stock = calculate_stock(product_id)
    is_low = check_low_stock(product_id)
    return {"product_id": product_id, "current_stock": stock, "low_stock_alert": is_low}

@app.post("/api/products")
def create_product(product: Product):
    product_id = len(products_db) + 1
    now = datetime.now().isoformat()
    product_data = {
        "id": product_id,
        **product.dict(),
        "created_at": now,
        "updated_at": now
    }
    products_db[product_id] = product_data
    return product_data

@app.put("/api/products/{product_id}")
def update_product(product_id: int, product: Product):
    if product_id not in products_db:
        raise HTTPException(status_code=404, detail="Product not found")
    now = datetime.now().isoformat()
    products_db[product_id].update({
        **product.dict(),
        "updated_at": now
    })
    return products_db[product_id]

@app.delete("/api/products/{product_id}")
def delete_product(product_id: int):
    if product_id not in products_db:
        raise HTTPException(status_code=404, detail="Product not found")
    del products_db[product_id]
    return {"message": "Product deleted"}

@app.get("/api/suppliers")
def get_suppliers():
    return list(suppliers_db.values())

@app.post("/api/suppliers")
def create_supplier(supplier: Supplier):
    supplier_id = len(suppliers_db) + 1
    now = datetime.now().isoformat()
    supplier_data = {
        "id": supplier_id,
        **supplier.dict(),
        "created_at": now
    }
    suppliers_db[supplier_id] = supplier_data
    return supplier_data

@app.get("/api/stock_movements")
def get_stock_movements(product_id: Optional[int] = None):
    movements = list(stock_movements_db.values())
    if product_id:
        movements = [m for m in movements if m["product_id"] == product_id]
    return movements

@app.post("/api/stock_movements")
def create_stock_movement(movement: StockMovement):
    if movement.product_id not in products_db:
        raise HTTPException(status_code=404, detail="Product not found")
    if movement.supplier_id and movement.supplier_id not in suppliers_db:
        raise HTTPException(status_code=404, detail="Supplier not found")
    if movement.quantity <= 0:
        raise HTTPException(status_code=400, detail="Quantity must be positive")
    movement_id = len(stock_movements_db) + 1
    now = datetime.now().isoformat()
    movement_data = {
        "id": movement_id,
        **movement.dict(),
        "created_at": now
    }
    stock_movements_db[movement_id] = movement_data
    
    is_low = check_low_stock(movement.product_id)
    if is_low:
        movement_data["low_stock_alert"] = True
    
    return movement_data

@app.get("/api/inventory_valuation")
def get_inventory_valuation():
    valuation = 0.0
    for product in products_db.values():
        stock = calculate_stock(product["id"])
        valuation += stock * product["unit_price"]
    return {"total_valuation": valuation}