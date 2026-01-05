from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.db.session import engine, Base
from app.routes import gov, vendor, public, auth

# Create database tables
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Procurement Transparency Platform",
    description="AI-assisted, blockchain-enabled public procurement system",
    version="1.0.0"
)

# CORS - Allow frontend to access API
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000", "*"],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS", "PATCH"],
    allow_headers=["*"],
    expose_headers=["*"],
)

# Include routers
app.include_router(auth.router)
app.include_router(gov.router)
app.include_router(vendor.router)
app.include_router(public.router)

@app.get("/")
def root():
    return {
        "message": "Procurement Transparency Platform API",
        "version": "1.0.0",
        "endpoints": {
            "government": "/gov",
            "vendor": "/vendor",
            "public": "/public"
        }
    }

@app.get("/health")
def health_check():
    return {"status": "healthy"}
