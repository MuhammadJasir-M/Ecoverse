from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional

class TenderCreate(BaseModel):
    title: str = Field(..., min_length=10, max_length=500)
    description: str = Field(..., min_length=50)
    category: str
    budget: float = Field(..., gt=0)
    department: str
    deadline: datetime

class TenderResponse(BaseModel):
    id: int
    title: str
    description: str
    category: str
    budget: float
    department: str
    deadline: datetime
    status: str
    creation_hash: Optional[str]
    creation_tx_hash: Optional[str]
    created_at: datetime
    
    class Config:
        from_attributes = True
