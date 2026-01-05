from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from datetime import datetime
from app.db.session import get_db
from app.db.models import Tender, Bid, Vendor, TenderStatus
from app.schemas.bid import BidCreate, BidResponse
from app.schemas.tender import TenderResponse
from app.services.hash_utils import generate_bid_hash
from app.services.blockchain import BlockchainService
from app.services.auth import require_vendor, get_password_hash

router = APIRouter(prefix="/vendor", tags=["Vendor"])

blockchain_service = BlockchainService()

@router.post("/register")
def register_vendor(
    name: str,
    email: str,
    company_registration: str,
    phone: str = None,
    address: str = None,
    db: Session = Depends(get_db)
):
    """Register a new vendor (legacy endpoint - use /auth/vendor/register for new registrations)"""
    
    # Check if vendor exists
    existing = db.query(Vendor).filter(Vendor.email == email).first()
    if existing:
        raise HTTPException(status_code=400, detail="Vendor with this email already exists")
    
    vendor = Vendor(
        name=name,
        email=email,
        company_registration=company_registration,
        phone=phone,
        address=address,
        reputation_score=3.0  # Starting reputation
    )
    db.add(vendor)
    db.commit()
    db.refresh(vendor)
    
    return {"id": vendor.id, "name": vendor.name, "message": "Vendor registered successfully. Please set up authentication via /auth/vendor/register"}

@router.get("/tenders/open", response_model=List[TenderResponse])
def get_open_tenders(
    db: Session = Depends(get_db),
    current_user: dict = Depends(require_vendor)
):
    """Get all open tenders"""
    return db.query(Tender).filter(
        Tender.status == TenderStatus.OPEN,
        Tender.deadline > datetime.utcnow()
    ).all()

@router.post("/bids", response_model=BidResponse)
def submit_bid(
    bid: BidCreate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(require_vendor)
):
    """Submit a bid for a tender"""
    
    # Validate tender
    tender = db.query(Tender).filter(Tender.id == bid.tender_id).first()
    if not tender:
        raise HTTPException(status_code=404, detail="Tender not found")
    
    if tender.status != TenderStatus.OPEN:
        raise HTTPException(status_code=400, detail="Tender is not open for bidding")
    
    if tender.deadline < datetime.utcnow():
        raise HTTPException(status_code=400, detail="Tender deadline has passed")
    
    # Validate vendor and ensure they match the authenticated user
    vendor = db.query(Vendor).filter(Vendor.id == bid.vendor_id).first()
    if not vendor:
        raise HTTPException(status_code=404, detail="Vendor not found")
    
    # Ensure vendor can only submit bids for themselves
    if current_user["id"] != bid.vendor_id:
        raise HTTPException(status_code=403, detail="You can only submit bids for your own account")
    
    # Check for duplicate bid
    existing_bid = db.query(Bid).filter(
        Bid.tender_id == bid.tender_id,
        Bid.vendor_id == bid.vendor_id
    ).first()
    if existing_bid:
        raise HTTPException(status_code=400, detail="Vendor has already submitted a bid for this tender")
    
    # Generate hash
    bid_hash = generate_bid_hash(bid.dict())
    
    # Create bid
    db_bid = Bid(
        **bid.dict(),
        submission_hash=bid_hash
    )
    db.add(db_bid)
    db.commit()
    db.refresh(db_bid)
    
    # Log on blockchain
    try:
        tx_hash = blockchain_service.log_bid_submission(
            db_bid.id,
            tender.id,
            bid_hash
        )
        if tx_hash:
            db_bid.submission_tx_hash = tx_hash
            db.commit()
    except Exception as e:
        print(f"Blockchain logging failed: {e}")
    
    return db_bid

@router.get("/bids/{vendor_id}")
def get_vendor_bids(
    vendor_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(require_vendor)
):
    """Get all bids submitted by a vendor"""
    # Ensure vendor can only see their own bids
    if current_user["id"] != vendor_id:
        raise HTTPException(status_code=403, detail="Access denied")
    
    bids = db.query(Bid).filter(Bid.vendor_id == vendor_id).all()
    
    results = []
    for bid in bids:
        tender = db.query(Tender).filter(Tender.id == bid.tender_id).first()
        results.append({
            "bid_id": bid.id,
            "tender_title": tender.title if tender else "Unknown",
            "proposed_price": bid.proposed_price,
            "status": bid.status,
            "ai_score": bid.ai_score,
            "submitted_at": bid.created_at
        })
    
    return results
