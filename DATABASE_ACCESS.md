# 📊 PostgreSQL Database Access Guide

Complete guide for accessing and viewing data in the Procurement Transparency Platform database.

---

## 🔗 Quick Access Commands

### **Option 1: Docker Exec (Recommended)**

Access PostgreSQL directly from the container:

```bash
# Connect to PostgreSQL container
docker exec -it procurement_db psql -U procurement_user -d procurement_db
```

### **Option 2: Using pgAdmin/DBeaver**

**Connection Details:**

- **Host:** localhost
- **Port:** 5432
- **Database:** procurement_db
- **Username:** procurement_user
- **Password:** secure_password_123

---

## 📋 Common Database Operations

### **1. View All Tables**

```bash
# Connect to database first
docker exec -it procurement_db psql -U procurement_user -d procurement_db

# Then list all tables
\dt
```

**Output shows:**

- tenders
- bids
- vendors
- awards
- government_accounts

### **2. View Table Structure**

```sql
-- Describe a specific table
\d tenders
\d bids
\d vendors
\d awards

-- See columns only
\d+ tenders
```

### **3. Exit PostgreSQL**

```sql
\q
```

---

## 🔍 Viewing Data

### **View All Tenders**

```bash
# Single command from terminal
docker exec -it procurement_db psql -U procurement_user -d procurement_db -c "SELECT id, title, budget, status, deadline FROM tenders;"
```

Or in PostgreSQL shell:

```sql
SELECT id, title, budget, status, deadline
FROM tenders
ORDER BY created_at DESC;
```

**Better formatted output:**

```sql
SELECT
    id,
    title,
    budget,
    department,
    status,
    TO_CHAR(deadline, 'YYYY-MM-DD') as deadline_date
FROM tenders
ORDER BY id;
```

### **View All Vendors**

```bash
# From terminal
docker exec -it procurement_db psql -U procurement_user -d procurement_db -c "SELECT id, name, email, reputation_score, total_wins FROM vendors;"
```

Or in SQL:

```sql
SELECT
    id,
    name,
    email,
    company_registration,
    reputation_score,
    total_wins,
    completed_projects
FROM vendors
ORDER BY reputation_score DESC;
```

### **View All Bids**

```bash
# From terminal
docker exec -it procurement_db psql -U procurement_user -d procurement_db -c "SELECT id, tender_id, vendor_id, proposed_price, delivery_timeline, ai_score, status FROM bids;"
```

Or in SQL:

```sql
SELECT
    b.id,
    t.title as tender_name,
    v.name as vendor_name,
    b.proposed_price,
    b.delivery_timeline,
    b.ai_score,
    b.status
FROM bids b
JOIN tenders t ON b.tender_id = t.id
JOIN vendors v ON b.vendor_id = v.id
ORDER BY b.tender_id, b.ai_score DESC;
```

### **View Bid Scores Breakdown**

```sql
SELECT
    b.id as bid_id,
    v.name as vendor,
    b.proposed_price,
    b.ai_score,
    b.price_score,
    b.vendor_score,
    b.technical_score,
    b.anomaly_flag
FROM bids b
JOIN vendors v ON b.vendor_id = v.id
WHERE b.tender_id = 1
ORDER BY b.ai_score DESC;
```

### **View Awards**

```sql
SELECT
    a.id,
    t.title as tender,
    v.name as winner,
    a.award_amount,
    a.justification,
    a.created_at
FROM awards a
JOIN tenders t ON a.tender_id = t.id
JOIN bids b ON a.winning_bid_id = b.id
JOIN vendors v ON b.vendor_id = v.id;
```

---

## 📊 Useful Queries

### **1. Tender with All Its Bids**

```sql
SELECT
    t.title as "Tender",
    t.budget as "Budget",
    v.name as "Vendor",
    b.proposed_price as "Bid Amount",
    b.delivery_timeline as "Days",
    b.ai_score as "AI Score",
    b.status as "Status"
FROM tenders t
LEFT JOIN bids b ON t.id = b.tender_id
LEFT JOIN vendors v ON b.vendor_id = v.id
WHERE t.id = 1
ORDER BY b.ai_score DESC;
```

### **2. Vendor Performance Overview**

```sql
SELECT
    v.name as "Vendor Name",
    v.reputation_score as "Reputation",
    v.total_wins as "Wins",
    v.completed_projects as "Projects",
    COUNT(b.id) as "Total Bids",
    AVG(b.ai_score) as "Avg AI Score"
FROM vendors v
LEFT JOIN bids b ON v.id = b.vendor_id
GROUP BY v.id, v.name, v.reputation_score, v.total_wins, v.completed_projects
ORDER BY v.total_wins DESC, "Avg AI Score" DESC;
```

### **3. Bid Statistics by Tender**

```sql
SELECT
    t.title as "Tender",
    COUNT(b.id) as "Total Bids",
    MIN(b.proposed_price) as "Lowest Bid",
    MAX(b.proposed_price) as "Highest Bid",
    AVG(b.proposed_price) as "Average Bid",
    t.budget as "Budget"
FROM tenders t
LEFT JOIN bids b ON t.id = b.tender_id
GROUP BY t.id, t.title, t.budget;
```

