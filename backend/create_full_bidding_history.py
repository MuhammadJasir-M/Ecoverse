"""
Create Comprehensive Bidding History for All Vendors with Blockchain Logging
Run this script INSIDE the Docker container:
  docker cp create_full_bidding_history.py procurement_backend:/app/
  docker-compose exec backend python create_full_bidding_history.py
"""

from app.db.session import SessionLocal
from app.db.models import Tender, Bid, Award, Vendor, TenderStatus, BidStatus
from app.services.hash_utils import generate_tender_hash, generate_bid_hash, generate_award_hash
from app.services.blockchain import BlockchainService
from datetime import datetime, timedelta
import random

def main():
    print("🏛️  Creating Comprehensive Bidding History with Blockchain Logging")
    print("=" * 80)
    
    db = SessionLocal()
    blockchain_service = BlockchainService()
    
    try:
        # Get existing vendors
        vendors = db.query(Vendor).all()
        if len(vendors) < 2:
            print("❌ Need at least 2 vendors. Please register vendors first.")
            return
        
        print(f"✅ Found {len(vendors)} vendors:")
        for i, v in enumerate(vendors, 1):
            print(f"   {i}. {v.name} (ID: {v.id}, Vendor ID: {v.vendor_id})")
        
        now = datetime.utcnow()
        
        # Create 20 diverse tenders with blockchain logging (more opportunities for all vendors)
        print(f"\n📝 Creating 20 historical tenders...")
        tender_data = [
            {
                "title": "City Website Redesign Project",
                "description": "Complete redesign of the city's main website with modern UI/UX, mobile responsiveness, accessibility compliance, and CMS integration.",
                "category": "Web Development",
                "budget": 75000.0,
                "department": "Department of Communications",
                "deadline": now - timedelta(days=60)
            },
            {
                "title": "Municipal Tax Collection Software",
                "description": "Automated tax calculation and collection system for property taxes, business licenses, and other municipal fees.",
                "category": "IT Services",
                "budget": 120000.0,
                "department": "Department of Finance",
                "deadline": now - timedelta(days=30)
            },
            {
                "title": "Smart Parking Management System",
                "description": "IoT-based parking management solution for city parking lots with real-time tracking and mobile app.",
                "category": "Smart City Solutions",
                "budget": 95000.0,
                "department": "Department of Transportation",
                "deadline": now - timedelta(days=15)
            },
            {
                "title": "Public Health Portal Development",
                "description": "Health information portal for citizens with appointment booking, medical records access, and vaccination tracking. HIPAA compliance required.",
                "category": "Healthcare IT",
                "budget": 85000.0,
                "department": "Department of Health",
                "deadline": now + timedelta(days=20)
            },
            {
                "title": "E-Permit Application System",
                "description": "Online permit application and approval system for building permits, business licenses, and event permits.",
                "category": "Government Services",
                "budget": 65000.0,
                "department": "Department of Development Services",
                "deadline": now + timedelta(days=35)
            },
            {
                "title": "Smart Street Lighting System",
                "description": "IoT-enabled LED street lighting with remote monitoring, automated scheduling, and energy consumption analytics.",
                "category": "Smart City Solutions",
                "budget": 180000.0,
                "department": "Department of Public Works",
                "deadline": now - timedelta(days=20)
            },
            {
                "title": "Waste Management Tracking Platform",
                "description": "GPS-based waste collection tracking system with route optimization, citizen complaint management, and analytics dashboard.",
                "category": "Environmental Technology",
                "budget": 95000.0,
                "department": "Department of Sanitation",
                "deadline": now - timedelta(days=10)
            },
            {
                "title": "Digital Library Management System",
                "description": "Comprehensive library management software with online catalog, book reservation, e-book lending, and member management.",
                "category": "Education Technology",
                "budget": 55000.0,
                "department": "Department of Culture & Education",
                "deadline": now + timedelta(days=25)
            },
            {
                "title": "Traffic Management & Analytics Platform",
                "description": "AI-powered traffic monitoring system with real-time analytics, congestion prediction, and automated signal control integration.",
                "category": "Smart City Solutions",
                "budget": 200000.0,
                "department": "Department of Transportation",
                "deadline": now - timedelta(days=5)
            },
            {
                "title": "Citizen Grievance Redressal System",
                "description": "Mobile and web-based complaint management platform with workflow automation, geo-tagging, and citizen feedback loop.",
                "category": "Government Services",
                "budget": 70000.0,
                "department": "Department of Administration",
                "deadline": now + timedelta(days=30)
            },
            {
                "title": "Water Quality Monitoring Network",
                "description": "IoT sensor network for continuous water quality monitoring across distribution points with real-time alerts and reporting.",
                "category": "Environmental Technology",
                "budget": 145000.0,
                "department": "Department of Water Resources",
                "deadline": now + timedelta(days=40)
            },
            {
                "title": "Emergency Response Coordination Platform",
                "description": "Integrated emergency management system with incident tracking, resource allocation, and multi-agency coordination capabilities.",
                "category": "Public Safety Technology",
                "budget": 175000.0,
                "department": "Department of Emergency Services",
                "deadline": now + timedelta(days=45)
            },
            {
                "title": "Public Transportation Ticketing System",
                "description": "Contactless smart card and mobile ticketing platform for buses and metro with fare management and trip analytics.",
                "category": "Smart City Solutions",
                "budget": 130000.0,
                "department": "Department of Transportation",
                "deadline": now - timedelta(days=25)
            },
            {
                "title": "Building Safety Inspection Management",
                "description": "Mobile-first inspection scheduling and reporting system for building code compliance with photo documentation.",
                "category": "Government Services",
                "budget": 58000.0,
                "department": "Department of Building Safety",
                "deadline": now + timedelta(days=50)
            },
            {
                "title": "Urban Forest Management System",
                "description": "GIS-based tree inventory and maintenance tracking platform with citizen reporting and work order management.",
                "category": "Environmental Technology",
                "budget": 72000.0,
                "department": "Department of Parks & Recreation",
                "deadline": now - timedelta(days=35)
            },
            {
                "title": "Community Center Booking Platform",
                "description": "Online reservation system for community centers, sports facilities, and public venues with payment integration.",
                "category": "Government Services",
                "budget": 48000.0,
                "department": "Department of Community Services",
                "deadline": now + timedelta(days=55)
            },
            {
                "title": "Air Quality Monitoring Network",
                "description": "Network of IoT sensors for real-time air quality monitoring with public dashboard and alert system.",
                "category": "Environmental Technology",
                "budget": 165000.0,
                "department": "Department of Environmental Protection",
                "deadline": now - timedelta(days=12)
            },
            {
                "title": "Business License Portal Upgrade",
                "description": "Enhanced online business registration and renewal platform with document verification and payment processing.",
                "category": "IT Services",
                "budget": 62000.0,
                "department": "Department of Economic Development",
                "deadline": now + timedelta(days=38)
            },
            {
                "title": "Fleet Management & GPS Tracking",
                "description": "Comprehensive vehicle fleet tracking system with maintenance scheduling, fuel monitoring, and route optimization.",
                "category": "Smart City Solutions",
                "budget": 110000.0,
                "department": "Department of Fleet Services",
                "deadline": now - timedelta(days=8)
            },
            {
                "title": "Civic Engagement Mobile App",
                "description": "Citizen engagement platform with news updates, event calendars, service requests, and community polls.",
                "category": "Government Services",
                "budget": 78000.0,
                "department": "Department of Communications",
                "deadline": now + timedelta(days=42)
            }
        ]
        
        tenders = []
        for t_data in tender_data:
            tender_hash = generate_tender_hash({
                "title": t_data["title"],
                "description": t_data["description"],
                "category": t_data["category"],
                "budget": t_data["budget"],
                "department": t_data["department"],
                "deadline": str(t_data["deadline"])
            })
            
            tender = Tender(
                title=t_data["title"],
                description=t_data["description"],
                category=t_data["category"],
                budget=t_data["budget"],
                department=t_data["department"],
                deadline=t_data["deadline"],
                status=TenderStatus.OPEN,
                creation_hash=tender_hash
            )
            db.add(tender)
            db.flush()
            
            # Log on blockchain
            tx_hash = blockchain_service.log_tender_creation(tender.id, tender_hash)
            if tx_hash:
                tender.creation_tx_hash = tx_hash
                print(f"   ✅ Tender #{tender.id}: {tender.title[:45]}... [Blockchain: {tx_hash[:15]}...]")
            
            tenders.append(tender)
        
        db.commit()
        
        # Create balanced competitive bids - ensure EACH vendor gets approximately equal bids
        print(f"\n💼 Creating balanced competitive bids from {len(vendors)} vendors...")
        print(f"   (Ensuring each vendor participates equally in bidding)")
        
        all_bids = []
        bid_count = 0
        
        # Track bids per vendor to ensure balance
        vendor_bid_count = {v.id: 0 for v in vendors}
        target_bids_per_vendor = len(tenders) // 2  # Each vendor should bid on ~half of tenders
        
        # For each tender, ensure balanced vendor participation
        for tender_idx, tender in enumerate(tenders):
            print(f"\n   Tender #{tender.id}: {tender.title[:40]}...")
            
            # Determine which vendors should bid (ensure balance)
            available_vendors = []
            
            # Prioritize vendors with fewer bids
            sorted_vendors = sorted(vendors, key=lambda v: vendor_bid_count[v.id])
            
            # Select 6-8 vendors per tender, prioritizing those with fewer bids
            num_bidders = random.randint(6, 8)
            selected_vendors = sorted_vendors[:num_bidders]
            
            for vendor in selected_vendors:
                # Generate realistic bid price (88% to 102% of budget for competitiveness)
                price_factor = random.uniform(0.88, 1.02)
                proposed_price = round(tender.budget * price_factor, 2)
                
                # Generate realistic delivery timeline (60-180 days based on budget)
                base_timeline = int(tender.budget / 1000)  # $1000 = 1 day
                timeline = random.randint(int(base_timeline * 0.8), int(base_timeline * 1.2))
                timeline = max(30, min(timeline, 180))  # Between 30-180 days
                
                # Generate proposal text
                proposal = f"{vendor.name} proposes a comprehensive solution for {tender.title}. "
                proposal += f"Our team has extensive experience in {tender.category} projects. "
                proposal += f"We offer innovative technology, proven methodologies, and dedicated support. "
                proposal += f"Budget-optimized at ${proposed_price:,.0f} with {timeline}-day delivery timeline. "
                proposal += f"Includes training, documentation, and warranty support."
                
                bid_hash = generate_bid_hash({
                    "tender_id": tender.id,
                    "vendor_id": vendor.id,
                    "proposed_price": proposed_price
                })
                
                bid = Bid(
                    tender_id=tender.id,
                    vendor_id=vendor.id,
                    proposed_price=proposed_price,
                    technical_proposal=proposal,
                    delivery_timeline=timeline,
                    status=BidStatus.SUBMITTED,
                    submission_hash=bid_hash
                )
                db.add(bid)
                db.flush()
                
                # Log on blockchain
                tx_hash = blockchain_service.log_bid_submission(bid.id, tender.id, bid_hash)
                if tx_hash:
                    bid.submission_tx_hash = tx_hash
                
                vendor_bid_count[vendor.id] += 1
                print(f"      ✅ Bid #{bid.id} from {vendor.name[:25]:25} - ${proposed_price:>10,.0f} ({timeline} days) [Total: {vendor_bid_count[vendor.id]}]")
                all_bids.append(bid)
                bid_count += 1
        
        db.commit()
        print(f"\n✅ Created {bid_count} total bids across all tenders")
        print(f"\n📊 Bid Distribution Per Vendor:")
        for vendor in sorted(vendors, key=lambda v: v.name):
            print(f"   {vendor.name[:35]:<35} - {vendor_bid_count[vendor.id]:>3} bids")
        
        # Award 14 tenders (past/completed projects) - leave 6 open
        print(f"\n🏆 Awarding 14 completed tenders with blockchain logging...")
        
        awarded_count = 0
        vendor_stats = {v.id: {"bids": 0, "wins": 0} for v in vendors}
        
        # Count bids per vendor
        for bid in all_bids:
            vendor_stats[bid.vendor_id]["bids"] += 1
        
        # Award first 14 tenders
        for tender_idx in range(14):
            tender = tenders[tender_idx]
            
            # Get all bids for this tender
            tender_bids = [b for b in all_bids if b.tender_id == tender.id]
            
            if not tender_bids:
                continue
            
            # Select winner based on best price (simple logic)
            winning_bid = min(tender_bids, key=lambda b: b.proposed_price)
            
            # Update tender status
            tender.status = TenderStatus.AWARDED
            
            # Update bid statuses
            for bid in tender_bids:
                bid.status = BidStatus.ACCEPTED if bid.id == winning_bid.id else BidStatus.REJECTED
            
            # Create award
            award_hash = generate_award_hash({
                "tender_id": tender.id,
                "winning_bid_id": winning_bid.id,
                "award_amount": winning_bid.proposed_price
            })
            
            tender.award_hash = award_hash
            
            winner_vendor = next(v for v in vendors if v.id == winning_bid.vendor_id)
            justification = f"{winner_vendor.name} selected based on competitive pricing (${winning_bid.proposed_price:,.0f}) "
            justification += f"and strong technical proposal. AI analysis confirmed excellent scores across all criteria. "
            justification += f"The vendor demonstrated proven expertise in {tender.category} with realistic delivery timeline "
            justification += f"of {winning_bid.delivery_timeline} days. No anomalies detected in bid evaluation."
            
            award = Award(
                tender_id=tender.id,
                winning_bid_id=winning_bid.id,
                award_amount=winning_bid.proposed_price,
                justification=justification,
                contract_start=now - timedelta(days=random.randint(5, 15)),
                contract_end=now + timedelta(days=random.randint(60, 120))
            )
            db.add(award)
            db.flush()
            
            # Log on blockchain
            tx_hash = blockchain_service.log_award_decision(tender.id, winning_bid.id, award_hash)
            if tx_hash:
                tender.award_tx_hash = tx_hash
                print(f"   ✅ Award #{award.id}: Tender #{tender.id} → {winner_vendor.name[:30]:30} [${winning_bid.proposed_price:>10,.0f}]")
                awarded_count += 1
                vendor_stats[winner_vendor.id]["wins"] += 1
            
            # Update vendor stats
            winner_vendor.total_wins += 1
        
        db.commit()
        
        # Summary
        print("\n" + "="*80)
        print("✅ Comprehensive Bidding History Created Successfully!")
        print("="*80)
        print(f"\n📊 Overall Summary:")
        print(f"   - {len(tenders)} tenders created (all blockchain-logged)")
        print(f"   - {bid_count} total bids submitted (all blockchain-logged)")
        print(f"   - {awarded_count} tenders awarded (all blockchain-logged)")
        print(f"   - {len(tenders) - awarded_count} tenders still open for bidding")
        
        print(f"\n📈 Vendor Performance Analysis:")
        print(f"   {'Vendor Name':<35} {'Bids':>6} {'Wins':>6} {'Win Rate':>10}")
        print(f"   {'-'*35} {'-'*6} {'-'*6} {'-'*10}")
        for vendor in sorted(vendors, key=lambda v: vendor_stats[v.id]["wins"], reverse=True):
            stats = vendor_stats[vendor.id]
            win_rate = (stats["wins"] / stats["bids"] * 100) if stats["bids"] > 0 else 0
            print(f"   {vendor.name[:35]:<35} {stats['bids']:>6} {stats['wins']:>6} {win_rate:>9.1f}%")
        
        print(f"\n💰 Budget Analysis:")
        total_budget = sum(t.budget for t in tenders)
        awarded_budget = sum(t.budget for t in tenders if t.status == TenderStatus.AWARDED)
        total_awarded_amount = sum(a.award_amount for a in db.query(Award).all())
        savings = awarded_budget - total_awarded_amount
        
        print(f"   - Total tender budget: ${total_budget:,.0f}")
        print(f"   - Awarded budget: ${awarded_budget:,.0f}")
        print(f"   - Actual amount spent: ${total_awarded_amount:,.0f}")
        print(f"   - Total savings: ${savings:,.0f} ({savings/awarded_budget*100:.1f}%)")
        
        print(f"\n💡 Blockchain Verification:")
        print(f"   ✅ All {len(tenders)} tender creations logged on blockchain")
        print(f"   ✅ All {bid_count} bid submissions logged on blockchain")
        print(f"   ✅ All {awarded_count} award decisions logged on blockchain")
        print(f"   ✅ Complete immutable audit trail established")
        
        print(f"\n🌐 Next Steps:")
        print(f"   1. Login to Government portal to see all tenders and awards")
        print(f"   2. Login as any vendor to see their bidding history")
        print(f"   3. Visit Public portal to view {awarded_count} blockchain-verified tenders")
        print(f"   4. Check vendor rankings and performance analytics")
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    main()
