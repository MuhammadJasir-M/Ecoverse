# 🏛️ Procurement Transparency Platform

AI-powered, blockchain-enabled public procurement monitoring system for transparent government tendering.

## 🎯 Features

- **Government Portal**: Create tenders, review bids, get AI-powered recommendations, award contracts
- **Vendor Portal**: Register companies, browse open tenders, submit competitive bids, track proposal status
- **Public Portal**: View awarded contracts, verify blockchain audit trails, rate completed projects
- **AI Recommendation Engine**:
  - Statistical price analysis (Z-score based)
  - Vendor credibility scoring
  - Technical proposal evaluation with NLP
  - Fraud detection and anomaly flagging
  - Multi-factor weighted scoring (Price 40% + Vendor 35% + Technical 25%)
- **Blockchain Audit**: Immutable records for tender creation, bid submission, and contract awards

## 🧠 AI Scoring System

The platform uses an intelligent scoring algorithm that:

- Analyzes bid prices using statistical methods (not just "lowest wins")
- Evaluates vendor reputation and track record
- Assesses technical proposal quality through keyword analysis
- Detects suspicious patterns (collusion, dumping, unrealistic timelines)
- Provides ranked recommendations with detailed score breakdowns

**[📖 Read Complete AI Scoring Guide](HOW_SCORING_WORKS_SIMPLE.md)**

## 🛠️ Tech Stack

**Frontend:**

- React 18 + Vite + Tailwind CSS
- React Router for navigation
- Context API for state management

**Backend:**

- FastAPI (Python 3.11)
- SQLAlchemy ORM
- PostgreSQL 15
- JWT Authentication

**Blockchain:**

- Hardhat Development Environment
- Solidity 0.8.20
- Local Ethereum Network

**AI/ML:**

- NumPy for statistical calculations
- Pandas for data manipulation
- Custom NLP for proposal analysis

## 🚀 Quick Start

### Prerequisites

- Docker & Docker Compose installed
- Windows: WSL2 enabled (for Docker)
- 8GB RAM minimum
- Ports available: 5173 (frontend), 8000 (backend), 8545 (blockchain), 5432 (database)

### 1. Clone Repository

```bash
git clone https://github.com/yourusername/procurement-transparency.git
cd procurement-transparency
```

### 2. Start All Services

```bash
# Windows
.\start.bat

# Linux/Mac
chmod +x start.sh
./start.sh
```

This will:

- Build and start all Docker containers
- Initialize the database
- Deploy blockchain smart contracts
- Create the default government account
- Start the frontend, backend, and blockchain services

### 3. Access the Application

**Frontend:** http://localhost:5173

**Default Credentials:**

- **Government Login**: Access Code: `GOVT2024SECURE`
- **Vendor Login**: Register a new vendor account

### 4. Customize Government Password (Optional)

To set a custom government access code:

```bash
# Using Docker
docker exec -it procurement_backend python -m app.scripts.init_government_account --code YOUR_CUSTOM_CODE

# Example
docker exec -it procurement_backend python -m app.scripts.init_government_account --code GOVT2026ADMIN
```

The access code should be:

- At least 8 characters long
- Alphanumeric (letters and numbers)
- Kept secure and confidential

## 📚 User Guides

### For Government Officials

1. **Login**: Use your access code at http://localhost:5173/government/login
2. **Create Tender**:
   - Click "Create New Tender"
   - Fill in details: Title, Description, Budget, Deadline, Category
   - Submit (automatically recorded on blockchain)
3. **Review Bids**:
   - Click on a tender to view all submitted bids
   - Click "Get AI Recommendations" to analyze bids
   - Review scores: Price, Vendor, Technical, Overall AI Score
4. **Award Contract**:
   - Select the winning bid using "Select Winner" button
   - Enter justification
   - Award is recorded on blockchain

### For Vendors

1. **Register**: Create account at http://localhost:5173/vendor/register
   - Provide: Vendor ID, Company Name, Email, Registration Number
   - Create secure password
2. **Browse Tenders**: View all open tenders on dashboard
3. **Submit Bid**:
   - Click "Submit Bid" on any open tender
   - Enter: Proposed Price, Delivery Timeline (days), Technical Proposal
   - Submit (recorded on blockchain)
4. **Track Status**: Monitor bid status and AI scores after evaluation

### For Public Access

1. **View Contracts**: Access http://localhost:5173/public
2. **Verify Transparency**:
   - View all awarded contracts
   - See bid details and AI scores
   - Verify blockchain transaction hashes
3. **Rate Projects**: Provide feedback on completed projects

## 🔧 Advanced Configuration

### Environment Variables

Edit `.env` file for custom configuration:

