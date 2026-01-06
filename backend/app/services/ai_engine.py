import numpy as np
from typing import Dict, List, Optional, Tuple
from app.db.models import Bid, Vendor, Tender
import logging
import re

logger = logging.getLogger(__name__)


class AIEngine:
    """
    Enhanced rule-based AI engine for tender scoring and anomaly detection.
    
    Scoring Logic:
    - Price Score (40%): Based on competitiveness relative to budget and other bids
    - Vendor Score (35%): Based on vendor reputation, completed projects, and ratings
    - Technical Score (25%): Based on proposal quality and delivery timeline
    
    Final AI Score Ranges:
    - 85-100: Excellent (All 3 key conditions met)
    - 60-85:  Good (2 conditions met)
    - 45-70:  Fair (1 condition met)
    - 0-45:   Poor (No conditions met)
    
    Anomalies detected: Suspiciously low prices, collusion indicators, unrealistic timelines
    """

    # Configuration constants
    PRICE_WEIGHT = 0.40
    VENDOR_WEIGHT = 0.35
    TECHNICAL_WEIGHT = 0.25
    
    ANOMALY_PENALTY = 15
    MIN_REASONABLE_TIMELINE = 7  # days
    OPTIMAL_PRICE_RATIO = 0.8    # 80% of budget is considered optimal
    
    @staticmethod
    def _safe_divide(numerator: float, denominator: float, default: float = 0.0) -> float:
        """Safely divide two numbers, returning default if denominator is zero."""
        try:
            return numerator / denominator if denominator != 0 else default
        except (TypeError, ZeroDivisionError):
            return default

    @staticmethod
    def score_bid(bid: Bid, tender: Tender, vendor: Vendor, all_bids: List[Bid]) -> Dict:
        """
        Calculate comprehensive AI score for a bid.
        
        Args:
            bid: The bid to score
            tender: The tender being bid on
            vendor: The vendor submitting the bid
            all_bids: All bids for this tender (for comparative analysis)
            
        Returns:
            Dictionary containing ai_score, component scores, and anomaly information
        """
        try:
            # Extract bid prices for comparative analysis
            bid_prices = [b.proposed_price for b in all_bids if b.proposed_price > 0]
            
            if not bid_prices:
                logger.warning(f"No valid bid prices found for tender {tender.id}")
                bid_prices = [bid.proposed_price]

            # =========================
            # 1. PRICE SCORE (40%)
            # =========================
            price_score = AIEngine._calculate_price_score(
                bid.proposed_price, 
                bid_prices, 
                tender.budget
            )

            # =========================
            # 2. VENDOR SCORE (35%)
            # =========================
            vendor_score = AIEngine._calculate_vendor_score(vendor)

            # =========================
            # 3. TECHNICAL SCORE (25%)
            # =========================
            technical_score = AIEngine._calculate_technical_score(
                bid.technical_proposal,
                bid.delivery_timeline
            )

            # =========================
            # 4. ANOMALY DETECTION
            # =========================
            anomaly_flag, anomaly_reasons, price_deviation = AIEngine._detect_anomalies(
                bid, 
                bid_prices, 
                all_bids
            )

            # =========================
            # 5. CONDITION CHECKS (CORE LOGIC)
            # =========================
            avg_price = np.mean(bid_prices)
            
            # Define success conditions
            low_cost = bid.proposed_price <= avg_price * 0.9  # 10% below average
            reasonable_timeline = bid.delivery_timeline <= 90  # <= 90 days
            good_reputation = vendor.reputation_score >= 3.5 or vendor.total_wins >= 3
            
            conditions_met = sum([low_cost, reasonable_timeline, good_reputation])

            # =========================
            # 6. BASE SCORE CALCULATION
            # =========================
            base_score = (
                price_score * AIEngine.PRICE_WEIGHT +
                vendor_score * AIEngine.VENDOR_WEIGHT +
                technical_score * AIEngine.TECHNICAL_WEIGHT
            )

            # =========================
            # 7. APPLY SCORE RANGES BASED ON CONDITIONS
            # =========================
            ai_score = AIEngine._apply_score_range(base_score, conditions_met)

            # =========================
            # 8. APPLY ANOMALY PENALTY
            # =========================
            if anomaly_flag:
                ai_score = max(0, ai_score - AIEngine.ANOMALY_PENALTY)

            return {
                "ai_score": round(ai_score, 2),
                "price_score": round(price_score, 2),
                "vendor_score": round(vendor_score, 2),
                "technical_score": round(technical_score, 2),
                "anomaly_flag": anomaly_flag,
                "anomaly_reason": "; ".join(anomaly_reasons) if anomaly_reasons else None
            }
            
        except Exception as e:
            logger.error(f"Error scoring bid {bid.id}: {str(e)}")
            # Return safe default scores in case of error
            return {
                "ai_score": 50.0,
                "price_score": 50.0,
                "vendor_score": 50.0,
                "technical_score": 50.0,
                "anomaly_flag": True,
                "anomaly_reason": f"Scoring error: {str(e)}"
            }

    @staticmethod
    def _calculate_price_score(proposed_price: float, all_prices: List[float], budget: float) -> float:
        """
        Calculate price competitiveness score.
        
        Logic:
        - If multiple bids exist, use statistical deviation from mean
        - Otherwise, compare against budget ratio
        """
        if len(all_prices) > 1:
            mean_price = np.mean(all_prices)
            std_price = np.std(all_prices)
            
            if std_price > 0:
                # Z-score approach: penalize prices far from mean
                deviation = (proposed_price - mean_price) / std_price
                # Score decreases as price deviates from mean (in either direction)
                price_score = max(0, 100 - abs(deviation) * 20)
            else:
                # All prices are the same, score based on budget ratio
                price_ratio = AIEngine._safe_divide(proposed_price, budget, 1.0)
                price_score = 100 if price_ratio <= AIEngine.OPTIMAL_PRICE_RATIO else \
                              max(0, 100 - (price_ratio - AIEngine.OPTIMAL_PRICE_RATIO) * 200)
        else:
            # Single bid: score based on budget efficiency
            price_ratio = AIEngine._safe_divide(proposed_price, budget, 1.0)
            if price_ratio <= AIEngine.OPTIMAL_PRICE_RATIO:
                price_score = 100
            elif price_ratio <= 1.0:
                # Between 80% and 100% of budget
                price_score = 100 - ((price_ratio - AIEngine.OPTIMAL_PRICE_RATIO) * 200)
            else:
                # Over budget - penalize heavily
                price_score = max(0, 60 - ((price_ratio - 1.0) * 100))
        
        return max(0, min(100, price_score))

    @staticmethod
    def _calculate_vendor_score(vendor: Vendor) -> float:
        """
        Calculate vendor reputation and experience score.
        
        Factors:
        - Reputation score (if available, 0-5 scale)
        - Average rating (0-5 scale)
        - Total wins (project success history)
        - Completed projects (experience level)
        """
        # Reputation score component (0-5 scale → 0-100)
        reputation_component = min(100, (vendor.reputation_score or 0) * 20)
        
        # Average rating component (0-5 scale → 0-100)
        rating_component = min(100, (vendor.average_rating or 0) * 20)
        
        # Win rate bonus: +10 points per win, max 30
        win_bonus = min(30, (vendor.total_wins or 0) * 10)
        
        # Experience bonus: +5 points per completed project, max 20
        experience_bonus = min(20, (vendor.completed_projects or 0) * 5)
        
        # Combine components
        vendor_score = (
            reputation_component * 0.4 +
            rating_component * 0.4 +
            win_bonus +
            experience_bonus
        )
        
        return max(0, min(100, vendor_score))

    @staticmethod
    def _calculate_technical_score(proposal: str, timeline: int) -> float:
        """
        Calculate technical merit score with NLP-enhanced analysis.
        
        Factors:
        - Proposal completeness and quality
        - Keyword presence (methodology, quality, experience)
        - Timeline reasonableness (faster is better, but not unrealistic)
        """
        proposal_text = (proposal or "").lower()
        proposal_length = len(proposal or "")
        
        # 1. Length-based scoring (optimal: 300-1000 chars)
        if proposal_length < 100:
            length_score = 15
        elif proposal_length < 300:
            length_score = 35
        elif proposal_length <= 1000:
            length_score = 55  # Optimal
        elif proposal_length <= 2000:
            length_score = 50
        else:
            length_score = 45
        
        # 2. Quality keywords analysis (boost score for professional proposals)
        quality_keywords = [
            'experience', 'expertise', 'methodology', 'approach', 'team',
            'quality', 'standards', 'best practices', 'implementation',
            'testing', 'maintenance', 'support', 'documentation',
            'compliance', 'certification', 'proven', 'successful'
        ]
        
        keyword_count = sum(1 for kw in quality_keywords if kw in proposal_text)
        keyword_bonus = min(20, keyword_count * 1.5)
        
        # 3. Technical depth indicators
        technical_terms = [
            'architecture', 'infrastructure', 'scalability', 'security',
            'integration', 'deployment', 'monitoring', 'optimization',
            'performance', 'reliability', 'efficiency'
        ]
        
        tech_depth = sum(1 for term in technical_terms if term in proposal_text)
        tech_bonus = min(15, tech_depth * 2)
        
        proposal_score = min(100, length_score + keyword_bonus + tech_bonus)
        
        # 4. Timeline score (optimal is 30-90 days)
        if timeline <= 0:
            timeline_score = 0
        elif timeline < AIEngine.MIN_REASONABLE_TIMELINE:
            # Too fast - suspicious
            timeline_score = 25
        elif timeline <= 30:
            # Very fast but reasonable
            timeline_score = 100
        elif timeline <= 90:
            # Good timeline (optimal range)
            timeline_score = 95
        elif timeline <= 180:
            # Acceptable timeline
            timeline_score = 75
        elif timeline <= 365:
            # Long timeline
            timeline_score = 55
        else:
            # Very long timeline
            timeline_score = max(25, 50 - ((timeline - 365) / 365 * 20))
        
        # Combine: 60% proposal quality, 40% timeline
        technical_score = proposal_score * 0.6 + timeline_score * 0.4
        
        return max(0, min(100, technical_score))

    @staticmethod
    def _detect_anomalies(
        bid: Bid, 
        all_prices: List[float], 
        all_bids: List[Bid]
    ) -> tuple[bool, List[str], Optional[float]]:
        """
        Detect potential bid anomalies indicating fraud or collusion.
        
        Returns:
            (anomaly_flag, anomaly_reasons, price_deviation)
        """
        anomaly_flag = False
        anomaly_reasons = []
        price_deviation = None
        
        # Calculate price deviation if possible
        if len(all_prices) > 1:
            mean_price = np.mean(all_prices)
            std_price = np.std(all_prices)
            
            if std_price > 0:
                price_deviation = (bid.proposed_price - mean_price) / std_price
                
                # Anomaly 1: Suspiciously low price (>2.5 std deviations below mean)
                if price_deviation < -2.5:
                    anomaly_flag = True
                    anomaly_reasons.append("Suspiciously low bid price (possible underbidding)")
                
                # Anomaly 2: Suspiciously high price (>2 std deviations above mean)
                elif price_deviation > 2.0:
                    anomaly_flag = True
                    anomaly_reasons.append("Unusually high bid price")
        
        # Anomaly 3: Exact price matching (collusion indicator)
        exact_matches = sum(
            1 for b in all_bids
            if b.id != bid.id and abs(b.proposed_price - bid.proposed_price) < 0.01
        )
        if exact_matches > 0:
            anomaly_flag = True
            anomaly_reasons.append(f"Exact price match with {exact_matches} other bid(s) - possible collusion")
        
        # Anomaly 4: Unrealistically short timeline
        if bid.delivery_timeline < AIEngine.MIN_REASONABLE_TIMELINE:
            anomaly_flag = True
            anomaly_reasons.append(f"Unrealistically short delivery timeline ({bid.delivery_timeline} days)")
        
        # Anomaly 5: Suspiciously long timeline
        if bid.delivery_timeline > 730:  # More than 2 years
            anomaly_flag = True
            anomaly_reasons.append(f"Excessively long delivery timeline ({bid.delivery_timeline} days)")
        
        # Anomaly 6: Very short proposal (possible lack of effort)
        if len(bid.technical_proposal or "") < 50:
            anomaly_flag = True
            anomaly_reasons.append("Insufficient technical proposal detail")
        
        return anomaly_flag, anomaly_reasons, price_deviation

    @staticmethod
    def _apply_score_range(base_score: float, conditions_met: int) -> float:
        """
        Apply score ranges based on how many success conditions were met.
        """
        if conditions_met == 3:
            # All conditions met: Force into 85-100 range
            return max(85, min(100, base_score))
        elif conditions_met == 2:
            # Two conditions met: Force into 60-85 range
            return max(60, min(85, base_score))
        elif conditions_met == 1:
            # One condition met: Force into 45-70 range
            return max(45, min(70, base_score))
        else:
            # No conditions met: Force into 0-45 range
            return max(0, min(45, base_score))


    @staticmethod
    def get_recommendations(
        tender_id: int,
        bids: List[Bid],
        vendors: Dict[int, Vendor],
        tender: Tender
    ) -> List[Dict]:
        """
        Generate ranked bid recommendations with comprehensive scoring.
        
        Args:
            tender_id: ID of the tender
            bids: List of all bids for this tender
            vendors: Dictionary mapping vendor_id to Vendor objects
            tender: The tender object
            
        Returns:
            List of bid recommendations sorted by AI score (highest first)
        """
        if not bids:
            logger.warning(f"No bids provided for tender {tender_id}")
            return []
        
        recommendations = []

        try:
            for bid in bids:
                vendor = vendors.get(bid.vendor_id)
                if not vendor:
                    logger.warning(f"Vendor {bid.vendor_id} not found for bid {bid.id}")
                    continue

                # Calculate scores
                scores = AIEngine.score_bid(bid, tender, vendor, bids)

                # Determine recommendation level
                ai_score = scores["ai_score"]
                if ai_score >= 85:
                    recommendation = "Highly Recommended"
                    rank_color = "green"
                elif ai_score >= 70:
                    recommendation = "Recommended"
                    rank_color = "blue"
                elif ai_score >= 50:
                    recommendation = "Consider"
                    rank_color = "yellow"
                else:
                    recommendation = "Not Recommended"
                    rank_color = "red"

                recommendations.append({
                    "bid_id": bid.id,
                    "vendor_id": vendor.id,
                    "vendor_name": vendor.name,
                    "proposed_price": bid.proposed_price,
                    "delivery_timeline": bid.delivery_timeline,
                    "vendor_reputation": vendor.reputation_score,
                    "vendor_total_wins": vendor.total_wins,
                    "vendor_completed_projects": vendor.completed_projects,
                    **scores,
                    "recommendation": recommendation,
                    "rank_color": rank_color,
                    "price_to_budget_ratio": round(
                        AIEngine._safe_divide(bid.proposed_price, tender.budget, 0) * 100, 2
                    )
                })

            # Sort by AI score descending (best first)
            recommendations.sort(key=lambda x: x["ai_score"], reverse=True)
            
            # Add ranking position
            for idx, rec in enumerate(recommendations, 1):
                rec["rank"] = idx
            
            logger.info(f"Generated {len(recommendations)} recommendations for tender {tender_id}")
            return recommendations
            
        except Exception as e:
            logger.error(f"Error generating recommendations for tender {tender_id}: {str(e)}")
            return []
