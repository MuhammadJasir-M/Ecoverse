from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Text, Boolean, Enum
from sqlalchemy.orm import relationship
from datetime import datetime
import enum
from app.db.session import Base

class TenderStatus(str, enum.Enum):
    DRAFT = "draft"
    OPEN = "open"
    CLOSED = "closed"
    AWARDED = "awarded"

class BidStatus(str, enum.Enum):
    SUBMITTED = "submitted"
    UNDER_REVIEW = "under_review"
    ACCEPTED = "accepted"
    REJECTED = "rejected"

class Tender(Base):
    __tablename__ = "tenders"
    
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(500), nullable=False)
    description = Column(Text, nullable=False)
    category = Column(String(100), nullable=False)
    budget = Column(Float, nullable=False)
    department = Column(String(200), nullable=False)
    deadline = Column(DateTime, nullable=False)
    status = Column(Enum(TenderStatus), default=TenderStatus.DRAFT)
    
    # Blockchain audit
    creation_hash = Column(String(66), nullable=True)
    creation_tx_hash = Column(String(66), nullable=True)
    award_hash = Column(String(66), nullable=True)
    award_tx_hash = Column(String(66), nullable=True)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    bids = relationship("Bid", back_populates="tender", cascade="all, delete-orphan")
    award = relationship("Award", back_populates="tender", uselist=False)

class GovernmentAccount(Base):
    __tablename__ = "government_accounts"
    
    id = Column(Integer, primary_key=True, index=True)
    access_code_hash = Column(String(255), nullable=False, unique=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    last_login = Column(DateTime, nullable=True)

class Vendor(Base):
    __tablename__ = "vendors"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(300), nullable=False)
    email = Column(String(200), unique=True, nullable=False, index=True)
    company_registration = Column(String(100), unique=True)
    phone = Column(String(20))
    address = Column(Text)
    
    # Authentication
    password_hash = Column(String(255), nullable=True)  # Nullable for backward compatibility
    vendor_id = Column(String(100), unique=True, nullable=True, index=True)  # Login ID
    
    # Reputation metrics
    reputation_score = Column(Float, default=0.0)
    completed_projects = Column(Integer, default=0)
    total_wins = Column(Integer, default=0)
    average_rating = Column(Float, default=0.0)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    last_login = Column(DateTime, nullable=True)
    
    bids = relationship("Bid", back_populates="vendor")

class Bid(Base):
    __tablename__ = "bids"
    
    id = Column(Integer, primary_key=True, index=True)
    tender_id = Column(Integer, ForeignKey("tenders.id"), nullable=False)
    vendor_id = Column(Integer, ForeignKey("vendors.id"), nullable=False)
    
    proposed_price = Column(Float, nullable=False)
    technical_proposal = Column(Text, nullable=False)
    delivery_timeline = Column(Integer, nullable=False)  # in days
    
    status = Column(Enum(BidStatus), default=BidStatus.SUBMITTED)
    
    # AI Scoring
    ai_score = Column(Float, nullable=True)
    price_score = Column(Float, nullable=True)
    vendor_score = Column(Float, nullable=True)
    technical_score = Column(Float, nullable=True)
    anomaly_flag = Column(Boolean, default=False)
    anomaly_reason = Column(Text, nullable=True)
    
    # Blockchain
    submission_hash = Column(String(66), nullable=True)
    submission_tx_hash = Column(String(66), nullable=True)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    
    tender = relationship("Tender", back_populates="bids")
    vendor = relationship("Vendor", back_populates="bids")

class Award(Base):
    __tablename__ = "awards"
    
    id = Column(Integer, primary_key=True, index=True)
    tender_id = Column(Integer, ForeignKey("tenders.id"), nullable=False, unique=True)
    winning_bid_id = Column(Integer, ForeignKey("bids.id"), nullable=False)
    
    justification = Column(Text, nullable=False)
    award_amount = Column(Float, nullable=False)
    contract_start = Column(DateTime, nullable=False)
    contract_end = Column(DateTime, nullable=False)
    
    # Public feedback
    public_rating = Column(Float, nullable=True)
    public_feedback_count = Column(Integer, default=0)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    
    tender = relationship("Tender", back_populates="award")
    winning_bid = relationship("Bid")
    ratings = relationship("PublicRating", back_populates="award")

class PublicRating(Base):
    __tablename__ = "public_ratings"
    
    id = Column(Integer, primary_key=True, index=True)
    award_id = Column(Integer, ForeignKey("awards.id"), nullable=False)
    
    rating = Column(Integer, nullable=False)  # 1-5
    feedback = Column(Text, nullable=True)
    citizen_name = Column(String(200), nullable=True)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    
    award = relationship("Award", back_populates="ratings")