### **4. Bids with Anomalies**

```sql
SELECT
    v.name as "Vendor",
    t.title as "Tender",
    b.proposed_price as "Price",
    b.anomaly_reason as "Issue"
FROM bids b
JOIN vendors v ON b.vendor_id = v.id
JOIN tenders t ON b.tender_id = t.id
WHERE b.anomaly_flag = true;
```

### **5. Top Scoring Bids**

```sql
SELECT
    v.name as "Vendor",
    t.title as "Tender",
    b.ai_score as "AI Score",
    b.proposed_price as "Price",
    b.delivery_timeline as "Timeline"
FROM bids b
JOIN vendors v ON b.vendor_id = v.id
JOIN tenders t ON b.tender_id = t.id
ORDER BY b.ai_score DESC
LIMIT 10;
```

### **6. Check Government Account**

```sql
SELECT
    id,
    LEFT(access_code_hash, 20) || '...' as code_hash,
    created_at,
    last_login
FROM government_accounts;
```

---

## 🔧 Data Modification (Use Carefully!)

### **Update Vendor Reputation**

```sql
-- Update a vendor's reputation score
UPDATE vendors
SET reputation_score = 4.5
WHERE id = 1;

-- Update completed projects
UPDATE vendors
SET completed_projects = 5, total_wins = 2
WHERE id = 2;
```

### **Update Bid Scores Manually**

```sql
-- Recalculate or adjust a bid's AI score
UPDATE bids
SET ai_score = 75.5, price_score = 85.0
WHERE id = 1;
```

### **Change Tender Status**

```sql
-- Close a tender
UPDATE tenders
SET status = 'closed'
WHERE id = 1;

-- Mark as awarded
UPDATE tenders
SET status = 'awarded'
WHERE id = 1;
```

---

## 📈 Advanced Analytics

### **Price Competition Analysis**

```sql
SELECT
    t.title as "Tender",
    t.budget as "Budget",
    COUNT(b.id) as "Bids",
    MIN(b.proposed_price) as "Min",
    MAX(b.proposed_price) as "Max",
    AVG(b.proposed_price) as "Average",
    STDDEV(b.proposed_price) as "Std Dev",
    (t.budget - MIN(b.proposed_price)) as "Max Savings"
FROM tenders t
LEFT JOIN bids b ON t.id = b.tender_id
GROUP BY t.id, t.title, t.budget
HAVING COUNT(b.id) > 0;
```

### **Vendor Win Rate**

```sql
SELECT
    v.name as "Vendor",
    COUNT(b.id) as "Total Bids",
    v.total_wins as "Wins",
    CASE
        WHEN COUNT(b.id) > 0
        THEN ROUND((v.total_wins::numeric / COUNT(b.id)) * 100, 2)
        ELSE 0
    END as "Win Rate %"
FROM vendors v
LEFT JOIN bids b ON v.id = b.vendor_id
GROUP BY v.id, v.name, v.total_wins
ORDER BY "Win Rate %" DESC;
```

### **AI Score Distribution**

```sql
SELECT
    CASE
        WHEN ai_score >= 85 THEN '85-100 (Excellent)'
        WHEN ai_score >= 70 THEN '70-84 (Good)'
        WHEN ai_score >= 55 THEN '55-69 (Fair)'
        ELSE '0-54 (Poor)'
    END as "Score Range",
    COUNT(*) as "Count",
    ROUND(AVG(ai_score), 2) as "Avg Score"
FROM bids
WHERE ai_score IS NOT NULL
GROUP BY
    CASE
        WHEN ai_score >= 85 THEN '85-100 (Excellent)'
        WHEN ai_score >= 70 THEN '70-84 (Good)'
        WHEN ai_score >= 55 THEN '55-69 (Fair)'
        ELSE '0-54 (Poor)'
    END
ORDER BY "Avg Score" DESC;
```

---

## 💾 Data Export

### **Export to CSV**

```bash
# Export tenders to CSV
docker exec -it procurement_db psql -U procurement_user -d procurement_db -c "COPY (SELECT * FROM tenders) TO STDOUT WITH CSV HEADER" > tenders.csv

# Export bids with scores
docker exec -it procurement_db psql -U procurement_user -d procurement_db -c "COPY (SELECT b.*, v.name as vendor_name FROM bids b JOIN vendors v ON b.vendor_id = v.id) TO STDOUT WITH CSV HEADER" > bids_export.csv

# Export specific tender data
docker exec -it procurement_db psql -U procurement_user -d procurement_db -c "COPY (SELECT * FROM tenders WHERE id = 1) TO STDOUT WITH CSV HEADER" > tender_1.csv
```

### **Backup Database**

```bash
# Full database backup
docker exec procurement_db pg_dump -U procurement_user procurement_db > backup.sql

# Backup with timestamp
docker exec procurement_db pg_dump -U procurement_user procurement_db > backup_$(date +%Y%m%d_%H%M%S).sql
```

