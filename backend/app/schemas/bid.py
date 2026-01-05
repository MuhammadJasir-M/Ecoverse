from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional

class BidCreate(BaseModel):
    tender_id: int
    vendor_id: int
    proposed_price: float = Field(..., gt=0)
    technical_proposal: str = Field(..., min_length=100)
    delivery_timeline: int = Field(..., gt=0)

class BidResponse(BaseModel):
    id: int
    tender_id: int
    vendor_id: int
    proposed_price: float
    technical_proposal: str
    delivery_timeline: int
    status: str
    ai_score: Optional[float]
    anomaly_flag: bool
    anomaly_reason: Optional[str]
    created_at: datetime
    
    class Config:
        from_attributes = True

class BidWithVendor(BidResponse):
    vendor_name: str
    vendor_reputation: float
