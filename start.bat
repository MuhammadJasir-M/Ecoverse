@echo off
REM Procurement Transparency Platform - Windows Startup Script

echo.
echo ===============================================
echo   Procurement Transparency Platform
echo   Windows Startup Script
echo ===============================================
echo.

REM Check if Docker is running
echo Checking Docker status...
docker info >nul 2>&1
if errorlevel 1 (
    echo.
    echo [ERROR] Docker Desktop is not running!
    echo.
    echo Please start Docker Desktop and wait for it to be ready, then run this script again.
    echo.
    echo Steps:
    echo   1. Open Docker Desktop
    echo   2. Wait for "Docker Desktop is running" status
    echo   3. Run this script again: .\start.bat
    echo.
    pause
    exit /b 1
)
echo [OK] Docker is running
echo.

REM Check if .env exists
if not exist ".env" (
    echo [ERROR] .env file not found!
    echo Creating .env file from template...
    (
        echo # Database Configuration
        echo POSTGRES_USER=procurement_user
        echo POSTGRES_PASSWORD=secure_password_123
        echo POSTGRES_DB=procurement_db
        echo DATABASE_URL=postgresql://procurement_user:secure_password_123@db:5432/procurement_db
        echo.
        echo # Backend Security
        echo SECRET_KEY=your-super-secret-key-change-in-production
        echo.
        echo # Blockchain Configuration
        echo ETHEREUM_RPC_URL=http://blockchain:8545
        echo CONTRACT_ADDRESS=0x5FbDB2315678afecb367f032d93F642f64180aa3
        echo PRIVATE_KEY=0xac0974bec39a17e36ba4a6b4d238ff944bacb478cbed5efcae784d7bf4f2ff80
        echo.
        echo # Frontend Configuration
        echo VITE_API_URL=http://localhost:8000
        echo VITE_BLOCKCHAIN_RPC=http://localhost:8545
    ) > .env
    echo [OK] .env file created
)

echo Step 1/5: Stopping any existing containers...
docker-compose down 2>nul
echo.

echo Step 2/5: Building Docker images...
docker-compose build
echo.

echo Step 3/5: Starting database and blockchain...
docker-compose up -d db blockchain
echo Waiting for services to be ready (20 seconds)...
timeout /t 20 /nobreak >nul
echo.

echo Step 4/5: Deploying smart contract...
echo This will generate the ABI file needed by the backend...
docker-compose exec blockchain npx hardhat run scripts/deploy.js --network localhost
if errorlevel 1 (
    echo [WARNING] Contract deployment failed. Retrying in 5 seconds...
    timeout /t 5 /nobreak >nul
    docker-compose exec blockchain npx hardhat run scripts/deploy.js --network localhost
)
echo.

REM Copy ABI file to backend if deployment was successful
if exist "blockchain\ProcurementAudit_ABI.json" (
    echo Copying ABI file to backend...
    if not exist "backend\app\services" mkdir "backend\app\services"
    copy /Y "blockchain\ProcurementAudit_ABI.json" "backend\app\services\" >nul
    echo [OK] ABI file copied
) else (
    echo [WARNING] ABI file not found. Backend may fail to connect.
)
echo.

echo Step 5/5: Starting backend and frontend...
docker-compose up -d backend frontend
echo.

echo ===============================================
echo   All services started successfully!
echo ===============================================
echo.
echo Service URLs:
echo    Frontend:     http://localhost:5173
echo    Backend API:  http://localhost:8000
echo    API Docs:     http://localhost:8000/docs
echo    Blockchain:   http://localhost:8545
echo    Database:     postgresql://localhost:5432/procurement_db
echo.
echo To view logs:
echo    All services:  docker-compose logs -f
echo    Backend only:  docker-compose logs -f backend
echo    Frontend only: docker-compose logs -f frontend
echo.
echo To stop all services:
echo    docker-compose down
echo.
pause
