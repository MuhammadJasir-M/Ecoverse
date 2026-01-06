from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from app.db.session import get_db
from app.db.models import Tender, Bid, Award, Vendor, TenderStatus, BidStatus
from app.schemas.tender import TenderCreate, TenderResponse
from app.schemas.award import AwardCreate, AwardResponse
from app.services.hash_utils import generate_tender_hash, generate_award_hash
from app.services.blockchain import BlockchainService
from app.services.ai_engine import AIEngine
from app.services.auth import require_government
from datetime import datetime

router = APIRouter(prefix="/gov", tags=["Government"])

blockchain_service = BlockchainService()

@router.post("/tenders", response_model=TenderResponse)
def create_tender(
    tender: TenderCreate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(require_government)
):
    """Government creates a new tender"""
    
    # Generate hash
    tender_hash = generate_tender_hash(tender.dict())
    
    # Create tender in DB
    db_tender = Tender(
        **tender.dict(),
        status=TenderStatus.OPEN,
        creation_hash=tender_hash
    )
    db.add(db_tender)
    db.commit()
    db.refresh(db_tender)
    
    # Log on blockchain
    try:
        tx_hash = blockchain_service.log_tender_creation(db_tender.id, tender_hash)
        if tx_hash:
            db_tender.creation_tx_hash = tx_hash
            db.commit()
    except Exception as e:
        print(f"Blockchain logging failed: {e}")
    
    return db_tender

@router.get("/tenders", response_model=List[TenderResponse])
def list_tenders(
    db: Session = Depends(get_db),
    current_user: dict = Depends(require_government)
):
    """List all tenders"""
    return db.query(Tender).all()

@router.get("/tenders/{tender_id}/bids")
def get_tender_bids(
    tender_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(require_government)
):
    """Get all bids for a tender with details"""
    tender = db.query(Tender).filter(Tender.id == tender_id).first()
    if not tender:
        raise HTTPException(status_code=404, detail="Tender not found")
    
    bids = db.query(Bid).filter(Bid.tender_id == tender_id).all()
    
    results = []
    for bid in bids:
        vendor = db.query(Vendor).filter(Vendor.id == bid.vendor_id).first()
        results.append({
            "id": bid.id,
            "vendor_name": vendor.name if vendor else "Unknown",
            "vendor_reputation": vendor.reputation_score if vendor else 0,
            "proposed_price": bid.proposed_price,
            "delivery_timeline": bid.delivery_timeline,
            "ai_score": bid.ai_score,
            "anomaly_flag": bid.anomaly_flag,
            "status": bid.status
        })
    
    return results

@router.post("/tenders/{tender_id}/close")
def close_tender(
    tender_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(require_government)
):
    """Close bidding for a tender"""
    tender = db.query(Tender).filter(Tender.id == tender_id).first()
    if not tender:
        raise HTTPException(status_code=404, detail="Tender not found")
    
    tender.status = TenderStatus.CLOSED
    db.commit()
    
    return {"message": "Tender closed successfully"}

@router.get("/tenders/{tender_id}/recommendations")
def get_ai_recommendations(
    tender_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(require_government)
):
    """Get AI-powered bid recommendations"""
    try:
        tender = db.query(Tender).filter(Tender.id == tender_id).first()
        if not tender:
            raise HTTPException(status_code=404, detail="Tender not found")
        
        bids = db.query(Bid).filter(Bid.tender_id == tender_id).all()
        if not bids:
            return {
                "recommendations": [], 
                "message": "No bids submitted yet",
                "total_bids": 0
            }
        
        # Get vendors
        vendor_ids = [bid.vendor_id for bid in bids]
        vendors = db.query(Vendor).filter(Vendor.id.in_(vendor_ids)).all()
        vendor_dict = {v.id: v for v in vendors}
        
        # Validate all bids have corresponding vendors
        missing_vendors = [bid.vendor_id for bid in bids if bid.vendor_id not in vendor_dict]
        if missing_vendors:
            print(f"Warning: Missing vendors for IDs: {missing_vendors}")
        
        # Get AI recommendations
        recommendations = AIEngine.get_recommendations(tender_id, bids, vendor_dict, tender)
        
        if not recommendations:
            return {
                "recommendations": [],
                "message": "Unable to generate recommendations. Please check bid data.",
                "total_bids": len(bids)
            }
        
        # Update bid scores in database
        for rec in recommendations:
            try:
                bid = next((b for b in bids if b.id == rec["bid_id"]), None)
                if bid:
                    bid.ai_score = rec["ai_score"]
                    bid.price_score = rec["price_score"]
                    bid.vendor_score = rec["vendor_score"]
                    bid.technical_score = rec["technical_score"]
                    bid.anomaly_flag = rec["anomaly_flag"]
                    bid.anomaly_reason = rec["anomaly_reason"]
            except Exception as e:
                print(f"Error updating bid {rec.get('bid_id')}: {e}")
                continue
        
        db.commit()
        
        return {
            "recommendations": recommendations, 
            "total_bids": len(bids),
            "message": "Recommendations generated successfully"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error in get_ai_recommendations: {str(e)}")
        import traceback
        traceback.print_exc()
        raise HTTPException(
            status_code=500, 
            detail=f"Failed to generate recommendations: {str(e)}"
        )

@router.post("/awards", response_model=AwardResponse)
def create_award(
    award: AwardCreate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(require_government)
):
    """Award tender to winning bid"""
    
    # Validate tender and bid
    tender = db.query(Tender).filter(Tender.id == award.tender_id).first()
    if not tender:
        raise HTTPException(status_code=404, detail="Tender not found")
    
    winning_bid = db.query(Bid).filter(Bid.id == award.winning_bid_id).first()
    if not winning_bid:
        raise HTTPException(status_code=404, detail="Bid not found")
    
    # Create award
    award_data = award.dict()
    award_data['award_amount'] = winning_bid.proposed_price
    
    award_hash = generate_award_hash({
        "tender_id": award.tender_id,
        "winning_bid_id": award.winning_bid_id,
        "award_amount": winning_bid.proposed_price
    })
    
    db_award = Award(**award_data)
    db.add(db_award)
    
    # Update tender status
    tender.status = TenderStatus.AWARDED
    tender.award_hash = award_hash
    
    # Update bid status
    winning_bid.status = BidStatus.ACCEPTED
    
    # Update vendor stats
    vendor = db.query(Vendor).filter(Vendor.id == winning_bid.vendor_id).first()
    if vendor:
        vendor.total_wins += 1
    
    db.commit()
    db.refresh(db_award)
    
    # Log on blockchain
    try:
        tx_hash = blockchain_service.log_award_decision(
            tender.id,
            winning_bid.id,
            award_hash
        )
        if tx_hash:
            tender.award_tx_hash = tx_hash
            db.commit()
    except Exception as e:
        print(f"Blockchain logging failed: {e}")
    
    return db_award
