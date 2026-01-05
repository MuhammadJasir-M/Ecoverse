import numpy as np
import pandas as pd
from typing import Dict, List, Tuple
from app.db.models import Bid, Vendor, Tender

class AIEngine:
    """
    AI-powered tender recommendation and anomaly detection
    Inspired by fraud detection techniques from credit card fraud dataset
    """
    
    @staticmethod
    def score_bid(bid: Bid, tender: Tender, vendor: Vendor, all_bids: List[Bid]) -> Dict:
        """
        Score a bid based on multiple factors
        Returns: {ai_score, price_score, vendor_score, technical_score, anomaly_flag, anomaly_reason}
        """
        
        # 1. Price Scoring (normalized inverse - lower is better)
        bid_prices = [b.proposed_price for b in all_bids]
        if len(bid_prices) > 1:
            price_deviation = (bid.proposed_price - np.mean(bid_prices)) / np.std(bid_prices) if np.std(bid_prices) > 0 else 0
            price_score = max(0, 100 - abs(price_deviation) * 20)
        else:
            price_ratio = bid.proposed_price / tender.budget
            price_score = 100 if price_ratio < 0.8 else (100 - (price_ratio - 0.8) * 200)
        
        # 2. Vendor Reputation Score
        vendor_score = min(100, vendor.reputation_score * 20)  # Assuming reputation is 0-5
        if vendor.completed_projects > 0:
            vendor_score += min(20, vendor.completed_projects * 2)
        
        # 3. Technical Score (based on proposal length and delivery timeline)
        proposal_length_score = min(100, len(bid.technical_proposal) / 10)
        timeline_score = 100 - min(100, (bid.delivery_timeline / 365) * 50)
        technical_score = (proposal_length_score * 0.6 + timeline_score * 0.4)
        
        # 4. Anomaly Detection
        anomaly_flag = False
        anomaly_reasons = []
        
        # Check for suspiciously low price (potential dumping)
        if price_deviation < -2.5:
            anomaly_flag = True
            anomaly_reasons.append("Suspiciously low bid price (>2.5 std below mean)")
        
        # Check for exact price matching (possible collusion)
        exact_matches = sum(1 for b in all_bids if b.id != bid.id and abs(b.proposed_price - bid.proposed_price) < 0.01)
        if exact_matches > 0:
            anomaly_flag = True
            anomaly_reasons.append(f"Exact price match with {exact_matches} other bid(s)")
        
        # Check vendor concentration (same vendor winning too often)
        if vendor.total_wins > 10 and vendor.completed_projects > 0:
            win_rate = vendor.total_wins / vendor.completed_projects
            if win_rate > 0.7:
                anomaly_flag = True
                anomaly_reasons.append(f"High win rate vendor ({win_rate:.1%})")
        
        # Check for unrealistic delivery timeline
        if bid.delivery_timeline < 7:
            anomaly_flag = True
            anomaly_reasons.append("Unrealistically short delivery timeline (<7 days)")
        
        # 5. Calculate Final AI Score (weighted average)
        weights = {
            'price': 0.35,
            'vendor': 0.30,
            'technical': 0.25,
            'risk': 0.10
        }
        
        risk_penalty = 30 if anomaly_flag else 0
        
        ai_score = (
            price_score * weights['price'] +
            vendor_score * weights['vendor'] +
            technical_score * weights['technical'] -
            risk_penalty * weights['risk']
        )
        
        return {
            "ai_score": round(max(0, min(100, ai_score)), 2),
            "price_score": round(price_score, 2),
            "vendor_score": round(vendor_score, 2),
            "technical_score": round(technical_score, 2),
            "anomaly_flag": anomaly_flag,
            "anomaly_reason": "; ".join(anomaly_reasons) if anomaly_reasons else None
        }
    
    @staticmethod
    def get_recommendations(tender_id: int, bids: List[Bid], vendors: Dict[int, Vendor], tender: Tender) -> List[Dict]:
        """
        Get ranked recommendations for all bids
        """
        recommendations = []
        
        for bid in bids:
            vendor = vendors.get(bid.vendor_id)
            if not vendor:
                continue
            
            scores = AIEngine.score_bid(bid, tender, vendor, bids)
            
            recommendations.append({
                "bid_id": bid.id,
                "vendor_name": vendor.name,
                "vendor_id": vendor.id,
                "proposed_price": bid.proposed_price,
                "delivery_timeline": bid.delivery_timeline,
                **scores,
                "recommendation": "High" if scores["ai_score"] > 75 else "Medium" if scores["ai_score"] > 50 else "Low"
            })
        
        # Sort by AI score descending
        recommendations.sort(key=lambda x: x["ai_score"], reverse=True)
        
        return recommendations