```env
# Database
POSTGRES_USER=procurement_user
POSTGRES_PASSWORD=secure_password_123
POSTGRES_DB=procurement_db

# Backend
SECRET_KEY=your-secret-key-change-in-production
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# Blockchain
BLOCKCHAIN_RPC_URL=http://blockchain:8545

# AI Engine (Optional LLM Integration)
AI_ENGINE_MODE=rule_based  # Options: rule_based, llm_enhanced
OPENAI_API_KEY=your-openai-key  # For LLM mode
```

### Custom Government Account

**Method 1: Command Line**

```bash
docker exec -it procurement_backend python -m app.scripts.init_government_account --code YOUR_CODE
```

**Method 2: Python Script**

```bash
docker exec -it procurement_backend python
>>> from app.scripts.init_government_account import create_government_account
>>> create_government_account("YOUR_CUSTOM_CODE")
```

## 🧪 Testing

### Sample Demo Data

The system includes pre-configured demo data:

- 1 Sample Tender (Smart City Surveillance Project)
- 3 Sample Vendors (GreenTech, Nova Smart, ABC Construction)
- 3 Sample Bids with realistic data

### Run Tests

```bash
# Backend tests
docker exec procurement_backend pytest

# Check AI engine
docker exec procurement_backend python -m app.services.ai_engine
```

## 🔍 Troubleshooting

### Port Already in Use

```bash
# Check what's using the port
netstat -ano | findstr :5173
netstat -ano | findstr :8000

# Kill the process or change ports in docker-compose.yml
```

### Database Connection Issues

```bash
# Reset database
docker-compose down -v
docker-compose up -d
```

### Blockchain Not Responding

```bash
# Restart blockchain service
docker-compose restart blockchain
```

### Frontend Shows "API Offline"

```bash
# Check backend logs
docker logs procurement_backend

# Verify backend is running
docker ps | findstr backend
```

## 📊 Understanding AI Scores

The AI recommendation system evaluates each bid across three dimensions:

### 1. Price Score (40% weight)

- Uses statistical Z-score analysis
- Compares bid to average of all bids
- Rewards competitive pricing
- Penalizes extreme outliers (both high and low)
- **Why not just "lowest wins"?** Prevents unrealistic lowball bids that lead to project failures

### 2. Vendor Score (35% weight)

- Company reputation (0-5 stars)
- Completed projects count
- Total contract wins
- Average customer ratings
- **Builds over time** as vendors complete more projects

### 3. Technical Score (25% weight)

- Proposal quality (length, keywords, technical depth)
- Timeline feasibility (optimal: 30-90 days)
- Professional language detection
- **Keywords matter**: methodology, experience, compliance, quality, etc.

### Final Score Calculation

```
Base Score = (Price × 0.40) + (Vendor × 0.35) + (Technical × 0.25)
```

Then adjusted based on:

- Success conditions met (price, timeline, reputation)
- Anomaly detection (fraud patterns, collusion)

**📖 [Read Full Scoring Explanation](HOW_SCORING_WORKS_SIMPLE.md)**

## 🔐 Security Features

- ✅ JWT-based authentication
- ✅ Password hashing with bcrypt
- ✅ Role-based access control (Government, Vendor, Public)
- ✅ Blockchain audit trail (immutable records)
- ✅ SQL injection protection (SQLAlchemy ORM)
- ✅ CORS configuration for API security

## 🌐 API Documentation

Once running, access interactive API docs:

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## 📂 Project Structure

```
procurement-transparency/
├── frontend/              # React frontend
│   ├── src/
│   │   ├── components/   # Reusable UI components
│   │   ├── pages/        # Page components
│   │   ├── contexts/     # Auth context
│   │   └── services/     # API calls
│   └── package.json
├── backend/               # FastAPI backend
│   ├── app/
│   │   ├── routes/       # API endpoints
│   │   ├── services/     # Business logic (AI, blockchain)
│   │   ├── db/           # Database models
│   │   └── schemas/      # Pydantic models
│   └── requirements.txt
├── blockchain/            # Smart contracts
│   ├── contracts/        # Solidity contracts
│   └── scripts/          # Deployment scripts
├── db/                    # Database initialization
├── docker-compose.yml     # Container orchestration
└── README.md
```

## 🤝 Contributing

Contributions welcome! Please:

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

## 📄 License

MIT License - see LICENSE file for details

## 🆘 Support

- **Documentation**: Check [HOW_SCORING_WORKS_SIMPLE.md](HOW_SCORING_WORKS_SIMPLE.md)
- **Issues**: GitHub Issues
- **Email**: support@procurement-platform.com

## 🎯 Roadmap

- [ ] Multi-language support
- [ ] Email notifications for bid updates
- [ ] Advanced analytics dashboard
- [ ] LLM integration for semantic proposal analysis
- [ ] Mobile application
- [ ] Export reports (PDF, Excel)
- [ ] Integration with e-signature services

---

**Built with ❤️ for transparent governance and fair procurement**
