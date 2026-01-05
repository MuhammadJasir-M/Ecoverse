"""
Script to initialize the government account with an access code.
Run this once to set up the government account.

Usage:
    python -m app.scripts.init_government_account <access_code>
    
Or set the access code via environment variable:
    GOVERNMENT_ACCESS_CODE=your_code python -m app.scripts.init_government_account
"""
import sys
import os
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from app.db.session import SessionLocal
from app.db.models import GovernmentAccount
from app.services.auth import get_password_hash

def init_government_account(access_code: str):
    """Initialize or update the government account"""
    db = SessionLocal()
    try:
        # Check if account exists
        gov_account = db.query(GovernmentAccount).first()
        
        if gov_account:
            # Update existing account
            gov_account.access_code_hash = get_password_hash(access_code)
            print("✅ Government account access code updated")
        else:
            # Create new account
            gov_account = GovernmentAccount(
                access_code_hash=get_password_hash(access_code)
            )
            db.add(gov_account)
            print("✅ Government account created")
        
        db.commit()
        print(f"✅ Access code set successfully")
        print(f"⚠️  Keep this access code secure. It cannot be recovered if lost.")
        
    except Exception as e:
        db.rollback()
        print(f"❌ Error: {e}")
        sys.exit(1)
    finally:
        db.close()

if __name__ == "__main__":
    # Get access code from command line or environment
    if len(sys.argv) > 1:
        access_code = sys.argv[1]
    elif os.getenv("GOVERNMENT_ACCESS_CODE"):
        access_code = os.getenv("GOVERNMENT_ACCESS_CODE")
    else:
        print("Usage: python -m app.scripts.init_government_account <access_code>")
        print("   Or: GOVERNMENT_ACCESS_CODE=code python -m app.scripts.init_government_account")
        sys.exit(1)
    
    if len(access_code) < 8:
        print("⚠️  Warning: Access code should be at least 8 characters long")
    
    init_government_account(access_code)




