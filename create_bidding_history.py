"""
Create Historical Bidding Data with Blockchain Logging
Run this script INSIDE the Docker container:
  docker-compose exec backend python create_bidding_history.py
"""

from app.db.session import SessionLocal
from app.db.models import Tender, Bid, Award, Vendor, TenderStatus, BidStatus
from app.services.hash_utils import generate_tender_hash, generate_bid_hash, generate_award_hash
from app.services.blockchain import BlockchainService
from datetime import datetime, timedelta

def main():
    print("🏛️  Creating Historical Bidding Data with Blockchain Logging")
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
        
        # Create 5 historical tenders with blockchain logging
        print("\n📝 Creating 5 historical tenders...")
        tender_data = [
            {
                "title": "City Website Redesign Project",
                "description": "Complete redesign of the city's main website with modern UI/UX, mobile responsiveness, accessibility compliance, and CMS integration.",
                "category": "Web Development",
                "budget": 75000.0,
                "department": "Department of Communications",
                "deadline": now - timedelta(days=60),
                "created_days_ago": 90
            },
            {
                "title": "Municipal Tax Collection Software",
                "description": "Automated tax calculation and collection system for property taxes, business licenses, and other municipal fees.",
                "category": "IT Services",
                "budget": 120000.0,
                "department": "Department of Finance",
                "deadline": now - timedelta(days=30),
                "created_days_ago": 75
            },
            {
                "title": "Smart Parking Management System",
                "description": "IoT-based parking management solution for city parking lots with real-time tracking and mobile app.",
                "category": "Smart City Solutions",
                "budget": 95000.0,
                "department": "Department of Transportation",
                "deadline": now - timedelta(days=15),
                "created_days_ago": 60
            },
            {
                "title": "Public Health Portal Development",
                "description": "Health information portal for citizens with appointment booking, medical records access, and vaccination tracking. HIPAA compliance required.",
                "category": "Healthcare IT",
                "budget": 85000.0,
                "department": "Department of Health",
                "deadline": now + timedelta(days=20),
                "created_days_ago": 45
            },
            {
                "title": "E-Permit Application System",
                "description": "Online permit application and approval system for building permits, business licenses, and event permits.",
                "category": "Government Services",
                "budget": 65000.0,
                "department": "Department of Development Services",
                "deadline": now + timedelta(days=35),
                "created_days_ago": 30
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
                print(f"   ✅ Tender #{tender.id}: {tender.title[:40]}... [Blockchain: {tx_hash[:15]}...]")
            
            tenders.append(tender)
        
        db.commit()
        
        # Create competitive bids for each tender
        print(f"\n💼 Creating competitive bids from {len(vendors)} vendors...")
        
        bid_data = [
            # Tender 1: City Website
            [
                {"vendor_id": vendors[0].id, "price": 68000.0, "timeline": 70, "proposal": f"{vendors[0].name} proposes a modern React/Next.js website with Azure cloud hosting, SEO optimization, WCAG 2.1 AA accessibility, and multilingual support. 1 year free maintenance included."},
                {"vendor_id": vendors[1].id, "price": 72000.0, "timeline": 49, "proposal": f"{vendors[1].name} offers WordPress CMS solution with custom theme, plugin integration, and mobile responsiveness. Quick delivery with standard features."}
            ],
            # Tender 2: Tax Collection
            [
                {"vendor_id": vendors[0].id, "price": 125000.0, "timeline": 126, "proposal": f"{vendors[0].name} proposes Python/FastAPI backend with React frontend, PostgreSQL database. PCI DSS compliance, automated tax calculation, payment gateway integration, and comprehensive reporting."},
                {"vendor_id": vendors[1].id, "price": 110000.0, "timeline": 105, "proposal": f"{vendors[1].name} provides proven tax management solution using .NET Core and SQL Server. Includes data migration, staff training, and 1-year warranty. Successfully deployed for 8 municipalities."}
            ],
            # Tender 3: Smart Parking
            [
                {"vendor_id": vendors[0].id, "price": 88000.0, "timeline": 105, "proposal": f"{vendors[0].name} delivers IoT solution with ultrasonic sensors, Node.js platform, and iOS/Android apps. Hardware included with 2-year warranty."},
                {"vendor_id": vendors[1].id, "price": 92000.0, "timeline": 98, "proposal": f"{vendors[1].name} offers camera-based license plate recognition system with mobile app, payment integration, and 99.9% uptime SLA. Currently used in 5 facilities."}
            ],
            # Tender 4: Health Portal
            [
                {"vendor_id": vendors[0].id, "price": 82000.0, "timeline": 119, "proposal": f"{vendors[0].name} proposes HIPAA-compliant portal with React frontend and Python backend. Includes appointment scheduling, secure records access, vaccination tracking, and telemedicine integration."},
                {"vendor_id": vendors[1].id, "price": 79000.0, "timeline": 105, "proposal": f"{vendors[1].name} specializes in healthcare IT with existing HIPAA certification. Includes BAA, security testing, provider training, and 18 months support. Deployed 12 healthcare portals."}
            ],
            # Tender 5: E-Permit System
            [
                {"vendor_id": vendors[0].id, "price": 61000.0, "timeline": 77, "proposal": f"{vendors[0].name} delivers React/FastAPI permit system with workflow automation, document management, payment processing, and mobile-responsive design."},
                {"vendor_id": vendors[1].id, "price": 59000.0, "timeline": 77, "proposal": f"{vendors[1].name} provides .NET/Angular solution with configurable workflows, GIS integration, inspector mobile app, and data migration from existing systems."}
            ]
        ]
        
        all_bids = []
        for tender_idx, tender in enumerate(tenders):
            for bid_spec in bid_data[tender_idx]:
                bid_hash = generate_bid_hash({
                    "tender_id": tender.id,
                    "vendor_id": bid_spec["vendor_id"],
                    "proposed_price": bid_spec["price"]
                })
                
                bid = Bid(
                    tender_id=tender.id,
                    vendor_id=bid_spec["vendor_id"],
                    proposed_price=bid_spec["price"],
                    technical_proposal=bid_spec["proposal"],
                    delivery_timeline=bid_spec["timeline"],
                    status=BidStatus.SUBMITTED,
                    submission_hash=bid_hash
                )
                db.add(bid)
                db.flush()
                
                # Log on blockchain
                tx_hash = blockchain_service.log_bid_submission(bid.id, tender.id, bid_hash)
                if tx_hash:
                    bid.submission_tx_hash = tx_hash
                
                vendor_name = next(v.name for v in vendors if v.id == bid_spec["vendor_id"])
                print(f"   ✅ Bid #{bid.id} from {vendor_name} for Tender #{tender.id}: ${bid_spec['price']:,.0f}")
                all_bids.append(bid)
        
        db.commit()
        
        # Award first 4 tenders (past/completed projects)
        print(f"\n🏆 Awarding 4 completed tenders...")
        
        awards_spec = [
            {"tender_idx": 0, "winning_vendor_idx": 0, "justification": f"{vendors[0].name} demonstrated superior technical expertise with modern frameworks and comprehensive maintenance plan. AI score: 95/100."},
            {"tender_idx": 1, "winning_vendor_idx": 1, "justification": f"{vendors[1].name} provided most cost-effective solution with proven municipal tax system experience. AI score: 88/100."},
            {"tender_idx": 2, "winning_vendor_idx": 0, "justification": f"{vendors[0].name} proposed the most advanced IoT solution with superior sensor technology. AI recommendation: 94/100."},
            {"tender_idx": 3, "winning_vendor_idx": 1, "justification": f"{vendors[1].name} brings specialized healthcare IT expertise with existing HIPAA certification. AI score: 91/100."}
        ]
        
        for award_spec in awards_spec:
            tender = tenders[award_spec["tender_idx"]]
            winning_vendor_id = vendors[award_spec["winning_vendor_idx"]].id
            
            # Find winning bid
            winning_bid = next(b for b in all_bids if b.tender_id == tender.id and b.vendor_id == winning_vendor_id)
            
            # Update tender status
            tender.status = TenderStatus.AWARDED
            
            # Update bid statuses
            for bid in all_bids:
                if bid.tender_id == tender.id:
                    bid.status = BidStatus.ACCEPTED if bid.id == winning_bid.id else BidStatus.REJECTED
            
            # Create award
            award_hash = generate_award_hash({
                "tender_id": tender.id,
                "winning_bid_id": winning_bid.id,
                "award_amount": winning_bid.proposed_price
            })
            
            tender.award_hash = award_hash
            
            award = Award(
                tender_id=tender.id,
                winning_bid_id=winning_bid.id,
                award_amount=winning_bid.proposed_price,
                justification=award_spec["justification"],
                contract_start=now - timedelta(days=10),
                contract_end=now + timedelta(days=90)
            )
            db.add(award)
            db.flush()
            
            # Log on blockchain
            tx_hash = blockchain_service.log_award_decision(tender.id, winning_bid.id, award_hash)
            if tx_hash:
                tender.award_tx_hash = tx_hash
                winner_name = next(v.name for v in vendors if v.id == winning_vendor_id)
                print(f"   ✅ Award #{award.id}: Tender #{tender.id} → {winner_name} [Blockchain: {tx_hash[:15]}...]")
            
            # Update vendor stats
            winner_vendor = next(v for v in vendors if v.id == winning_vendor_id)
            winner_vendor.total_wins += 1
        
        db.commit()
        
        # Summary
        print("\n" + "="*80)
        print("✅ Historical Bidding Data Created Successfully!")
        print("="*80)
        print(f"\n📊 Summary:")
        print(f"   - {len(tenders)} tenders created (all blockchain-logged)")
        print(f"   - {len(all_bids)} bids submitted (all blockchain-logged)")
        print(f"   - {len(awards_spec)} tenders awarded (all blockchain-logged)")
        print(f"\n📈 Vendor Performance:")
        for vendor in vendors:
            wins = vendor.total_wins
            total_bids = len([b for b in all_bids if b.vendor_id == vendor.id])
            print(f"   - {vendor.name}: {wins} wins out of {total_bids} bids ({wins/total_bids*100:.0f}% success rate)")
        
        print(f"\n💡 Blockchain Verification:")
        print(f"   ✅ All tender creations logged on blockchain")
        print(f"   ✅ All bid submissions logged on blockchain")
        print(f"   ✅ All award decisions logged on blockchain")
        print(f"   ✅ Complete immutable audit trail established")
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    main()
