"""
Demo Data Script - Procurement Transparency Platform
Creates bidding history for existing vendor profiles with blockchain logging
"""

import requests
import json
from datetime import datetime, timedelta
import sys

BASE_URL = "http://localhost:8000"

# Existing vendor profiles (will be auto-detected)
EXISTING_VENDORS = []

def print_response(response, title):
    print(f"\n{'='*60}")
    print(f"{title}")
    print(f"{'='*60}")
    print(f"Status: {response.status_code}")
    if response.status_code >= 200 and response.status_code < 300:
        try:
            print(json.dumps(response.json(), indent=2))
        except:
            print(response.text)
    else:
        print(f"Error: {response.text}")
    print(f"{'='*60}\n")

def main():
    print("🏛️  Procurement Transparency Platform - Historical Bidding Data Script")
    print("=" * 80)
    
    # Check API health
    print("\n📡 Checking API health...")
    try:
        health = requests.get(f"{BASE_URL}/health", timeout=5)
        if health.status_code == 200:
            print("✅ API is healthy and ready!")
        else:
            print("❌ API health check failed!")
            return
    except Exception as e:
        print(f"❌ Cannot connect to API: {e}")
        print(f"   Make sure backend is running at {BASE_URL}")
        return
    
    # 0. Get Government Access Token
    print("\n🔐 Authenticating as Government...")
    try:
        gov_login = requests.post(
            f"{BASE_URL}/auth/government/login",
            json={"access_code": "admin123"}
        )
        if gov_login.status_code != 200:
            print(f"❌ Government login failed: {gov_login.text}")
            print("   Make sure government account is initialized with 'admin123'")
            return
        gov_token = gov_login.json()["access_token"]
        gov_headers = {"Authorization": f"Bearer {gov_token}"}
        print("✅ Government authenticated!")
    except Exception as e:
        print(f"❌ Authentication failed: {e}")
        return
    
    # 1. Get Existing Vendors
    print("\n1️⃣  Fetching Existing Vendor Profiles...")
    global EXISTING_VENDORS
    try:
        # Get vendors directly from database via backend
        vendors_resp = requests.get(f"{BASE_URL}/vendor/profile", headers=gov_headers)
        if vendors_resp.status_code == 200:
            EXISTING_VENDORS = vendors_resp.json() if isinstance(vendors_resp.json(), list) else []
    except:
        pass
    
    # If API doesn't work, we'll use the known vendors
    if not EXISTING_VENDORS:
        EXISTING_VENDORS = [
            {"id": 1, "vendor_id": "24CS0001", "name": "NPTN Company", "email": "nagapoojith27@gmail.com"},
            {"id": 2, "vendor_id": "24CS0555", "name": "MDJR Corporate PVT LTD", "email": "muhammadjasir126@gmail.com"}
        ]
    
    print(f"✅ Found {len(EXISTING_VENDORS)} existing vendors:")
    for v in EXISTING_VENDORS:
        print(f"   - {v['name']} (ID: {v['id']}, Vendor ID: {v.get('vendor_id', 'N/A')})")
    
    if len(EXISTING_VENDORS) < 2:
        print("❌ Need at least 2 vendors to create competitive bidding history!")
        return
    
    # 2. Create Historical Tenders (with blockchain logging)
    print("\n2️⃣  Creating Historical Tenders with Blockchain Logging...")
    now = datetime.utcnow()
    
    # Past tenders with varying timelines
    tenders = [
        {
            "title": "City Website Redesign Project",
            "description": "Complete redesign of the city's main website with modern UI/UX, mobile responsiveness, accessibility compliance, and CMS integration. Must include citizen feedback system and multilingual support.",
            "category": "Web Development",
            "budget": 75000.0,
            "department": "Department of Communications",
            "deadline": (now - timedelta(days=60)).isoformat(),  # Past project
            "created_days_ago": 90
        },
        {
            "title": "Municipal Tax Collection Software",
            "description": "Automated tax calculation and collection system for property taxes, business licenses, and other municipal fees. Should integrate with existing financial systems and provide online payment options.",
            "category": "IT Services",
            "budget": 120000.0,
            "department": "Department of Finance",
            "deadline": (now - timedelta(days=30)).isoformat(),
            "created_days_ago": 75
        },
        {
            "title": "Smart Parking Management System",
            "description": "IoT-based parking management solution for city parking lots. Real-time availability tracking, mobile app for citizens, automated payment system, and analytics dashboard for parking utilization.",
            "category": "Smart City Solutions",
            "budget": 95000.0,
            "department": "Department of Transportation",
            "deadline": (now - timedelta(days=15)).isoformat(),
            "created_days_ago": 60
        },
        {
            "title": "Public Health Portal Development",
            "description": "Health information portal for citizens with appointment booking, medical records access, vaccination tracking, and health alerts system. HIPAA compliance required.",
            "category": "Healthcare IT",
            "budget": 85000.0,
            "department": "Department of Health",
            "deadline": (now + timedelta(days=20)).isoformat(),  # Upcoming
            "created_days_ago": 45
        },
        {
            "title": "E-Permit Application System",
            "description": "Online permit application and approval system for building permits, business licenses, and event permits. Should include document upload, workflow automation, and payment processing.",
            "category": "Government Services",
            "budget": 65000.0,
            "department": "Department of Development Services",
            "deadline": (now + timedelta(days=35)).isoformat(),
            "created_days_ago": 30
        }
    ]
    
    tender_ids = []
    for tender in tenders:
        tender_data = {k: v for k, v in tender.items() if k != 'created_days_ago'}
        resp = requests.post(f"{BASE_URL}/gov/tenders", json=tender_data, headers=gov_headers)
        print_response(resp, f"Creating Tender: {tender['title'][:50]}...")
        if resp.status_code == 200:
            tender_id = resp.json()["id"]
            tender_ids.append(tender_id)
            creation_tx = resp.json().get("creation_tx_hash")
            if creation_tx:
                print(f"   ✅ Blockchain logged: {creation_tx[:20]}...")
    
    if len(tender_ids) == 0:
        print("❌ No tenders created. Exiting.")
        return
    
    print(f"\n✅ Created {len(tender_ids)} tenders with blockchain logging: {tender_ids}")
    
    # 3. Login Vendors and Submit Competitive Bids (with blockchain logging)
    print("\n3️⃣  Submitting Competitive Bids from Both Vendors...")
    
    # Authenticate both vendors
    vendor_tokens = []
    for vendor in EXISTING_VENDORS[:2]:  # Use first two vendors
        # Note: Assuming vendors have passwords set during registration
        # If not, this section may need adjustment
        print(f"   Note: Using vendor ID {vendor['id']} for bidding")
        vendor_tokens.append((vendor['id'], vendor['name']))
    
    # Create competitive bids for each tender
    all_bids = []
    bid_count = 0
    
    # Tender 1: City Website - NPTN wins with better technical proposal
    tender_1_bids = [
        {
            "tender_id": tender_ids[0],
            "vendor_id": EXISTING_VENDORS[0]['id'],  # NPTN Company
            "proposed_price": 68000.0,
            "technical_proposal": f"{EXISTING_VENDORS[0]['name']} proposes a modern, responsive website using React and Next.js framework. Our solution includes SEO optimization, Content Management System, multilingual support (English, Spanish, Chinese), WCAG 2.1 AA accessibility compliance, and mobile-first design. We'll use Azure cloud hosting for reliability and scalability. Our team has delivered 15+ government websites. Includes 1 year of free maintenance, security updates, and staff training. Project timeline: Design (2 weeks), Development (6 weeks), Testing (1 week), Deployment (1 week).",
            "delivery_timeline": 70
        },
        {
            "tender_id": tender_ids[0],
            "vendor_id": EXISTING_VENDORS[1]['id'],  # MDJR Corporate
            "proposed_price": 72000.0,
            "technical_proposal": f"{EXISTING_VENDORS[1]['name']} offers a comprehensive website solution with WordPress CMS for easy content management. Includes custom theme development, plugin integration, contact forms, news section, and document repository. Basic accessibility features and mobile responsiveness. Hosting not included but can help with setup. Our team specializes in quick delivery with standard features. Timeline: Setup (1 week), Development (5 weeks), Launch (1 week).",
            "delivery_timeline": 49
        }
    ]
    
    # Tender 2: Tax Collection - MDJR wins with competitive price and good technical
    tender_2_bids = [
        {
            "tender_id": tender_ids[1],
            "vendor_id": EXISTING_VENDORS[0]['id'],
            "proposed_price": 125000.0,
            "technical_proposal": f"{EXISTING_VENDORS[0]['name']} proposes an enterprise-grade tax collection system built with Python/FastAPI backend, React frontend, PostgreSQL database. Features include: automated tax calculation engine, payment gateway integration (credit cards, ACH, digital wallets), taxpayer portal, bulk import/export, reporting dashboard, email/SMS notifications, and integration APIs for existing financial systems. Security: encrypted data storage, PCI DSS compliance, audit logging, role-based access control. Includes comprehensive testing, documentation, and 6 months support. Timeline: Requirements (3 weeks), Development (12 weeks), Testing (2 weeks), Deployment (1 week).",
            "delivery_timeline": 126
        },
        {
            "tender_id": tender_ids[1],
            "vendor_id": EXISTING_VENDORS[1]['id'],
            "proposed_price": 110000.0,
            "technical_proposal": f"{EXISTING_VENDORS[1]['name']} provides a proven tax management solution using open-source frameworks with custom modifications. Our system handles property tax, business licenses, and miscellaneous fees with automated calculations based on configurable rules. Online payment integration with major payment processors, installment plan management, delinquency tracking, and automated reminder notifications. Web-based admin portal with real-time reporting. Built with .NET Core and SQL Server. Includes data migration from existing systems, staff training (2 sessions), and 1 year warranty support. We have successfully deployed similar systems for 8 municipalities. Timeline: Planning (2 weeks), Development (10 weeks), Testing & Migration (3 weeks).",
            "delivery_timeline": 105
        }
    ]
    
    # Tender 3: Smart Parking - Competitive, NPTN wins
    tender_3_bids = [
        {
            "tender_id": tender_ids[2],
            "vendor_id": EXISTING_VENDORS[0]['id'],
            "proposed_price": 88000.0,
            "technical_proposal": f"{EXISTING_VENDORS[0]['name']} delivers an IoT-based smart parking solution using ultrasonic sensors for real-time occupancy detection. Cloud platform built with Node.js and MongoDB for scalability. Mobile apps (iOS & Android) for citizens to find parking, reserve spots, and pay digitally. Web dashboard for parking management with analytics: peak hours, utilization rates, revenue tracking. Features automated payment with mobile wallets, QR codes, license plate recognition. Integration with city's payment gateway. Hardware included: sensors, gateway devices, signage displays. Installation, configuration, and training included. 2-year hardware warranty and software support. Timeline: Hardware procurement (3 weeks), Installation (4 weeks), Software development (6 weeks), Testing (2 weeks).",
            "delivery_timeline": 105
        },
        {
            "tender_id": tender_ids[2],
            "vendor_id": EXISTING_VENDORS[1]['id'],
            "proposed_price": 92000.0,
            "technical_proposal": f"{EXISTING_VENDORS[1]['name']} offers a comprehensive parking management system with camera-based license plate recognition technology for entry/exit tracking. Software platform includes: real-time availability display, mobile app for parking search and payment, automated billing, violation detection, and analytics dashboard. Payment integration with all major credit cards and mobile payment systems. Cloud-hosted solution with 99.9% uptime SLA. Hardware package includes cameras, barriers, display boards, and payment kiosks. Our solution is currently used in 5 commercial parking facilities with excellent results. Includes installation, setup, operator training (3 sessions), and 2 years of technical support. Timeline: Equipment delivery (4 weeks), Installation (3 weeks), Software configuration (5 weeks), Testing & Training (2 weeks).",
            "delivery_timeline": 98
        }
    ]
    
    # Tender 4: Health Portal - MDJR wins with healthcare expertise
    tender_4_bids = [
        {
            "tender_id": tender_ids[3],
            "vendor_id": EXISTING_VENDORS[0]['id'],
            "proposed_price": 82000.0,
            "technical_proposal": f"{EXISTING_VENDORS[0]['name']} proposes a HIPAA-compliant health portal using modern web technologies. Features: patient registration, appointment scheduling with calendar integration, secure document upload for medical records, vaccination record tracking with reminder system, health alerts and notifications, telemedicine integration capability, and patient-provider messaging. Built with React frontend and Python backend, encrypted database storage. Includes HIPAA compliance audit, security testing, and staff training. Cloud hosting with daily backups and disaster recovery. 1 year of support and maintenance. Timeline: Design & Security Planning (3 weeks), Development (10 weeks), HIPAA Audit (2 weeks), Testing & Training (2 weeks).",
            "delivery_timeline": 119
        },
        {
            "tender_id": tender_ids[3],
            "vendor_id": EXISTING_VENDORS[1]['id'],
            "proposed_price": 79000.0,
            "technical_proposal": f"{EXISTING_VENDORS[1]['name']} specializes in healthcare IT solutions with HIPAA compliance expertise. Our portal includes: user registration with identity verification, appointment booking system integrated with clinic calendars, secure medical records access with audit logging, vaccination tracking with CDC integration, health alerts via email/SMS, provider directory, and prescription refill requests. Built on proven healthcare platform with existing HIPAA certification. Includes BAA (Business Associate Agreement), security risk assessment, penetration testing, encrypted data transmission and storage, role-based access control, and comprehensive audit trails. Our team has deployed 12 healthcare portals for clinics and hospitals. Includes data migration, provider training (multiple sessions), patient education materials, and 18 months support. Timeline: Requirements & BAA (2 weeks), Development & Integration (9 weeks), Security Testing (2 weeks), Training & Launch (2 weeks).",
            "delivery_timeline": 105
        }
    ]
    
    # Tender 5: E-Permit System - Still open, both bid competitively
    tender_5_bids = [
        {
            "tender_id": tender_ids[4],
            "vendor_id": EXISTING_VENDORS[0]['id'],
            "proposed_price": 61000.0,
            "technical_proposal": f"{EXISTING_VENDORS[0]['name']} delivers a streamlined online permit application system. Features: online application forms for building permits, business licenses, event permits with custom workflows for each permit type, document upload and management, automated routing for approvals, payment processing integration, applicant portal to track status, email notifications at each stage, and admin dashboard for permit management. Built with React and FastAPI for fast performance. Includes integration with city's payment gateway, reporting module for permit statistics, and mobile-responsive design. Timeline: Design (2 weeks), Development (7 weeks), Testing (1 week), Training & Launch (1 week).",
            "delivery_timeline": 77
        },
        {
            "tender_id": tender_ids[4],
            "vendor_id": EXISTING_VENDORS[1]['id'],
            "proposed_price": 59000.0,
            "technical_proposal": f"{EXISTING_VENDORS[1]['name']} provides an automated permit management solution with workflow engine. Support for multiple permit types: building, electrical, plumbing, business license, special events, etc. Online application with intelligent form validation, digital document upload with virus scanning, configurable approval workflows, automated fee calculation, online payment with receipt generation, status tracking for applicants, inspector assignment and scheduling, mobile app for inspectors, GIS integration for property location, and comprehensive reporting. Built with .NET and Angular. Includes permit data migration from existing systems, process mapping workshop, staff training, and public tutorials. 1 year warranty support. Timeline: Configuration (2 weeks), Development (6 weeks), Data Migration & Testing (2 weeks), Go-Live Support (1 week).",
            "delivery_timeline": 77
        }
    ]
    
    all_bids = tender_1_bids + tender_2_bids + tender_3_bids + tender_4_bids + tender_5_bids
    
    # Submit all bids (blockchain will be logged automatically by backend)
    for bid in all_bids:
        resp = requests.post(f"{BASE_URL}/vendor/bids", json=bid, headers=gov_headers)
        vendor_name = next((v['name'] for v in EXISTING_VENDORS if v['id'] == bid['vendor_id']), "Unknown")
        if resp.status_code == 200:
            bid_id = resp.json().get("id")
            submission_tx = resp.json().get("submission_tx_hash")
            print(f"   ✅ Bid #{bid_id} from {vendor_name} for Tender #{bid['tender_id']}")
            if submission_tx:
                print(f"      Blockchain: {submission_tx[:20]}...")
            bid_count += 1
        else:
            print(f"   ❌ Failed: {resp.text[:100]}")
    
    print(f"\n✅ Submitted {bid_count} bids with blockchain logging")
    
    # 4. Get AI Recommendations and Award Completed Projects (with blockchain logging)
    print("\n4️⃣  Processing AI Recommendations and Awarding Completed Projects...")
    
    # Award first 3 tenders (past/completed projects)
    awards_to_create = [
        {
            "tender_id": tender_ids[0],
            "winner_vendor_id": EXISTING_VENDORS[0]['id'],  # NPTN wins Tender 1
            "winning_bid_id": None,  # Will be determined
            "justification": f"{EXISTING_VENDORS[0]['name']} demonstrated superior technical expertise with modern frameworks, excellent accessibility compliance, and comprehensive maintenance plan. AI analysis showed highest scores in technical capability (95/100) and vendor reliability (92/100). The proposed solution exceeds requirements with multilingual support and robust security features. Price is competitive at $68,000 vs budget of $75,000.",
            "days_offset": 7  # Awarded 7 days after tender creation
        },
        {
            "tender_id": tender_ids[1],
            "winner_vendor_id": EXISTING_VENDORS[1]['id'],  # MDJR wins Tender 2
            "winning_bid_id": None,
            "justification": f"{EXISTING_VENDORS[1]['name']} provided the most cost-effective solution at $110,000 with proven experience in municipal tax systems. AI analysis confirmed strong technical proposal (88/100) with 8 successful deployments. The solution includes comprehensive data migration and extended training, which are critical for this complex system. No anomalies detected. Price is $10,000 under budget with excellent value proposition.",
            "days_offset": 10
        },
        {
            "tender_id": tender_ids[2],
            "winner_vendor_id": EXISTING_VENDORS[0]['id'],  # NPTN wins Tender 3
            "winning_bid_id": None,
            "justification": f"{EXISTING_VENDORS[0]['name']} proposed the most advanced IoT solution with superior sensor technology and comprehensive mobile app. AI recommendation score: 94/100 (highest among all bids). The solution includes hardware warranty and demonstrated expertise in smart city implementations. While slightly under budget at $88,000, the technical advantages and proven reliability justify the selection.",
            "days_offset": 12
        },
        {
            "tender_id": tender_ids[3],
            "winner_vendor_id": EXISTING_VENDORS[1]['id'],  # MDJR wins Tender 4
            "winning_bid_id": None,
            "justification": f"{EXISTING_VENDORS[1]['name']} brings specialized healthcare IT expertise with 12 successfully deployed healthcare portals. AI analysis: Technical score 91/100, Compliance score 98/100 (HIPAA expertise), Price competitiveness 96/100. The existing HIPAA certification and BAA inclusion significantly reduce implementation risk. 18 months of support provides excellent long-term value. Strong recommendation from AI engine with no anomalies detected.",
            "days_offset": 15
        }
    ]
    
    awarded_count = 0
    for award_spec in awards_to_create:
        tender_id = award_spec['tender_id']
        
        # Get AI recommendations first
        print(f"\n   Getting AI recommendations for Tender #{tender_id}...")
        rec_resp = requests.get(f"{BASE_URL}/gov/tenders/{tender_id}/recommendations", headers=gov_headers)
        if rec_resp.status_code == 200:
            recommendations = rec_resp.json().get("recommendations", [])
            print(f"   ✅ AI analyzed {len(recommendations)} bids")
            
            # Find the winning bid ID
            winning_bid = next((rec for rec in recommendations 
                              if rec.get("vendor_id") == award_spec['winner_vendor_id']), None)
            
            if winning_bid:
                award_spec['winning_bid_id'] = winning_bid['bid_id']
                
                # Close the tender
                close_resp = requests.post(f"{BASE_URL}/gov/tenders/{tender_id}/close", headers=gov_headers)
                if close_resp.status_code == 200:
                    print(f"   ✅ Tender #{tender_id} closed")
                
                # Create award
                award_data = {
                    "tender_id": tender_id,
                    "winning_bid_id": award_spec['winning_bid_id'],
                    "justification": award_spec['justification'],
                    "contract_start": (now - timedelta(days=award_spec['days_offset'] - 5)).isoformat(),
                    "contract_end": (now + timedelta(days=90)).isoformat()
                }
                
                award_resp = requests.post(f"{BASE_URL}/gov/awards", json=award_data, headers=gov_headers)
                if award_resp.status_code == 200:
                    award_id = award_resp.json().get("id")
                    award_tx = award_resp.json().get("award_tx_hash")
                    winner_name = next((v['name'] for v in EXISTING_VENDORS 
                                      if v['id'] == award_spec['winner_vendor_id']), "Unknown")
                    print(f"   ✅ Award #{award_id} created - Winner: {winner_name}")
                    if award_tx:
                        print(f"      Blockchain: {award_tx[:20]}...")
                    awarded_count += 1
                else:
                    print(f"   ❌ Award failed: {award_resp.text[:100]}")
        else:
            print(f"   ❌ AI recommendations failed: {rec_resp.text[:100]}")
    
    print(f"\n✅ Awarded {awarded_count} tenders with blockchain logging")
    
    # 5. Submit Public Ratings for Completed Projects
    print("\n5️⃣  Submitting Public Ratings for Completed Projects...")
    resp = requests.get(f"{BASE_URL}/public/tenders/awarded")
    
    if resp.status_code == 200 and len(resp.json()) > 0:
        awarded_tenders = resp.json()
        public_ratings = [
            {
                "rating": 5,
                "feedback": f"Outstanding work by {EXISTING_VENDORS[0]['name']}! The new city website is modern, fast, and very easy to navigate. Citizens love the multilingual support and mobile app. Project delivered ahead of schedule with excellent quality.",
                "citizen_name": "Sarah Johnson"
            },
            {
                "rating": 4,
                "feedback": f"Great job by {EXISTING_VENDORS[1]['name']}. The tax collection system works smoothly and online payments are convenient. A few minor bugs in the first week but they were quickly fixed. Overall very satisfied with the new system.",
                "citizen_name": "Michael Chen"
            },
            {
                "rating": 5,
                "feedback": f"{EXISTING_VENDORS[0]['name']} delivered an excellent smart parking solution. Finding parking downtown is now so much easier! The mobile app is intuitive and payment is seamless. Highly recommend!",
                "citizen_name": "Emily Rodriguez"
            },
            {
                "rating": 5,
                "feedback": f"The new health portal by {EXISTING_VENDORS[1]['name']} is fantastic! Booking appointments online saves so much time. Medical records are easy to access and the vaccination tracker is very helpful. Secure and reliable system.",
                "citizen_name": "David Thompson"
            }
        ]
        
        rating_count = 0
        for idx, rating_data in enumerate(public_ratings[:len(awarded_tenders)]):
            rating_data['award_id'] = awarded_tenders[idx]['award_id']
            rating_resp = requests.post(f"{BASE_URL}/public/ratings", json=rating_data)
            if rating_resp.status_code == 200:
                print(f"   ✅ Rating submitted by {rating_data['citizen_name']}: {rating_data['rating']}/5")
                rating_count += 1
        
        print(f"\n✅ Submitted {rating_count} public ratings")
    
    # 6. Summary and blockchain verification
    print("\n6️⃣  Verifying Blockchain Records...")
    resp = requests.get(f"{BASE_URL}/public/tenders/awarded")
    if resp.status_code == 200:
        awarded = resp.json()
        blockchain_verified = [t for t in awarded if t.get('creation_tx') and t.get('award_tx')]
        print(f"   ✅ Total awarded tenders: {len(awarded)}")
        print(f"   ✅ Blockchain verified: {len(blockchain_verified)}")
        for tender in blockchain_verified:
            print(f"      - Tender #{tender['tender_id']}: {tender['title'][:50]}...")
            print(f"        Creation TX: {tender['creation_tx'][:20]}...")
            print(f"        Award TX: {tender['award_tx'][:20]}...")
    
    print("\n" + "="*80)
    print("✅ Historical Bidding Data Created Successfully with Blockchain Logging!")
    print("=" * 80)
    print("\n📊 Summary:")
    print(f"   - {len(EXISTING_VENDORS)} existing vendors used")
    print(f"   - {len(tender_ids)} historical tenders created")
    print(f"   - {bid_count} competitive bids submitted")
    print(f"   - {awarded_count} tenders awarded")
    print(f"   - All events logged on blockchain for transparency")
    print("\n📈 Vendor Performance:")
    for vendor in EXISTING_VENDORS[:2]:
        wins = sum(1 for a in awards_to_create if a['winner_vendor_id'] == vendor['id'])
        total_bids = len([b for b in all_bids if b['vendor_id'] == vendor['id']])
        print(f"   - {vendor['name']}: {wins} wins out of {total_bids} bids ({wins/total_bids*100:.0f}% success rate)")
    print("\n🌐 Next Steps:")
    print("   1. Open http://localhost:5173 in your browser")
    print("   2. Login as Government (admin123) to see all tenders and awards")
    print("   3. Login as Vendor to see bidding history")
    print("   4. Visit Public Portal to see blockchain-verified transparency data")
    print("\n💡 Blockchain Security:")
    print("   ✅ All tender creations logged on blockchain")
    print("   ✅ All bid submissions logged on blockchain")
    print("   ✅ All award decisions logged on blockchain")
    print("   ✅ Immutable audit trail for complete transparency")
    print("\n💡 Tip: Check API docs at http://localhost:8000/docs")
    print("="*80 + "\n")

if __name__ == "__main__":
    main()
