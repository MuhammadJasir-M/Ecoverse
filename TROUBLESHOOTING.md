# Quick Troubleshooting Guide

## Common Issues and Solutions

### 1. "Cannot connect to backend API"

**Symptoms:**

- Frontend shows "API Offline"
- Create demo data script fails to connect

**Solutions:**

```bash
# Check if backend is running
docker-compose ps backend

# View backend logs
docker-compose logs backend

# Restart backend
docker-compose restart backend

# If still failing, rebuild
docker-compose up --build backend
```

**Root Causes:**

- Backend container not started
- Database connection failed
- Missing ABI file

---

### 2. "Blockchain logging failed"

**Symptoms:**

- Error messages in backend logs: "Blockchain logging failed"
- Tender/bid creation works but no blockchain hash

**Solutions:**

```bash
# Check if blockchain service is running
docker-compose ps blockchain

# View blockchain logs
docker-compose logs blockchain

# Restart blockchain
docker-compose restart blockchain

# Redeploy contract
docker-compose exec blockchain npx hardhat run scripts/deploy.js --network localhost

# Copy ABI file
# Linux/Mac:
cp blockchain/ProcurementAudit_ABI.json backend/app/services/

# Windows:
copy blockchain\ProcurementAudit_ABI.json backend\app\services\
```

---

### 3. "ModuleNotFoundError" or Import Errors

**Symptoms:**

- Backend fails to start
- Errors about missing Python modules

**Solutions:**

```bash
# Rebuild backend with fresh dependencies
docker-compose build --no-cache backend

# Check requirements.txt exists
ls backend/requirements.txt

# Force reinstall
docker-compose exec backend pip install -r requirements.txt
```

---

### 4. Database Connection Errors

**Symptoms:**

- "could not connect to server"
- "database does not exist"

**Solutions:**

```bash
# Check database is running
docker-compose ps db

# Wait for database to be ready (takes 10-20 seconds on first start)
docker-compose logs db | grep "ready to accept connections"

# Restart database
docker-compose down
docker-compose up -d db
sleep 20
docker-compose up -d backend frontend

# If persistent, reset database
docker-compose down -v  # WARNING: Deletes all data!
docker-compose up -d
```

---

### 5. Frontend Not Loading

**Symptoms:**

- Browser shows "Cannot GET /"
- Port 5173 not accessible

**Solutions:**

```bash
# Check frontend status
docker-compose ps frontend

# View logs
docker-compose logs frontend

# Common issues:
# 1. Node modules not installed
docker-compose exec frontend npm install

# 2. Port conflict
# Change port in docker-compose.yml frontend ports section

# 3. Rebuild
docker-compose build --no-cache frontend
docker-compose up -d frontend
```

---

### 6. "Port already in use"

**Symptoms:**

- Error starting services
- "bind: address already in use"

**Solutions:**

**Windows:**

```cmd
# Find process using port 8000
netstat -ano | findstr :8000

# Kill process (replace PID with actual process ID)
taskkill /PID <PID> /F

# Or stop other Docker containers
docker stop $(docker ps -aq)
```

**Linux/Mac:**

```bash
# Find and kill process
lsof -ti:8000 | xargs kill -9

# Or stop conflicting containers
docker stop $(docker ps -aq)
```

---

### 7. Smart Contract Deployment Fails

**Symptoms:**

- "deployment failed"
- Contract address is 0x000...

**Solutions:**

```bash
# Ensure blockchain is running and ready
docker-compose ps blockchain
docker-compose logs blockchain | tail -20

# Restart blockchain node
docker-compose restart blockchain

# Wait 15 seconds for node to be ready
sleep 15

# Deploy again
docker-compose exec blockchain npx hardhat run scripts/deploy.js --network localhost

# Check if deployment was successful
docker-compose logs blockchain | grep "deployed"
```

---

### 8. AI Recommendations Return Empty

**Symptoms:**

- No recommendations shown
- Empty recommendations array

**Solutions:**

```bash
# Ensure bids exist for the tender
curl http://localhost:8000/gov/tenders/1/bids

# Check backend logs for errors
docker-compose logs backend | grep -i error

# Verify vendors exist
curl http://localhost:8000/vendor/tenders/open

# May need to submit bids first
# Use create_demo_data.py script
```

---

### 9. CORS Errors in Browser Console

**Symptoms:**

- "blocked by CORS policy"
- Frontend can't make API requests

**Solutions:**

