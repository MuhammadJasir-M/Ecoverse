# 🏛️ Procurement Transparency Platform

AI-assisted, blockchain-enabled public procurement monitoring system for government tendering.

## 🎯 Features

- **Government Portal**: Create tenders, view bids, get AI recommendations, award contracts
- **Vendor Portal**: Register, browse tenders, submit bids, track outcomes
- **Public Portal**: View awarded tenders, verify blockchain records, rate projects
- **AI Engine**: Score bids, detect anomalies, recommend winners
- **Blockchain**: Immutable audit trail for complete transparency

## 🛠️ Tech Stack

- **Frontend**: React 18 + Vite + Tailwind CSS
- **Backend**: FastAPI + Python 3.11
- **Database**: PostgreSQL 15
- **Blockchain**: Hardhat + Solidity 0.8.20
- **AI**: Scikit-learn + Pandas + NumPy

## 🚀 Quick Start (Docker)

### Prerequisites

- Docker & Docker Compose installed
- 8GB RAM minimum
- Ports 5173, 8000, 8545, 5432 available

### 1. Clone & Setup

```bash
git clone <your-repo>
cd procurement-transparency
```

### 2. Start All Services (Recommended)

**On Windows:**

```cmd
start.bat
```

**On Linux/Mac:**

```bash
chmod +x start.sh
./start.sh
```

The startup script will:

1. Check/create `.env` file
2. Build Docker images
3. Start database and blockchain
4. Deploy smart contract
5. Copy ABI files
6. Start backend and frontend

### 3. Access the Platform

- **Frontend**: http://localhost:5173
- **Backend API**: http://localhost:8000
- **API Documentation**: http://localhost:8000/docs
- **Blockchain RPC**: http://localhost:8545

## 📋 Manual Setup (Alternative)

If you prefer manual setup:

### 1. Create .env file

```env
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
```

### 2. Build and Start Services

```bash
docker-compose up --build -d
```

### 3. Deploy Smart Contract

```bash
# Wait for blockchain to be ready (10-15 seconds)
docker-compose exec blockchain npx hardhat run scripts/deploy.js --network localhost

# Copy ABI to backend (Linux/Mac)
cp blockchain/ProcurementAudit_ABI.json backend/app/services/

# Copy ABI to backend (Windows)
copy blockchain\ProcurementAudit_ABI.json backend\app\services\
```

## 🎮 Usage

### Government Portal

1. Create a new tender with budget, deadline, and requirements
2. Wait for vendors to submit bids
3. Close the tender when deadline passes
4. Get AI-powered recommendations
5. Award the contract to the winning vendor
6. All actions are logged on blockchain

### Vendor Portal

1. Register as a vendor
2. Browse open tenders
3. Submit bids with price, technical proposal, and timeline
4. Track your bid status and AI scores
5. View award decisions

### Public Portal

1. View all awarded contracts
2. See complete bid transparency (after award)
3. Verify blockchain audit trail
4. Rate completed projects
5. Provide public feedback

## 🔧 Development & Management

### View Logs

```bash
# All services
docker-compose logs -f

# Specific service
docker-compose logs -f backend
docker-compose logs -f frontend
docker-compose logs -f blockchain
docker-compose logs -f db
```

### Restart Services

```bash
# Restart all
docker-compose restart

# Restart specific service
docker-compose restart backend
```

### Stop Services

```bash
# Stop all services
docker-compose down

# Stop and remove volumes (complete cleanup)
docker-compose down -v
```

### Database Access

```bash
# Access PostgreSQL
docker-compose exec db psql -U procurement_user -d procurement_db

# Useful SQL commands
\dt                              # List all tables
SELECT * FROM tenders;           # View tenders
SELECT * FROM bids;              # View bids
SELECT * FROM awards;            # View awards
SELECT * FROM vendors;           # View vendors
SELECT * FROM public_ratings;    # View ratings
```

### Run Tests

```bash
# Backend tests (if implemented)
docker-compose exec backend pytest

# Blockchain tests
docker-compose exec blockchain npx hardhat test
```

## 🐛 Troubleshooting

### Backend fails to start

- **Check if `.env` file exists** in the root directory
- **Verify database is running**: `docker-compose ps db`
- **Check backend logs**: `docker-compose logs backend`
- **Ensure ABI file exists**: Should be at `backend/app/services/ProcurementAudit_ABI.json`
- **Solution**: Run `./start.sh` or `start.bat` to properly initialize all services

### Frontend shows "API Offline"

- **Verify backend is running**: `docker-compose ps backend`
- **Check backend health**: Open http://localhost:8000/health in browser
- **Check CORS settings** in backend (should allow all origins in development)
- **Solution**: Restart backend: `docker-compose restart backend`

### Blockchain connection fails

