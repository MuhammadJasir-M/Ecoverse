from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional

class AwardCreate(BaseModel):
    tender_id: int
    winning_bid_id: int
    justification: str = Field(..., min_length=50)
    contract_start: datetime
    contract_end: datetime

class AwardResponse(BaseModel):
    id: int
    tender_id: int
    winning_bid_id: int
    justification: str
    award_amount: float
    public_rating: Optional[float]
    public_feedback_count: int
    created_at: datetime
    
    class Config:
        from_attributes = True

class PublicRatingCreate(BaseModel):
    award_id: int
    rating: int = Field(..., ge=1, le=5)
    feedback: Optional[str] = None
    citizen_name: Optional[str] = None
