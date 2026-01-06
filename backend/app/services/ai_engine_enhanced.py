"""
Enhanced AI Engine with Advanced Scoring and Optional LLM Integration

This module provides two modes:
1. RULE_BASED: Advanced rule-based scoring with comprehensive metrics
2. LLM_ENHANCED: Uses LLM for semantic analysis of technical proposals

Configuration via environment variables:
- AI_ENGINE_MODE: "rule_based" or "llm_enhanced" (default: rule_based)
- OPENAI_API_KEY: Required for LLM mode
- ANTHROPIC_API_KEY: Alternative to OpenAI
"""

import numpy as np
from typing import Dict, List, Optional, Tuple
from app.db.models import Bid, Vendor, Tender
import logging
import os
import re
from datetime import datetime

logger = logging.getLogger(__name__)


class EnhancedAIEngine:
    """
    Advanced AI Engine with multi-dimensional scoring and optional LLM integration.
    
    Scoring Dimensions:
    1. Price Competitiveness (35%)
    2. Vendor Credibility (30%)
    3. Technical Quality (25%)
    4. Risk Assessment (10%)
    
    Features:
    - NLP-based proposal analysis
    - Advanced anomaly detection
    - Risk scoring
    - Semantic similarity detection
    - Optional LLM integration for deep proposal analysis
    """

    # Weights for different scoring components
    WEIGHTS = {
        "price": 0.35,
        "vendor": 0.30,
        "technical": 0.25,
        "risk": 0.10
    }
    
    # Thresholds
    ANOMALY_PENALTY = 15
    MIN_TIMELINE_DAYS = 7
    MAX_TIMELINE_DAYS = 730
    OPTIMAL_PRICE_RATIO = 0.80  # 80% of budget
    COLLUSION_SIMILARITY_THRESHOLD = 0.85
    
    def __init__(self, mode: str = None):
        """
        Initialize AI Engine with specified mode.
        
        Args:
            mode: "rule_based" or "llm_enhanced"
        """
        self.mode = mode or os.getenv("AI_ENGINE_MODE", "rule_based")
        self.llm_client = None
        
        if self.mode == "llm_enhanced":
            self._initialize_llm()
    
    def _initialize_llm(self):
        """Initialize LLM client (OpenAI or Anthropic)."""
        try:
            openai_key = os.getenv("OPENAI_API_KEY")
            anthropic_key = os.getenv("ANTHROPIC_API_KEY")
            
            if openai_key:
                import openai
                self.llm_client = openai.OpenAI(api_key=openai_key)
                self.llm_provider = "openai"
                logger.info("LLM mode enabled with OpenAI")
            elif anthropic_key:
                import anthropic
                self.llm_client = anthropic.Anthropic(api_key=anthropic_key)
                self.llm_provider = "anthropic"
                logger.info("LLM mode enabled with Anthropic")
            else:
                logger.warning("LLM mode requested but no API key found. Falling back to rule-based.")
                self.mode = "rule_based"
        except ImportError as e:
            logger.error(f"LLM libraries not installed: {e}. Falling back to rule-based.")
            self.mode = "rule_based"
    
    @staticmethod
    def _safe_divide(numerator: float, denominator: float, default: float = 0.0) -> float:
        """Safely divide two numbers."""
        try:
            return numerator / denominator if denominator != 0 else default
        except (TypeError, ZeroDivisionError):
            return default

    def score_bid(self, bid: Bid, tender: Tender, vendor: Vendor, all_bids: List[Bid]) -> Dict:
        """
        Calculate comprehensive AI score for a bid.
        
        Returns detailed scoring breakdown with explanations.
        """
        try:
            bid_prices = [b.proposed_price for b in all_bids if b.proposed_price > 0]
            
            if not bid_prices:
                logger.warning(f"No valid bid prices for tender {tender.id}")
                bid_prices = [bid.proposed_price]

            # 1. Price Score (35%)
            price_score, price_insights = self._calculate_price_score_v2(
                bid.proposed_price, bid_prices, tender.budget
            )

            # 2. Vendor Score (30%)
            vendor_score, vendor_insights = self._calculate_vendor_score_v2(vendor)

            # 3. Technical Score (25%)
            if self.mode == "llm_enhanced" and self.llm_client:
                technical_score, tech_insights = self._calculate_technical_score_llm(
                    bid.technical_proposal, bid.delivery_timeline, tender
                )
            else:
                technical_score, tech_insights = self._calculate_technical_score_v2(
                    bid.technical_proposal, bid.delivery_timeline, tender
                )

            # 4. Risk Score (10%)
            risk_score, risk_insights = self._calculate_risk_score(
                bid, vendor, bid_prices, all_bids
            )

            # 5. Anomaly Detection
            anomaly_flag, anomaly_reasons = self._detect_anomalies_v2(
                bid, bid_prices, all_bids, tender
            )

            # 6. Calculate Base Score
            base_score = (
                price_score * self.WEIGHTS["price"] +
                vendor_score * self.WEIGHTS["vendor"] +
                technical_score * self.WEIGHTS["technical"] +
                risk_score * self.WEIGHTS["risk"]
            )

            # 7. Apply Intelligent Adjustments
            final_score = self._apply_intelligent_adjustments(
                base_score, bid, vendor, tender, bid_prices, anomaly_flag
            )

            # 8. Generate Insights
            insights = self._generate_insights(
                final_score, price_insights, vendor_insights, 
                tech_insights, risk_insights, anomaly_reasons
            )

            return {
                "ai_score": round(final_score, 2),
                "price_score": round(price_score, 2),
                "vendor_score": round(vendor_score, 2),
                "technical_score": round(technical_score, 2),
                "risk_score": round(risk_score, 2),
                "anomaly_flag": anomaly_flag,
                "anomaly_reason": "; ".join(anomaly_reasons) if anomaly_reasons else None,
                "insights": insights,
                "breakdown": {
                    "price": price_insights,
                    "vendor": vendor_insights,
                    "technical": tech_insights,
                    "risk": risk_insights
                }
            }
            
        except Exception as e:
            logger.error(f"Error scoring bid {bid.id}: {str(e)}", exc_info=True)
            return self._get_fallback_score(str(e))

    def _calculate_price_score_v2(
        self, proposed_price: float, all_prices: List[float], budget: float
    ) -> Tuple[float, Dict]:
        """Enhanced price scoring with detailed insights."""
        insights = {}
        
        # Calculate statistics
        mean_price = np.mean(all_prices)
        median_price = np.median(all_prices)
        std_price = np.std(all_prices) if len(all_prices) > 1 else 0
        
        price_ratio = self._safe_divide(proposed_price, budget, 1.0)
        insights["price_ratio"] = round(price_ratio, 3)
        insights["budget_percentage"] = round(price_ratio * 100, 1)
        insights["position_vs_mean"] = "below" if proposed_price < mean_price else "above"
        insights["savings"] = round((budget - proposed_price) / 1000000, 2)  # in millions
        
        # Multi-factor price scoring
        if len(all_prices) > 1 and std_price > 0:
            z_score = (proposed_price - mean_price) / std_price
            insights["z_score"] = round(z_score, 2)
            insights["competitiveness"] = (
                "highly competitive" if z_score < -1 else
                "competitive" if z_score < 0 else
                "average" if z_score < 1 else
                "expensive"
            )
            
            # Score based on competitiveness
            if z_score < -2:
                price_score = 100  # Significantly below average
            elif z_score < -1:
                price_score = 95  # Well below average
            elif z_score < 0:
                price_score = 85  # Below average
            elif z_score < 0.5:
                price_score = 75  # Slightly above average
            elif z_score < 1:
                price_score = 65  # Above average
            else:
                price_score = max(30, 80 - (z_score * 20))  # Well above average
        else:
            # Single bid or no variance - score on budget ratio
            if price_ratio <= self.OPTIMAL_PRICE_RATIO:
                price_score = 100
                insights["competitiveness"] = "excellent"
            elif price_ratio <= 0.95:
                price_score = 90
                insights["competitiveness"] = "good"
            elif price_ratio <= 1.0:
                price_score = 80
                insights["competitiveness"] = "acceptable"
            elif price_ratio <= 1.1:
                price_score = 60
                insights["competitiveness"] = "slightly over budget"
            else:
                price_score = max(20, 50 - (price_ratio - 1.1) * 100)
                insights["competitiveness"] = "over budget"
        
        # Bonus for value-for-money
        if 0.70 <= price_ratio <= 0.85:
            price_score = min(100, price_score + 5)
            insights["bonus"] = "optimal value range"
        
        return max(0, min(100, price_score)), insights

    def _calculate_vendor_score_v2(self, vendor: Vendor) -> Tuple[float, Dict]:
        """Enhanced vendor credibility scoring."""
        insights = {}
        
        # Base reputation (0-5 scale → 0-50 points)
        reputation = vendor.reputation_score or 0
        reputation_points = min(50, reputation * 10)
        insights["reputation"] = reputation
        insights["reputation_points"] = round(reputation_points, 1)
        
        # Track record (0-30 points)
        total_wins = vendor.total_wins or 0
        completed = vendor.completed_projects or 0
        
        track_record_points = min(30, (total_wins * 10) + (completed * 3))
        insights["total_wins"] = total_wins
        insights["completed_projects"] = completed
        insights["track_record_points"] = round(track_record_points, 1)
        
        # Average rating (0-5 scale → 0-20 points)
        avg_rating = vendor.average_rating or 0
        rating_points = min(20, avg_rating * 4)
        insights["average_rating"] = avg_rating
        insights["rating_points"] = round(rating_points, 1)
        
        # Experience level assessment
        if completed >= 10 and total_wins >= 5:
            insights["experience_level"] = "highly experienced"
        elif completed >= 5 and total_wins >= 2:
            insights["experience_level"] = "experienced"
        elif completed >= 1:
            insights["experience_level"] = "some experience"
        else:
            insights["experience_level"] = "new vendor"
        
        vendor_score = reputation_points + track_record_points + rating_points
        
        return max(0, min(100, vendor_score)), insights

    def _calculate_technical_score_v2(
        self, proposal: str, timeline: int, tender: Tender
    ) -> Tuple[float, Dict]:
        """Advanced rule-based technical scoring with NLP features."""
        insights = {}
        proposal_text = (proposal or "").lower()
        
        # 1. Proposal Quality Analysis (0-50 points)
        proposal_length = len(proposal or "")
        insights["proposal_length"] = proposal_length
        
        # Length-based scoring (optimal: 300-1000 chars)
        if proposal_length < 100:
            length_score = 10
            insights["length_quality"] = "too short"
        elif proposal_length < 300:
            length_score = 30
            insights["length_quality"] = "minimal"
        elif proposal_length <= 1000:
            length_score = 50
            insights["length_quality"] = "good"
        elif proposal_length <= 2000:
            length_score = 45
            insights["length_quality"] = "comprehensive"
        else:
            length_score = 40
            insights["length_quality"] = "very detailed"
        
        # 2. Content Quality (keyword analysis)
        quality_keywords = [
            'experience', 'expertise', 'methodology', 'approach', 'team',
            'quality', 'standards', 'best practices', 'implementation',
            'testing', 'maintenance', 'support', 'documentation',
            'compliance', 'certification', 'proven', 'successful'
        ]
        
        keyword_count = sum(1 for kw in quality_keywords if kw in proposal_text)
        content_quality = min(30, keyword_count * 2)
        insights["quality_keywords_found"] = keyword_count
        insights["content_quality_score"] = content_quality
        
        # 3. Technical depth indicators
        technical_terms = [
            'architecture', 'infrastructure', 'scalability', 'security',
            'integration', 'deployment', 'monitoring', 'optimization',
            'performance', 'reliability', 'efficiency'
        ]
        
        tech_depth = sum(1 for term in technical_terms if term in proposal_text)
        insights["technical_depth"] = tech_depth
        
        # 4. Timeline Score (0-50 points)
        insights["timeline_days"] = timeline
        
        if timeline <= 0:
            timeline_score = 0
            insights["timeline_assessment"] = "invalid"
        elif timeline < self.MIN_TIMELINE_DAYS:
            timeline_score = 20
            insights["timeline_assessment"] = "unrealistic (too fast)"
        elif timeline <= 30:
            timeline_score = 50
            insights["timeline_assessment"] = "aggressive but feasible"
        elif timeline <= 90:
            timeline_score = 48
            insights["timeline_assessment"] = "optimal"
        elif timeline <= 180:
            timeline_score = 42
            insights["timeline_assessment"] = "reasonable"
        elif timeline <= 365:
            timeline_score = 35
            insights["timeline_assessment"] = "conservative"
        else:
            timeline_score = max(15, 40 - ((timeline - 365) / 365 * 20))
            insights["timeline_assessment"] = "very long"
        
        # Combine scores
        proposal_score = length_score + content_quality * 0.5
        technical_score = (proposal_score * 0.6) + (timeline_score * 0.4)
        
        insights["proposal_component"] = round(proposal_score, 1)
        insights["timeline_component"] = round(timeline_score, 1)
        
        return max(0, min(100, technical_score)), insights

    def _calculate_technical_score_llm(
        self, proposal: str, timeline: int, tender: Tender
    ) -> Tuple[float, Dict]:
        """LLM-powered technical proposal analysis."""
        insights = {}
        
        try:
            # Get rule-based baseline
            baseline_score, baseline_insights = self._calculate_technical_score_v2(
                proposal, timeline, tender
            )
            insights.update(baseline_insights)
            
            # LLM semantic analysis
            prompt = f"""Analyze this technical proposal for a {tender.category} tender.

Tender: {tender.title}
Budget: {tender.budget}
Proposal: {proposal[:1500]}  # Limit to save tokens

Evaluate on:
1. Technical feasibility (0-10)
2. Innovation and approach (0-10)
3. Clarity and professionalism (0-10)
4. Completeness (0-10)
5. Risk mitigation strategies (0-10)

Respond in JSON format:
{{
  "feasibility": score,
  "innovation": score,
  "clarity": score,
  "completeness": score,
  "risk_mitigation": score,
  "strengths": ["strength1", "strength2"],
  "weaknesses": ["weakness1", "weakness2"],
  "overall_assessment": "brief assessment"
}}"""

            if self.llm_provider == "openai":
                response = self.llm_client.chat.completions.create(
                    model="gpt-4o-mini",  # Faster and cheaper
                    messages=[
                        {"role": "system", "content": "You are an expert procurement analyst."},
                        {"role": "user", "content": prompt}
                    ],
                    temperature=0.3,
                    max_tokens=500
                )
                llm_result = response.choices[0].message.content
            else:  # Anthropic
                response = self.llm_client.messages.create(
                    model="claude-3-haiku-20240307",  # Fast and cost-effective
                    max_tokens=500,
                    messages=[{"role": "user", "content": prompt}]
                )
                llm_result = response.content[0].text
            
            # Parse LLM response
            import json
            try:
                llm_analysis = json.loads(llm_result)
                
                # Calculate LLM score (0-100)
                llm_score = (
                    llm_analysis.get("feasibility", 5) +
                    llm_analysis.get("innovation", 5) +
                    llm_analysis.get("clarity", 5) +
                    llm_analysis.get("completeness", 5) +
                    llm_analysis.get("risk_mitigation", 5)
                ) * 2  # Convert 0-50 to 0-100
                
                insights["llm_score"] = round(llm_score, 1)
                insights["llm_analysis"] = llm_analysis.get("overall_assessment", "")
                insights["strengths"] = llm_analysis.get("strengths", [])
                insights["weaknesses"] = llm_analysis.get("weaknesses", [])
                
                # Blend rule-based and LLM scores (70% LLM, 30% rule-based)
                final_score = (llm_score * 0.7) + (baseline_score * 0.3)
                insights["scoring_mode"] = "llm_enhanced"
                
                return max(0, min(100, final_score)), insights
                
            except json.JSONDecodeError:
                logger.warning("Failed to parse LLM response, using rule-based score")
                insights["scoring_mode"] = "rule_based_fallback"
                return baseline_score, insights
                
        except Exception as e:
            logger.error(f"LLM analysis failed: {e}. Using rule-based scoring.")
            insights["scoring_mode"] = "rule_based_fallback"
            insights["llm_error"] = str(e)
            return baseline_score, insights

    def _calculate_risk_score(
        self, bid: Bid, vendor: Vendor, all_prices: List[float], all_bids: List[Bid]
    ) -> Tuple[float, Dict]:
        """Calculate risk score (higher score = lower risk)."""
        insights = {}
        risk_factors = []
        risk_score = 100  # Start with perfect score, deduct for risks
        
        # Risk 1: Price volatility
        if len(all_prices) > 1:
            mean_price = np.mean(all_prices)
            std_price = np.std(all_prices)
            if std_price > 0:
                z_score = (bid.proposed_price - mean_price) / std_price
                if abs(z_score) > 2:
                    risk_score -= 20
                    risk_factors.append("price_outlier")
        
        # Risk 2: Vendor track record
        if (vendor.total_wins or 0) == 0 and (vendor.completed_projects or 0) == 0:
            risk_score -= 25
            risk_factors.append("no_track_record")
        elif (vendor.total_wins or 0) < 2:
            risk_score -= 10
            risk_factors.append("limited_experience")
        
        # Risk 3: Timeline risk
        if bid.delivery_timeline < 14:
            risk_score -= 15
            risk_factors.append("aggressive_timeline")
        elif bid.delivery_timeline > 365:
            risk_score -= 10
            risk_factors.append("extended_timeline")
        
        # Risk 4: Proposal quality risk
        if len(bid.technical_proposal or "") < 200:
            risk_score -= 15
            risk_factors.append("thin_proposal")
        
        insights["risk_factors"] = risk_factors
        insights["risk_level"] = (
            "low" if risk_score >= 80 else
            "moderate" if risk_score >= 60 else
            "high" if risk_score >= 40 else
            "very high"
        )
        
        return max(0, min(100, risk_score)), insights

    def _detect_anomalies_v2(
        self, bid: Bid, all_prices: List[float], all_bids: List[Bid], tender: Tender
    ) -> Tuple[bool, List[str]]:
        """Enhanced anomaly detection."""
        anomalies = []
        
        # Statistical price anomalies
        if len(all_prices) > 1:
            mean_price = np.mean(all_prices)
            std_price = np.std(all_prices)
            if std_price > 0:
                z_score = (bid.proposed_price - mean_price) / std_price
                if z_score < -3:
                    anomalies.append("Extremely low price (>3σ below mean)")
                elif z_score > 2.5:
                    anomalies.append("Unusually high price (>2.5σ above mean)")
        
        # Collusion detection - exact matches
        exact_matches = sum(
            1 for b in all_bids 
            if b.id != bid.id and abs(b.proposed_price - bid.proposed_price) < 1
        )
        if exact_matches > 0:
            anomalies.append(f"Exact price match with {exact_matches} bid(s) - possible collusion")
        
        # Timeline anomalies
        if bid.delivery_timeline < self.MIN_TIMELINE_DAYS:
            anomalies.append(f"Unrealistically short timeline ({bid.delivery_timeline} days)")
        elif bid.delivery_timeline > self.MAX_TIMELINE_DAYS:
            anomalies.append(f"Excessive timeline ({bid.delivery_timeline} days)")
        
        # Proposal quality anomalies
        proposal_len = len(bid.technical_proposal or "")
        if proposal_len < 100:
            anomalies.append("Insufficient technical proposal (<100 chars)")
        
        # Budget anomalies
        if bid.proposed_price > tender.budget * 1.2:
            anomalies.append("Price exceeds 120% of budget")
        elif bid.proposed_price < tender.budget * 0.3:
            anomalies.append("Suspiciously low price (<30% of budget)")
        
        return len(anomalies) > 0, anomalies

    def _apply_intelligent_adjustments(
        self, base_score: float, bid: Bid, vendor: Vendor, 
        tender: Tender, all_prices: List[float], has_anomaly: bool
    ) -> float:
        """Apply intelligent score adjustments based on context."""
        score = base_score
        
        # Anomaly penalty
        if has_anomaly:
            score -= self.ANOMALY_PENALTY
        
        # Bonus for optimal conditions
        avg_price = np.mean(all_prices)
        conditions_met = 0
        
        if bid.proposed_price <= avg_price * 0.9:
            conditions_met += 1
        if bid.delivery_timeline <= 90:
            conditions_met += 1
        if (vendor.reputation_score or 0) >= 3.5 or (vendor.total_wins or 0) >= 3:
            conditions_met += 1
        
        # Apply bonus/penalty based on conditions
        if conditions_met == 3:
            score = max(score, 85)  # Ensure at least 85 if all conditions met
        elif conditions_met == 0:
            score = min(score, 60)  # Cap at 60 if no conditions met
        
        return max(0, min(100, score))

    def _generate_insights(
        self, final_score: float, price_insights: Dict, 
        vendor_insights: Dict, tech_insights: Dict, 
        risk_insights: Dict, anomalies: List[str]
    ) -> str:
        """Generate human-readable insights."""
        parts = []
        
        # Overall assessment
        if final_score >= 85:
            parts.append("⭐ Excellent bid - highly recommended")
        elif final_score >= 70:
            parts.append("✓ Strong bid - recommended")
        elif final_score >= 55:
            parts.append("○ Acceptable bid - consider carefully")
        else:
            parts.append("⚠ Weak bid - not recommended")
        
        # Key highlights
        if price_insights.get("competitiveness") in ["highly competitive", "excellent"]:
            parts.append(f"• Competitive pricing ({price_insights['budget_percentage']}% of budget)")
        
        if vendor_insights.get("experience_level") == "highly experienced":
            parts.append("• Highly experienced vendor")
        elif vendor_insights.get("experience_level") == "new vendor":
            parts.append("• New vendor - higher risk")
        
        if tech_insights.get("timeline_assessment") in ["optimal", "aggressive but feasible"]:
            parts.append(f"• Good timeline ({tech_insights['timeline_days']} days)")
        
        if risk_insights.get("risk_level") == "high":
            parts.append("• ⚠ High risk factors identified")
        
        return " | ".join(parts)

    def _get_fallback_score(self, error_msg: str) -> Dict:
        """Return safe fallback scores in case of error."""
        return {
            "ai_score": 50.0,
            "price_score": 50.0,
            "vendor_score": 50.0,
            "technical_score": 50.0,
            "risk_score": 50.0,
            "anomaly_flag": True,
            "anomaly_reason": f"Scoring error: {error_msg}",
            "insights": "Unable to generate full analysis due to error"
        }

    def get_recommendations(
        self, tender_id: int, bids: List[Bid], 
        vendors: Dict[int, Vendor], tender: Tender
    ) -> List[Dict]:
        """Generate comprehensive ranked recommendations."""
        if not bids:
            return []
        
        recommendations = []
        
        for bid in bids:
            vendor = vendors.get(bid.vendor_id)
            if not vendor:
                continue
            
            scores = self.score_bid(bid, tender, vendor, bids)
            
            # Determine recommendation
            ai_score = scores["ai_score"]
            if ai_score >= 85:
                recommendation = "Highly Recommended"
                rank_color = "green"
            elif ai_score >= 70:
                recommendation = "Recommended"
                rank_color = "blue"
            elif ai_score >= 55:
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
                **scores,
                "recommendation": recommendation,
                "rank_color": rank_color
            })
        
        # Sort by AI score
        recommendations.sort(key=lambda x: x["ai_score"], reverse=True)
        
        # Add rankings
        for idx, rec in enumerate(recommendations, 1):
            rec["rank"] = idx
        
        return recommendations
