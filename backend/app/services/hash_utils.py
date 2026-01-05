import hashlib
import json
from datetime import datetime

def generate_tender_hash(tender_data: dict) -> str:
    """Generate SHA-256 hash for tender creation"""
    hash_input = json.dumps({
        "title": tender_data["title"],
        "budget": tender_data["budget"],
        "deadline": str(tender_data["deadline"]),
        "timestamp": datetime.utcnow().isoformat()
    }, sort_keys=True)
    # Return as 0x-prefixed hex string (66 chars total) for Solidity bytes32
    return "0x" + hashlib.sha256(hash_input.encode()).hexdigest()

def generate_bid_hash(bid_data: dict) -> str:
    """Generate SHA-256 hash for bid submission"""
    hash_input = json.dumps({
        "tender_id": bid_data["tender_id"],
        "vendor_id": bid_data["vendor_id"],
        "proposed_price": bid_data["proposed_price"],
        "timestamp": datetime.utcnow().isoformat()
    }, sort_keys=True)
    return "0x" + hashlib.sha256(hash_input.encode()).hexdigest()

def generate_award_hash(award_data: dict) -> str:
    """Generate SHA-256 hash for award decision"""
    hash_input = json.dumps({
        "tender_id": award_data["tender_id"],
        "winning_bid_id": award_data["winning_bid_id"],
        "award_amount": award_data["award_amount"],
        "timestamp": datetime.utcnow().isoformat()
    }, sort_keys=True)
    return "0x" + hashlib.sha256(hash_input.encode()).hexdigest()
