#!/bin/bash

echo "🚀 Starting Procurement Transparency Backend..."

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo -e "${YELLOW}⚠️  Virtual environment not found. Creating...${NC}"
    python3 -m venv venv
    echo -e "${GREEN}✅ Virtual environment created${NC}"
fi

# Activate virtual environment
echo -e "${BLUE}📦 Activating virtual environment...${NC}"
source venv/bin/activate

# Upgrade pip
echo -e "${BLUE}⬆️  Upgrading pip...${NC}"
pip install --upgrade pip > /dev/null 2>&1

# Install dependencies
echo -e "${BLUE}📥 Installing dependencies...${NC}"
pip install -r requirements.txt

# Check if .env exists
if [ ! -f ".env" ]; then
    echo -e "${YELLOW}⚠️  .env file not found. Please create one${NC}"
    echo -e "${YELLOW}Copy from ../.env or create with required variables${NC}"
fi

# Wait for database to be ready
echo -e "${BLUE}⏳ Waiting for database to be ready...${NC}"
sleep 5

# Run database migrations (create tables)
echo -e "${BLUE}🗄️  Creating database tables...${NC}"
python3 -c "
from app.db.session import engine, Base
from app.db.models import *
print('Creating all database tables...')
Base.metadata.create_all(bind=engine)
print('✅ Database tables created successfully!')
"

# Start FastAPI server
echo -e "${GREEN}🚀 Starting FastAPI server on http://0.0.0.0:8000${NC}"
echo -e "${GREEN}📚 API Documentation: http://localhost:8000/docs${NC}"
echo -e "${GREEN}🔧 Alternative docs: http://localhost:8000/redoc${NC}"
echo ""

# Start with reload for development
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
