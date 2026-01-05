"""
Demo Data Script - Procurement Transparency Platform
Populate the database with sample data for testing
"""

import requests
import json
from datetime import datetime, timedelta

BASE_URL = "http://localhost:8000"

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
    print("🏛️  Procurement Transparency Platform - Demo Data Script")
    print("=" * 70)
    
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
    
    # 1. Register Vendors
    print("\n1️⃣  Registering Vendors...")
    vendors = [
        {
            "name": "TechCorp Solutions",
            "email": "contact@techcorp.com",
            "company_registration": "TC-2024-001",
            "phone": "+1-555-0101",
            "address": "123 Tech Street, Silicon Valley, CA"
        },
        {
            "name": "WebPro Development",
            "email": "info@webpro.com",
            "company_registration": "WP-2024-002",
            "phone": "+1-555-0102",
            "address": "456 Web Avenue, Austin, TX"
        },
        {
            "name": "QuickDev Studios",
            "email": "hello@quickdev.com",
            "company_registration": "QD-2024-003",
            "phone": "+1-555-0103",
            "address": "789 Dev Road, Seattle, WA"
        },
        {
            "name": "Enterprise Systems Inc",
            "email": "sales@entsys.com",
            "company_registration": "ES-2024-004",
            "phone": "+1-555-0104",
            "address": "321 Enterprise Blvd, New York, NY"
        }
    ]
    
    vendor_ids = []
    for vendor in vendors:
        params = {
            "name": vendor["name"],
            "email": vendor["email"],
            "company_registration": vendor["company_registration"],
            "phone": vendor.get("phone"),
            "address": vendor.get("address")
        }
        resp = requests.post(f"{BASE_URL}/vendor/register", params=params)
        print_response(resp, f"Registering {vendor['name']}")
        if resp.status_code == 200:
            vendor_ids.append(resp.json()["id"])
    
    if len(vendor_ids) == 0:
        print("❌ No vendors registered. Exiting.")
        return
    
    print(f"\n✅ Registered {len(vendor_ids)} vendors: {vendor_ids}")
    
    # 2. Create Tenders
    print("\n2️⃣  Creating Tenders...")
    now = datetime.utcnow()
    tenders = [
        {
            "title": "E-Government Portal Development",
            "description": "Development of a comprehensive e-government portal for citizen services. Must include payment gateway integration, document management, user authentication, and mobile responsiveness. Expected to handle 100,000+ users.",
            "category": "IT Services",
            "budget": 150000.0,
            "department": "Department of Information Technology",
            "deadline": (now + timedelta(days=30)).isoformat()
        },
        {
            "title": "Municipal Water Management System",
            "description": "IoT-based water monitoring and management system for the municipal water supply. Should include real-time monitoring, leak detection, automated billing, and mobile app for citizens to track water usage and pay bills.",
            "category": "Infrastructure Technology",
            "budget": 250000.0,
            "department": "Department of Water Resources",
            "deadline": (now + timedelta(days=45)).isoformat()
        },
        {
            "title": "Public School Management Software",
            "description": "Comprehensive school management system for 50 public schools. Features needed: student enrollment, attendance tracking, grade management, parent portal, teacher collaboration tools, and reporting dashboard.",
            "category": "Education Technology",
            "budget": 100000.0,
            "department": "Department of Education",
            "deadline": (now + timedelta(days=60)).isoformat()
        }
    ]
    
    tender_ids = []
    for tender in tenders:
        resp = requests.post(f"{BASE_URL}/gov/tenders", json=tender)
        print_response(resp, f"Creating Tender: {tender['title']}")
        if resp.status_code == 200:
            tender_ids.append(resp.json()["id"])
    
    if len(tender_ids) == 0:
        print("❌ No tenders created. Exiting.")
        return
    
    print(f"\n✅ Created {len(tender_ids)} tenders: {tender_ids}")
    
    # 3. Submit Bids
    print("\n3️⃣  Submitting Bids...")
    
    # Bids for first tender (E-Government Portal)
    tender_1_bids = [
        {
            "tender_id": tender_ids[0],
            "vendor_id": vendor_ids[0],
            "proposed_price": 135000.0,
            "technical_proposal": "TechCorp proposes a modern React-based frontend with FastAPI backend, PostgreSQL database, and AWS cloud hosting. Our team has 10+ years of experience in government portal development. We will deliver a scalable, secure, and user-friendly platform with complete documentation and 6 months of free support. Timeline includes: Planning (2 weeks), Development (10 weeks), Testing (2 weeks), Deployment (1 week).",
            "delivery_timeline": 105
        },
        {
            "tender_id": tender_ids[0],
            "vendor_id": vendor_ids[1],
            "proposed_price": 145000.0,
            "technical_proposal": "WebPro specializes in government digital solutions. We propose a Next.js frontend with Node.js backend, MongoDB database, and Azure hosting. Our solution includes advanced security features, WCAG 2.1 AA accessibility compliance, and multi-language support. We have successfully delivered 15+ government projects. Includes 1 year of maintenance and training for government staff.",
            "delivery_timeline": 90
        },
        {
            "tender_id": tender_ids[0],
            "vendor_id": vendor_ids[2],
            "proposed_price": 95000.0,
            "technical_proposal": "QuickDev offers rapid development using WordPress and off-the-shelf plugins. Basic functionality with some customization. Limited scalability but fast delivery. No cloud hosting included, can deploy to existing servers.",
            "delivery_timeline": 45
        }
    ]
    
    # Bids for second tender (Water Management)
    tender_2_bids = [
        {
            "tender_id": tender_ids[1],
            "vendor_id": vendor_ids[0],
            "proposed_price": 240000.0,
            "technical_proposal": "TechCorp proposes an IoT-enabled water management system using LoRaWAN sensors, real-time data analytics dashboard, and mobile apps for both administrators and citizens. Integration with existing billing systems. Machine learning algorithms for leak detection and demand forecasting. Includes hardware procurement, installation, and 2 years warranty.",
            "delivery_timeline": 180
        },
        {
            "tender_id": tender_ids[1],
            "vendor_id": vendor_ids[3],
            "proposed_price": 235000.0,
            "technical_proposal": "Enterprise Systems Inc brings 20 years of municipal infrastructure experience. Our solution uses industry-standard SCADA integration, real-time monitoring with predictive maintenance, and comprehensive reporting. Cloud-based platform with on-premise backup. Includes complete training program for municipal staff and 3 years of support. We have deployed similar systems in 30+ cities.",
            "delivery_timeline": 150
        }
    ]
    
    # Bids for third tender (School Management)
    tender_3_bids = [
        {
            "tender_id": tender_ids[2],
            "vendor_id": vendor_ids[1],
            "proposed_price": 92000.0,
            "technical_proposal": "WebPro's education platform is specifically designed for public schools. Features include student information system, learning management system integration, parent communication portal, and analytics dashboard. Mobile apps for iOS and Android. Cloud-based with automatic backups. Includes teacher and administrator training. Built with privacy and FERPA compliance in mind.",
            "delivery_timeline": 120
        },
        {
            "tender_id": tender_ids[2],
            "vendor_id": vendor_ids[2],
            "proposed_price": 92000.0,
            "technical_proposal": "QuickDev offers a streamlined school management solution using open-source platforms with custom modifications. Basic features for student management, attendance, and grading. Limited mobile support. Quick implementation with standard features.",
            "delivery_timeline": 60
        },
        {
            "tender_id": tender_ids[2],
            "vendor_id": vendor_ids[3],
            "proposed_price": 105000.0,
            "technical_proposal": "Enterprise Systems Inc provides enterprise-grade school management with advanced features: AI-powered student performance analytics, automated report card generation, integration with state education databases, comprehensive parent-teacher communication tools, and district-wide analytics. Proven track record with 100+ school districts. Includes 5 years of support and unlimited users.",
            "delivery_timeline": 150
        }
    ]
    
    all_bids = tender_1_bids + tender_2_bids + tender_3_bids
    
    for bid in all_bids:
        resp = requests.post(f"{BASE_URL}/vendor/bids", json=bid)
        vendor_name = vendors[bid["vendor_id"]-1]["name"] if bid["vendor_id"]-1 < len(vendors) else "Unknown"
        print_response(resp, f"Bid from {vendor_name} for Tender #{bid['tender_id']}")
    
    print(f"\n✅ Submitted {len(all_bids)} bids")
    
    # 4. Get AI Recommendations for first tender
    print("\n4️⃣  Getting AI Recommendations for First Tender...")
    resp = requests.get(f"{BASE_URL}/gov/tenders/{tender_ids[0]}/recommendations")
    print_response(resp, f"AI Recommendations for Tender #{tender_ids[0]}")
    
    # 5. Close first tender
    print("\n5️⃣  Closing First Tender...")
    resp = requests.post(f"{BASE_URL}/gov/tenders/{tender_ids[0]}/close")
    print_response(resp, f"Closing Tender #{tender_ids[0]}")
    
    # 6. Award first tender to best bid
    print("\n6️⃣  Awarding First Tender...")
    # Assuming WebPro (vendor_ids[1]) gets the award based on AI recommendation
    award_data = {
        "tender_id": tender_ids[0],
        "winning_bid_id": 2,  # This would be the bid ID, adjust if needed
        "justification": "WebPro Development demonstrates the best combination of technical expertise, government project experience, and reasonable pricing. Their solution includes advanced security features, accessibility compliance, and comprehensive support. The AI analysis confirmed strong scores across all criteria with no anomalies detected.",
        "contract_start": (now + timedelta(days=7)).isoformat(),
        "contract_end": (now + timedelta(days=97)).isoformat()
    }
    
    resp = requests.post(f"{BASE_URL}/gov/awards", json=award_data)
    print_response(resp, "Creating Award")
    
    # 7. Get awarded tenders (public view)
    print("\n7️⃣  Viewing Awarded Tenders (Public Portal)...")
    resp = requests.get(f"{BASE_URL}/public/tenders/awarded")
    print_response(resp, "Awarded Tenders")
    
    # 8. Submit public rating
    if resp.status_code == 200 and len(resp.json()) > 0:
        print("\n8️⃣  Submitting Public Ratings...")
        # Simulate public rating after project "completion"
        rating_data = {
            "award_id": 1,  # First award
            "rating": 5,
            "feedback": "Excellent work by WebPro! The e-government portal is user-friendly, fast, and secure. Citizens are very happy with the new system. Project was delivered on time and within budget.",
            "citizen_name": "John Smith"
        }
        
        resp = requests.post(f"{BASE_URL}/public/ratings", json=rating_data)
        print_response(resp, "Public Rating Submission")
    
    print("\n" + "="*70)
    print("✅ Demo data created successfully!")
    print("="*70)
    print("\n📊 Summary:")
    print(f"   - {len(vendor_ids)} vendors registered")
    print(f"   - {len(tender_ids)} tenders created")
    print(f"   - {len(all_bids)} bids submitted")
    print(f"   - 1 tender awarded")
    print(f"   - 1 public rating submitted")
    print("\n🌐 Next Steps:")
    print("   1. Open http://localhost:5173 in your browser")
    print("   2. Navigate to different portals to see the data")
    print("   3. Try AI recommendations, transparency views, etc.")
    print("\n💡 Tip: Check API docs at http://localhost:8000/docs")
    print("="*70 + "\n")

if __name__ == "__main__":
    main()
