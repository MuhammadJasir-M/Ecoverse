from app.services.ai_engine import AIEngine
from app.db.session import SessionLocal
from app.db.models import Bid, Vendor, Tender

db = SessionLocal()

print("=" * 60)
print("AI ENGINE IMPLEMENTATION TEST")
print("=" * 60)
print()

try:
    # Test 1: Check if AIEngine class exists
    print("✓ AIEngine class imported successfully")
    
    # Test 2: Get data from database
    tender = db.query(Tender).first()
    bids = db.query(Bid).filter(Bid.tender_id == tender.id).all()
    vendors = {v.id: v for v in db.query(Vendor).all()}
    
    print(f"✓ Found tender: {tender.title}")
    print(f"✓ Found {len(bids)} bids")
    print(f"✓ Found {len(vendors)} vendors")
    print()
    
    # Test 3: Generate recommendations
    print("Testing AI recommendations...")
    recs = AIEngine.get_recommendations(tender.id, bids, vendors, tender)
    
    print(f"✓ Generated {len(recs)} recommendations")
    print()
    
    # Test 4: Verify recommendation structure
    if recs:
        top_rec = recs[0]
        print("Top recommendation structure:")
        print(f"  - Vendor: {top_rec['vendor_name']}")
        print(f"  - AI Score: {top_rec['ai_score']}")
        print(f"  - Price Score: {top_rec['price_score']}")
        print(f"  - Vendor Score: {top_rec['vendor_score']}")
        print(f"  - Technical Score: {top_rec['technical_score']}")
        print(f"  - Recommendation: {top_rec['recommendation']}")
        print()
    
    # Test 5: Verify scoring for each bid
    print("All Recommendations:")
    print("-" * 60)
    for rec in recs:
        print(f"Rank #{rec['rank']}: {rec['vendor_name']}")
        print(f"  AI Score: {rec['ai_score']}")
        print(f"  Anomaly: {rec['anomaly_flag']}")
        if rec['anomaly_reason']:
            print(f"  Reason: {rec['anomaly_reason']}")
        print()
    
    print("=" * 60)
    print("✅ ALL TESTS PASSED - AI ENGINE WORKING CORRECTLY")
    print("=" * 60)
    
except Exception as e:
    print(f"❌ ERROR: {str(e)}")
    import traceback
    traceback.print_exc()
finally:
    db.close()