- **Ensure blockchain service is running**: `docker-compose ps blockchain`
- **Verify contract is deployed**: `docker-compose logs blockchain | grep "deployed"`
- **Check if ABI file was generated**: Look for `blockchain/ProcurementAudit_ABI.json`
- **Verify CONTRACT_ADDRESS** in `.env` matches the deployed address
- **Solution**: Redeploy contract or restart blockchain service

### Database connection errors

- **Wait for database** to fully start (may take 10-20 seconds on first run)
- **Check database logs**: `docker-compose logs db`
- **Verify DATABASE_URL** in `.env` is correct
- **Solution**: `docker-compose restart db` and wait 20 seconds

### Smart contract deployment fails

- **Restart blockchain**: `docker-compose restart blockchain`
- **Wait 10-15 seconds** for Hardhat node to be ready
- **Retry deployment**: `docker-compose exec blockchain npx hardhat run scripts/deploy.js --network localhost`
- **Check blockchain logs**: `docker-compose logs blockchain`

### Port already in use

```bash
# Find and kill process using port 8000 (backend)
# Windows
netstat -ano | findstr :8000
taskkill /PID <PID> /F

# Linux/Mac
lsof -ti:8000 | xargs kill -9

# Or change port in docker-compose.yml
```

## 📚 API Documentation

Once the backend is running, visit **http://localhost:8000/docs** for interactive API documentation (Swagger UI).

### Main Endpoints

**Government APIs** (`/gov`)

- `POST /gov/tenders` - Create tender
- `GET /gov/tenders` - List all tenders
- `GET /gov/tenders/{id}/bids` - Get bids for tender
- `POST /gov/tenders/{id}/close` - Close tender for bidding
- `GET /gov/tenders/{id}/recommendations` - Get AI recommendations
- `POST /gov/awards` - Award contract

**Vendor APIs** (`/vendor`)

- `POST /vendor/register` - Register vendor
- `GET /vendor/tenders/open` - List open tenders
- `POST /vendor/bids` - Submit bid
- `GET /vendor/bids/{vendor_id}` - Get vendor's bids

**Public APIs** (`/public`)

- `GET /public/tenders/awarded` - List awarded tenders
- `GET /public/tenders/{id}/transparency` - Get complete transparency view
- `POST /public/ratings` - Submit public rating

**System APIs**

- `GET /` - API information
- `GET /health` - Health check

## 🤖 AI Features

The AI engine analyzes bids based on multiple factors:

### Scoring Components

- **Price Score (35%)**: Competitive pricing relative to budget and other bids
- **Vendor Score (30%)**: Reputation, past performance, completion rate
- **Technical Score (25%)**: Proposal quality and delivery timeline
- **Risk Factor (10%)**: Penalty for anomalies

### Anomaly Detection

Automatically flags suspicious patterns:

- **Abnormally low prices**: >2.5 standard deviations below mean (potential dumping)
- **Price collusion**: Exact price matches between different bids
- **Unrealistic timelines**: Delivery promises <7 days
- **High-win-rate vendors**: Win rate >70% (potential favoritism)

### Recommendation Levels

- **High** (AI Score > 75): Strongly recommended
- **Medium** (AI Score 50-75): Consider carefully
- **Low** (AI Score < 50): Not recommended

## 🔐 Blockchain Transparency

Every critical action is logged immutably on the blockchain:

### What Gets Logged

1. **Tender Creation**: Hash of tender details (title, budget, deadline)
2. **Bid Submission**: Hash of bid data (price, vendor, proposal summary)
3. **Award Decision**: Hash of award details (winner, amount, justification)

### Verification

Public can verify:

- Complete audit trail exists for each tender
- Transaction timestamps are authentic
- Data integrity through cryptographic hash verification
- No tampering occurred after logging

### How It Works

```
Tender Created → Generate SHA-256 Hash → Log on Blockchain
              → Store hash in database → Return transaction hash

Later: Public retrieves both hashes → Compares → Verifies integrity
```

## 📦 Project Structure

```
procurement-transparency/
├── backend/              # FastAPI backend
│   ├── app/
│   │   ├── routes/      # API endpoints (gov, vendor, public)
│   │   ├── services/    # Business logic (AI, blockchain, hashing)
│   │   ├── db/          # Database models and session
│   │   ├── schemas/     # Pydantic request/response schemas
│   │   └── main.py      # FastAPI application
│   ├── requirements.txt # Python dependencies
│   └── Dockerfile
├── frontend/            # React frontend
│   ├── src/
│   │   ├── components/  # Reusable components
│   │   ├── pages/       # Dashboard pages
│   │   ├── services/    # API client
│   │   └── App.jsx      # Main application
│   ├── package.json
│   └── Dockerfile
├── blockchain/          # Smart contracts
│   ├── contracts/       # Solidity contracts
│   │   └── ProcurementAudit.sol
│   ├── scripts/         # Deployment scripts
│   │   └── deploy.js
│   ├── hardhat.config.js
│   └── Dockerfile
├── db/                  # Database initialization
│   └── init.sql         # SQL initialization scripts
├── docs/                # Documentation
├── docker-compose.yml   # Docker orchestration
├── .env                 # Environment variables
├── start.sh            # Linux/Mac startup script
└── start.bat           # Windows startup script
```