### **Restore Database**

```bash
# Restore from backup
docker exec -i procurement_db psql -U procurement_user -d procurement_db < backup.sql
```

---

## 🛠️ Database Maintenance

### **Check Database Size**

```sql
SELECT
    pg_size_pretty(pg_database_size('procurement_db')) as "Database Size";
```

### **Check Table Sizes**

```sql
SELECT
    tablename,
    pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename)) AS size
FROM pg_tables
WHERE schemaname = 'public'
ORDER BY pg_total_relation_size(schemaname||'.'||tablename) DESC;
```

### **Count Records in All Tables**

```sql
SELECT
    'tenders' as table_name,
    COUNT(*) as record_count
FROM tenders
UNION ALL
SELECT 'bids', COUNT(*) FROM bids
UNION ALL
SELECT 'vendors', COUNT(*) FROM vendors
UNION ALL
SELECT 'awards', COUNT(*) FROM awards
UNION ALL
SELECT 'government_accounts', COUNT(*) FROM government_accounts;
```

### **Vacuum Database (Clean Up)**

```sql
-- Analyze and optimize
VACUUM ANALYZE;

-- Full vacuum (requires more resources)
VACUUM FULL;
```

---

## 🔒 Security & Access Control

### **View Current Connections**

```sql
SELECT
    pid,
    usename,
    application_name,
    client_addr,
    state,
    query_start
FROM pg_stat_activity
WHERE datname = 'procurement_db';
```

### **Kill a Specific Connection**

```sql
-- Find the PID first, then:
SELECT pg_terminate_backend(PID);
```

---

## 🧪 Testing & Development

### **Insert Test Vendor**

```sql
INSERT INTO vendors (name, email, company_registration, reputation_score, total_wins, completed_projects)
VALUES ('Test Vendor Ltd', 'test@vendor.com', 'REG123456', 3.5, 2, 5);
```

### **Insert Test Bid**

```sql
INSERT INTO bids (
    tender_id,
    vendor_id,
    proposed_price,
    technical_proposal,
    delivery_timeline,
    status
)
VALUES (
    1,
    1,
    45000000,
    'Our company has extensive experience in smart city projects...',
    90,
    'submitted'
);
```

### **Delete Test Data**

```sql
-- Delete a specific bid
DELETE FROM bids WHERE id = 999;

-- Delete all bids for a tender
DELETE FROM bids WHERE tender_id = 999;

-- CAREFUL: Delete all data from a table
TRUNCATE TABLE bids CASCADE;
```

---

## 📝 Quick Reference

### **Connection String Format**

```
postgresql://procurement_user:secure_password_123@localhost:5432/procurement_db
```

### **Common PostgreSQL Commands**

| Command         | Description              |
| --------------- | ------------------------ |
| `\dt`           | List all tables          |
| `\d table_name` | Describe table structure |
| `\l`            | List all databases       |
| `\du`           | List all users           |
| `\q`            | Quit PostgreSQL          |
| `\h SELECT`     | Help for SELECT command  |
| `\?`            | Show all commands        |
| `\timing`       | Toggle query timing      |
| `\x`            | Toggle expanded display  |

### **Useful Filters**

```sql
-- Tenders created today
SELECT * FROM tenders WHERE created_at::date = CURRENT_DATE;

-- Bids with high AI scores
SELECT * FROM bids WHERE ai_score > 80;

-- Vendors with good reputation
SELECT * FROM vendors WHERE reputation_score >= 4.0;

-- Open tenders
SELECT * FROM tenders WHERE status = 'open';

-- Awarded contracts
SELECT * FROM tenders WHERE status = 'awarded';
```

---

## 🚨 Troubleshooting

### **Can't Connect to Database**

```bash
# Check if container is running
docker ps | grep procurement_db

# Check container logs
docker logs procurement_db

# Restart database container
docker-compose restart db
```

### **Permission Denied**

```bash
# Make sure you're using the correct user
docker exec -it procurement_db psql -U procurement_user -d procurement_db

# Check user permissions
docker exec -it procurement_db psql -U procurement_user -d procurement_db -c "\du"
```

### **Database Not Found**

```bash
# List available databases
docker exec -it procurement_db psql -U procurement_user -c "\l"

# Recreate database (CAUTION: loses all data)
docker-compose down -v
docker-compose up -d
```

---

## 📚 Additional Resources

- **PostgreSQL Documentation**: https://www.postgresql.org/docs/
- **SQL Tutorial**: https://www.postgresql.org/docs/current/tutorial-sql.html
- **GUI Tools**:
  - pgAdmin: https://www.pgadmin.org/
  - DBeaver: https://dbeaver.io/
  - TablePlus: https://tableplus.com/

---

**💡 Pro Tip**: Always backup your database before running UPDATE or DELETE commands!

**⚠️ Warning**: Be extremely careful with DELETE and TRUNCATE commands in production!
