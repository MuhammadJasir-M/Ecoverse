from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from app.db.session import get_db
from app.db.models import Tender, Award, Bid, Vendor, PublicRating, TenderStatus
from app.schemas.award import PublicRatingCreate
from app.services.blockchain import BlockchainService

router = APIRouter(prefix="/public", tags=["Public Transparency"])

blockchain_service = BlockchainService()

@router.get("/tenders/awarded")
def get_awarded_tenders(db: Session = Depends(get_db)):
    """Get all awarded tenders for public viewing"""
    tenders = db.query(Tender).filter(Tender.status == TenderStatus.AWARDED).all()
    
    results = []
    for tender in tenders:
        award = db.query(Award).filter(Award.tender_id == tender.id).first()
        if award:
            winning_bid = db.query(Bid).filter(Bid.id == award.winning_bid_id).first()
            vendor = db.query(Vendor).filter(Vendor.id == winning_bid.vendor_id).first() if winning_bid else None
            
            results.append({
                "tender_id": tender.id,
                "title": tender.title,
                "category": tender.category,
                "budget": tender.budget,
                "department": tender.department,
                "winner": vendor.name if vendor else "Unknown",
                "award_amount": award.award_amount,
                "contract_start": award.contract_start,
                "contract_end": award.contract_end,
                "justification": award.justification,
                "public_rating": award.public_rating,
                "feedback_count": award.public_feedback_count,
                "creation_tx": tender.creation_tx_hash,
                "award_tx": tender.award_tx_hash
            })
    
    return results

@router.get("/tenders/{tender_id}/transparency")
def get_tender_transparency(tender_id: int, db: Session = Depends(get_db)):
    """Get complete transparency view for a tender"""
    tender = db.query(Tender).filter(Tender.id == tender_id).first()
    if not tender:
        raise HTTPException(status_code=404, detail="Tender not found")
    
    if tender.status != TenderStatus.AWARDED:
        raise HTTPException(status_code=400, detail="Tender not yet awarded - transparency not available")
    
    # Get all bids
    bids = db.query(Bid).filter(Bid.tender_id == tender_id).all()
    
    bid_details = []
    for bid in bids:
        vendor = db.query(Vendor).filter(Vendor.id == bid.vendor_id).first()
        bid_details.append({
            "vendor_name": vendor.name if vendor else "Unknown",
            "proposed_price": bid.proposed_price,
            "delivery_timeline": bid.delivery_timeline,
            "ai_score": bid.ai_score,
            "anomaly_flag": bid.anomaly_flag,
            "status": bid.status
        })
    
    # Get award
    award = db.query(Award).filter(Award.tender_id == tender_id).first()
    
    # Verify blockchain
    blockchain_verification = blockchain_service.verify_audit_trail(tender_id)
    
    return {
        "tender": {
            "id": tender.id,
            "title": tender.title,
            "budget": tender.budget,
            "department": tender.department
        },
        "all_bids": bid_details,
        "award": {
            "winning_amount": award.award_amount if award else None,
            "justification": award.justification if award else None
        },
        "blockchain_proof": blockchain_verification,
        "public_rating": award.public_rating if award else None
    }

@router.post("/ratings")
def submit_public_rating(rating: PublicRatingCreate, db: Session = Depends(get_db)):
    """Public submits rating for completed project"""
    
    award = db.query(Award).filter(Award.id == rating.award_id).first()
    if not award:
        raise HTTPException(status_code=404, detail="Award not found")
    
    # Create rating
    db_rating = PublicRating(**rating.dict())
    db.add(db_rating)
    
    # Update award average rating
    all_ratings = db.query(PublicRating).filter(PublicRating.award_id == rating.award_id).all()
    total_ratings = len(all_ratings) + 1
    new_avg = (sum(r.rating for r in all_ratings) + rating.rating) / total_ratings
    
    award.public_rating = round(new_avg, 2)
    award.public_feedback_count = total_ratings
    
    # Update vendor reputation
    winning_bid = db.query(Bid).filter(Bid.id == award.winning_bid_id).first()
    if winning_bid:
        vendor = db.query(Vendor).filter(Vendor.id == winning_bid.vendor_id).first()
        if vendor:
            vendor.completed_projects += 1
            vendor.average_rating = ((vendor.average_rating * (vendor.completed_projects - 1)) + rating.rating) / vendor.completed_projects
            vendor.reputation_score = vendor.average_rating
    
    db.commit()
    
    return {"message": "Rating submitted successfully"}