## 🔄 Complete Workflow Example

### Scenario: Government needs website development

1. **Government** creates tender "E-Government Portal" - $50,000 budget, 90-day deadline
2. **Blockchain** logs tender creation with cryptographic hash `0x1a2b3c...`
3. **System** sends confirmation with transaction hash
4. **Vendors** browse open tenders on vendor portal
5. **Vendor A** (TechCorp, 4.2★) bids $45,000, 60-day timeline
6. **Vendor B** (WebPro, 4.8★) bids $48,000, 45-day timeline
7. **Vendor C** (QuickDev, 3.0★) bids $25,000, 30-day timeline
8. **Blockchain** logs all three bid submissions
9. **Government** closes tender after deadline
10. **Government** requests AI analysis
11. **AI Engine** analyzes and scores:

    ```
    Vendor A: 78/100 (Good balance of price and reputation)
      - Price Score: 82 (competitive)
      - Vendor Score: 84 (good reputation, 15 completed projects)
      - Technical Score: 75 (reasonable timeline)
      - Anomalies: None

    Vendor B: 85/100 (Best overall - RECOMMENDED)
      - Price Score: 78 (slightly higher but within budget)
      - Vendor Score: 96 (excellent reputation, 30 completed projects)
      - Technical Score: 88 (faster delivery)
      - Anomalies: None

    Vendor C: 42/100 (FLAGGED - Not Recommended)
      - Price Score: 45 (suspiciously low: 2.8 std below mean)
      - Vendor Score: 60 (low reputation, only 2 completed projects)
      - Technical Score: 65 (unrealistic timeline for scope)
      - Anomalies: ⚠️ Abnormally low bid price
    ```

12. **Government** reviews AI recommendations and decides to award to Vendor B
13. **Government** provides justification: "Best combination of reputation, timeline, and reasonable pricing"
14. **Blockchain** logs award decision with hash `0x9f8e7d...`
15. **Vendor B** notified of win, contract activated
16. **Public** can now view:
    - All three bids with prices and scores
    - AI analysis and recommendations
    - Government's justification
    - Blockchain transaction proofs
17. **Project completed** after 43 days
18. **Citizens** rate the project:
    - 5★ - "Excellent new portal, very user-friendly"
    - 4★ - "Good work, minor bugs initially"
    - 5★ - "Fast delivery, professional team"
19. **Vendor B** reputation increases to 4.9★ for future tenders
20. **Statistics updated**: Vendor B now has 31 completed projects, 26 wins

## 🌟 Key Features Explained

### Complete Transparency

- After award, public sees ALL bids, prices, and AI scores
- Nothing is hidden - full accountability
- Citizens can verify government decisions

### AI-Powered Recommendations

- Machine learning detects anomalies automatically
- Objective scoring reduces human bias
- Flags suspicious patterns (collusion, dumping)

### Immutable Audit Trail

- Blockchain prevents tampering with records
- Cryptographic hashes ensure data integrity
- Public verification without trusted intermediary

### Public Accountability

- Citizens rate completed projects
- Feedback influences vendor reputations
- Creates incentive for quality delivery

## 🔐 Security Considerations

### Production Deployment

Before deploying to production:

1. **Change SECRET_KEY** in `.env` to a strong random value
2. **Change database password** to a secure password
3. **Use a real Ethereum network** (not Hardhat local node)
4. **Enable HTTPS** for all services
5. **Set up proper authentication** (JWT tokens, OAuth, etc.)
6. **Configure CORS properly** (don't use `allow_origins=["*"]`)
7. **Set up database backups**
8. **Use environment-specific .env files**
9. **Enable rate limiting** on API endpoints
10. **Review and update dependencies** regularly

### Current Setup (Development Only)

- ⚠️ Hardhat local blockchain (data lost on restart)
- ⚠️ Default private key (publicly known, DO NOT USE IN PRODUCTION)
- ⚠️ Simple password authentication
- ⚠️ No HTTPS
- ⚠️ CORS allows all origins

## 📄 License

MIT License - Feel free to use for educational or production purposes.

## 👥 Contributing

Contributions welcome! Please:

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

## 🐞 Reporting Issues

Found a bug? Please open an issue with:

- Description of the problem
- Steps to reproduce
- Expected vs actual behavior
- Logs (from `docker-compose logs`)

## 🙏 Acknowledgments

Built with modern tools for maximum transparency in public procurement:

- FastAPI for high-performance backend
- React + Vite for responsive frontend
- PostgreSQL for reliable data storage
- Hardhat + Solidity for blockchain audit trail
- Scikit-learn for AI-powered bid analysis

---

**Built for transparency. Powered by AI. Verified by blockchain.** 🏛️✨
