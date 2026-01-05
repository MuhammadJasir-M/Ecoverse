from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from pydantic import BaseModel
from app.db.session import get_db
from app.db.models import GovernmentAccount, Vendor
from app.services.auth import (
    verify_password,
    get_password_hash,
    create_access_token,
    get_current_user
)
from datetime import datetime
import secrets

router = APIRouter(prefix="/auth", tags=["Authentication"])

# Request/Response Models
class GovernmentLoginRequest(BaseModel):
    access_code: str

class VendorLoginRequest(BaseModel):
    vendor_id: str
    password: str

class VendorRegisterRequest(BaseModel):
    vendor_id: str
    password: str
    name: str
    email: str
    company_registration: str
    phone: str = None
    address: str = None

class LoginResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    role: str
    user_id: int
    vendor_id: str = None
    name: str = None

@router.post("/government/login", response_model=LoginResponse)
def government_login(
    request: GovernmentLoginRequest,
    db: Session = Depends(get_db)
):
    """Government login with access code"""
    
    # Get the government account (there should only be one)
    gov_account = db.query(GovernmentAccount).first()
    
    if not gov_account:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Government account not configured"
        )
    
    # Verify access code
    if not verify_password(request.access_code, gov_account.access_code_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid access code"
        )
    
    # Update last login
    gov_account.last_login = datetime.utcnow()
    db.commit()
    
    # Create token
    access_token = create_access_token(
        data={"role": "government", "user_id": gov_account.id}
    )
    
    return LoginResponse(
        access_token=access_token,
        role="government",
        user_id=gov_account.id
    )

@router.post("/vendor/login", response_model=LoginResponse)
def vendor_login(
    request: VendorLoginRequest,
    db: Session = Depends(get_db)
):
    """Vendor login with vendor ID and password"""
    
    # Find vendor by vendor_id
    vendor = db.query(Vendor).filter(Vendor.vendor_id == request.vendor_id).first()
    
    if not vendor:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Vendor not found"
        )
    
    if not vendor.password_hash:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Vendor account not properly set up. Please contact support."
        )
    
    # Verify password
    if not verify_password(request.password, vendor.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid password"
        )
    
    # Update last login
    vendor.last_login = datetime.utcnow()
    db.commit()
    
    # Create token
    access_token = create_access_token(
        data={"role": "vendor", "user_id": vendor.id}
    )
    
    return LoginResponse(
        access_token=access_token,
        role="vendor",
        user_id=vendor.id,
        vendor_id=vendor.vendor_id,
        name=vendor.name
    )

@router.post("/vendor/register", response_model=LoginResponse)
def vendor_register(
    request: VendorRegisterRequest,
    db: Session = Depends(get_db)
):
    """Register a new vendor with authentication"""
    
    # Check if vendor_id already exists
    existing_vendor_id = db.query(Vendor).filter(Vendor.vendor_id == request.vendor_id).first()
    if existing_vendor_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Vendor ID already exists"
        )
    
    # Check if email already exists
    existing_email = db.query(Vendor).filter(Vendor.email == request.email).first()
    if existing_email:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Vendor with this email already exists"
        )
    
    # Hash password
    password_hash = get_password_hash(request.password)
    
    # Create vendor
    vendor = Vendor(
        vendor_id=request.vendor_id,
        name=request.name,
        email=request.email,
        company_registration=request.company_registration,
        phone=request.phone,
        address=request.address,
        password_hash=password_hash,
        reputation_score=3.0
    )
    db.add(vendor)
    db.commit()
    db.refresh(vendor)
    
    # Create token for immediate login
    access_token = create_access_token(
        data={"role": "vendor", "user_id": vendor.id}
    )
    
    return LoginResponse(
        access_token=access_token,
        role="vendor",
        user_id=vendor.id,
        vendor_id=vendor.vendor_id,
        name=vendor.name
    )

@router.get("/me")
def get_current_user_info(current_user: dict = Depends(get_current_user)):
    """Get current authenticated user information"""
    return current_user

@router.post("/logout")
def logout():
    """Logout endpoint (client should discard token)"""
    return {"message": "Logged out successfully"}

