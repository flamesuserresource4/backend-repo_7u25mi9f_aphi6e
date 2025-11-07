from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import List, Dict, Any

app = FastAPI(title="FRESH PICK API")

# Allow frontend dev server
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Simple in-memory product catalog for billing calculations
# In a real app, replace with database collections.
PRODUCT_PRICES: Dict[str, float] = {
    "P-2001": 1.80,  # Gala Apples
    "P-2002": 2.90,  # Whole Milk 1L
    "P-2003": 1.20,  # Brown Bread
    "P-2004": 3.50,  # Free-range Eggs
    "P-1999": 1.50,  # Yogurt Cup
}

class BillingItem(BaseModel):
    product_id: str
    quantity: int = Field(ge=1)

class BillingRequest(BaseModel):
    items: List[BillingItem]

class BillingLine(BaseModel):
    product_id: str
    quantity: int
    unit_price: float
    line_total: float

class BillingResponse(BaseModel):
    lines: List[BillingLine]
    total: float

@app.get("/test")
def test() -> Dict[str, Any]:
    return {"status": "ok", "message": "API running"}

@app.post("/billing/price", response_model=BillingResponse)
def price_bill(payload: BillingRequest) -> BillingResponse:
    lines: List[BillingLine] = []
    total = 0.0
    for item in payload.items:
        price = PRODUCT_PRICES.get(item.product_id, 0.0)
        line_total = round(price * item.quantity, 2)
        total += line_total
        lines.append(BillingLine(
            product_id=item.product_id,
            quantity=item.quantity,
            unit_price=price,
            line_total=line_total,
        ))
    return BillingResponse(lines=lines, total=round(total, 2))