1. **Check backend CORS configuration** in `backend/app/main.py`:

   ```python
   app.add_middleware(
       CORSMiddleware,
       allow_origins=["*"],  # Should allow all in development
       allow_credentials=True,
       allow_methods=["*"],
       allow_headers=["*"],
   )
   ```

2. **Verify VITE_API_URL** in `.env`:

   ```
   VITE_API_URL=http://localhost:8000
   ```

3. **Restart backend:**
   ```bash
   docker-compose restart backend
   ```

---

### 10. Docker Compose Command Not Found

**Symptoms:**

- "docker-compose: command not found"

**Solutions:**

**Try newer syntax:**

```bash
docker compose up
# instead of
docker-compose up
```

**Or install Docker Compose:**

- **Windows/Mac**: Should come with Docker Desktop
- **Linux**:
  ```bash
  sudo apt-get update
  sudo apt-get install docker-compose-plugin
  ```

---

## Complete Reset (Nuclear Option)

If nothing works, completely reset everything:

```bash
# Stop all containers
docker-compose down -v

# Remove all images
docker-compose rm -f

# Remove volumes (WARNING: Deletes all data!)
docker volume prune -f

# Clean build cache
docker builder prune -f

# Start fresh
docker-compose build --no-cache
docker-compose up -d

# Wait 30 seconds
sleep 30

# Deploy contract
docker-compose exec blockchain npx hardhat run scripts/deploy.js --network localhost

# Copy ABI
cp blockchain/ProcurementAudit_ABI.json backend/app/services/

# Restart backend
docker-compose restart backend

# Create demo data
python create_demo_data.py
```

---

## Checking Service Health

### Manual Health Checks

```bash
# Backend health
curl http://localhost:8000/health
# Should return: {"status":"healthy"}

# Database connectivity
docker-compose exec db pg_isready -U procurement_user
# Should return: "ready to accept connections"

# Frontend (browser)
# Open: http://localhost:5173
# Should see the platform UI

# Blockchain RPC
curl -X POST http://localhost:8545 \
  -H "Content-Type: application/json" \
  -d '{"jsonrpc":"2.0","method":"eth_blockNumber","params":[],"id":1}'
# Should return block number
```

### View All Service Status

```bash
docker-compose ps

# Should show all 4 services "Up":
# - procurement_db
# - procurement_backend
# - procurement_blockchain
# - procurement_frontend
```

---

## Log Analysis

### View logs for specific issues:

```bash
# All errors across services
docker-compose logs | grep -i error

# Backend errors only
docker-compose logs backend | grep -i error

# Last 50 lines of backend
docker-compose logs backend --tail=50

# Follow logs in real-time
docker-compose logs -f backend

# Blockchain deployment logs
docker-compose logs blockchain | grep -A 10 "Deploying"
```

---

## Performance Issues

### Slow Response Times

```bash
# Check container resources
docker stats

# If containers are using >80% CPU/Memory:
# 1. Increase Docker Desktop resources
# 2. Close other applications
# 3. Use production build instead of dev mode
```

### Database Slow

```bash
# Check database size
docker-compose exec db psql -U procurement_user -d procurement_db -c "SELECT pg_size_pretty(pg_database_size('procurement_db'));"

# Check active connections
docker-compose exec db psql -U procurement_user -d procurement_db -c "SELECT count(*) FROM pg_stat_activity;"

# If too many connections, restart backend
docker-compose restart backend
```

---

## Getting Help

If issues persist:

1. **Check logs** thoroughly:

   ```bash
   docker-compose logs > full_logs.txt
   ```

2. **Verify environment**:

   ```bash
   cat .env
   docker --version
   docker-compose --version
   ```

3. **Create GitHub issue** with:

   - Full error message
   - Relevant log output
   - Docker version
   - Operating system
   - Steps to reproduce

4. **Search existing issues** on repository

---

## Prevention Tips

### Regular Maintenance

```bash
# Keep Docker clean (run weekly)
docker system prune -f

# Update images when needed
docker-compose pull
docker-compose build --pull

# Check disk space
df -h
docker system df
```

### Before Important Demo

```bash
# Day before demo:
./start.sh  # Test full startup
python create_demo_data.py  # Populate data
# Test all features manually

# Day of demo:
docker-compose down
./start.sh
# Warm up system by browsing all pages
```

---

**Remember**: Most issues are resolved by:

1. Checking logs: `docker-compose logs <service>`
2. Restarting: `docker-compose restart <service>`
3. Rebuilding: `docker-compose build --no-cache <service>`
4. Complete reset: `docker-compose down -v && docker-compose up`
