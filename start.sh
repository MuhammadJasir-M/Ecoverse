#!/bin/bash

# Procurement Transparency Platform - Complete Startup Script
# This script starts all services in the correct order

set -e  # Exit on any error

echo "🏛️  Procurement Transparency Platform - Startup Script"
echo "======================================================"
echo ""

# Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m'

# Check if .env exists
if [ ! -f ".env" ]; then
    echo -e "${RED}❌ Error: .env file not found!${NC}"
    echo "Creating .env file from template..."
    cat > .env << 'EOF'
# Database Configuration
POSTGRES_USER=procurement_user
POSTGRES_PASSWORD=secure_password_123
POSTGRES_DB=procurement_db
DATABASE_URL=postgresql://procurement_user:secure_password_123@db:5432/procurement_db

# Backend Security
SECRET_KEY=your-super-secret-key-change-in-production

# Blockchain Configuration
ETHEREUM_RPC_URL=http://blockchain:8545
CONTRACT_ADDRESS=0x5FbDB2315678afecb367f032d93F642f64180aa3
PRIVATE_KEY=0xac0974bec39a17e36ba4a6b4d238ff944bacb478cbed5efcae784d7bf4f2ff80

# Frontend Configuration
VITE_API_URL=http://localhost:8000
VITE_BLOCKCHAIN_RPC=http://localhost:8545
EOF
    echo -e "${GREEN}✅ .env file created${NC}"
fi

echo -e "${BLUE}Step 1/5: Stopping any existing containers...${NC}"
docker-compose down -v 2>/dev/null || true
echo ""

echo -e "${BLUE}Step 2/5: Building Docker images...${NC}"
docker-compose build
echo ""

echo -e "${BLUE}Step 3/5: Starting database and blockchain...${NC}"
docker-compose up -d db blockchain
echo -e "${YELLOW}⏳ Waiting for services to be ready (20 seconds)...${NC}"
sleep 20
echo ""

echo -e "${BLUE}Step 4/5: Deploying smart contract...${NC}"
echo "This will generate the ABI file needed by the backend..."
docker-compose exec blockchain npx hardhat run scripts/deploy.js --network localhost || {
    echo -e "${YELLOW}⚠️  Contract deployment failed. Retrying in 5 seconds...${NC}"
    sleep 5
    docker-compose exec blockchain npx hardhat run scripts/deploy.js --network localhost
}
echo ""

# Copy ABI file to backend if deployment was successful
if [ -f "blockchain/ProcurementAudit_ABI.json" ]; then
    echo -e "${GREEN}Copying ABI file to backend...${NC}"
    mkdir -p backend/app/services
    cp blockchain/ProcurementAudit_ABI.json backend/app/services/
    echo -e "${GREEN}✅ ABI file copied${NC}"
else
    echo -e "${YELLOW}⚠️  ABI file not found in blockchain directory. Backend may fail to connect.${NC}"
fi
echo ""

echo -e "${BLUE}Step 5/5: Starting backend and frontend...${NC}"
docker-compose up -d backend frontend
echo ""

echo -e "${GREEN}=====================================================${NC}"
echo -e "${GREEN}✅ All services started successfully!${NC}"
echo -e "${GREEN}=====================================================${NC}"
echo ""
echo "📋 Service URLs:"
echo "   Frontend:     http://localhost:5173"
echo "   Backend API:  http://localhost:8000"
echo "   API Docs:     http://localhost:8000/docs"
echo "   Blockchain:   http://localhost:8545"
echo "   Database:     postgresql://localhost:5432/procurement_db"
echo ""
echo "📊 To view logs:"
echo "   All services:  docker-compose logs -f"
echo "   Backend only:  docker-compose logs -f backend"
echo "   Frontend only: docker-compose logs -f frontend"
echo ""
echo "🛑 To stop all services:"
echo "   docker-compose down"
echo ""
echo "🔄 To restart:"
echo "   docker-compose restart"
echo ""
