# Instagram Analyzer - Quick Start Guide

## 📁 Project Structure

```
instagram-analyzer/
├── instagram_analyzer.py    # Core analysis engine (main module)
├── api_server.py            # FastAPI REST API server
├── database.py              # PostgreSQL models with SQLAlchemy
├── scheduler.py             # Automated crawling scheduler
├── cli.py                   # Command-line interface
├── demo.py                  # Interactive demo script
├── requirements.txt         # Python dependencies
├── docker-compose.yml       # Docker setup for PostgreSQL
├── alembic.ini             # Database migration config
├── .env.example            # Environment variables template
└── README.md               # Full documentation
```

## 🚀 Quick Start (5 Minutes)

### Step 1: Start PostgreSQL with Docker
```bash
docker-compose up -d
```

This starts:
- PostgreSQL on port 5432
- pgAdmin at http://localhost:5050 (optional database UI)

### Step 2: Install Dependencies
```bash
pip install -r requirements.txt
```

### Step 3: Setup Environment
```bash
cp .env.example .env
# Default settings work with Docker - no need to edit
```

### Step 4: Initialize Database
```bash
python database.py
```

### Step 5: Run the Demo
```bash
python demo.py
```

### Step 6: Analyze Your First Profile
```bash
python cli.py analyze example_business
```

### Step 7: Start API Server (Optional)
```bash
python api_server.py
# Visit http://localhost:8000/docs for interactive API docs
```

That's it! You're now ready to identify Instagram growth opportunities.

## 💡 Common Use Cases

### Use Case 1: Find Local Business Opportunities
```bash
# Create a file with local business Instagram handles
echo "downtown_cafe" >> local_businesses.txt
echo "fitness_studio_main" >> local_businesses.txt
echo "boutique_fashion_st" >> local_businesses.txt

# Analyze them all
python cli.py batch local_businesses.txt --min-score 6.0
```

### Use Case 2: Use the FastAPI Server
```bash
# Start server
python api_server.py

# In another terminal, use the API:
curl -X POST http://localhost:8000/api/analyze \
  -H "Content-Type: application/json" \
  -d '{"username": "example_business"}'

# Or visit http://localhost:8000/docs for interactive UI
```

### Use Case 3: Monitor Competitors
```bash
# Analyze competitor
python cli.py analyze competitor_agency

# Check their history over time
python cli.py history competitor_agency
```

### Use Case 4: Weekly Lead Generation
```bash
# Start automated scheduler
python scheduler.py

# It will:
# - Run daily at 9 AM
# - Generate weekly reports on Mondays
# - Track all changes automatically
```

## 📊 Understanding Results

### High Opportunity (Score 7-10)
- **What it means**: Strong lead - established account with clear issues
- **Action**: Prioritize outreach, prepare detailed proposal
- **Example pitch**: "I noticed your engagement rate is only 1.8% despite having 2,450 followers..."

### Medium Opportunity (Score 5-6)
- **What it means**: Decent potential but requires analysis
- **Action**: Review specific issues, personalize approach
- **Example pitch**: "Your posting frequency is inconsistent..."

### Low Opportunity (Score 1-4)
- **What it means**: Either performing well or too problematic
- **Action**: Monitor for future opportunities or skip

## 🎯 Sample Workflow

```bash
# Morning: Batch analyze new prospects
python cli.py batch prospects.txt

# Midday: Review opportunities via API
curl http://localhost:8000/api/opportunities?min_score=7.0

# Afternoon: Track outreach
python cli.py contact cafe_downtown --notes "Sent proposal email"

# Weekly: Generate report
# (Automated by scheduler.py)
```

## 🔧 Database Management

### View Database with pgAdmin
1. Open http://localhost:5050
2. Login: admin@admin.com / admin
3. Add server: localhost:5432, postgres/postgres

### Direct PostgreSQL Access
```bash
# Connect to database
docker exec -it instagram_analyzer_db psql -U postgres -d instagram_analyzer

# View tables
\dt

# Query opportunities
SELECT username, opportunity_score, engagement_rate 
FROM analysis_history 
WHERE opportunity_score >= 7.0 
ORDER BY opportunity_score DESC 
LIMIT 10;
```

### Backup Database
```bash
# Backup
docker exec instagram_analyzer_db pg_dump -U postgres instagram_analyzer > backup.sql

# Restore
docker exec -i instagram_analyzer_db psql -U postgres instagram_analyzer < backup.sql
```

## 🌐 API Examples

### Using Python requests
```python
import requests

# Analyze profile
response = requests.post(
    'http://localhost:8000/api/analyze',
    json={'username': 'example_business'}
)
print(response.json())

# Get opportunities
response = requests.get(
    'http://localhost:8000/api/opportunities',
    params={'limit': 20, 'min_score': 7.0}
)
opportunities = response.json()
```

### Using JavaScript/fetch
```javascript
// Analyze profile
const response = await fetch('http://localhost:8000/api/analyze', {
  method: 'POST',
  headers: {'Content-Type': 'application/json'},
  body: JSON.stringify({username: 'example_business'})
});
const data = await response.json();
```

## 📝 Important Notes

⚠️ **Rate Limiting**: Instagram limits API requests. Always add delays (5-10 seconds) between profile analyses.

⚠️ **Public Profiles Only**: This tool only works with public Instagram accounts.

⚠️ **Ethical Use**: Only use for legitimate business development. Respect privacy and platform terms.

✅ **Best Results**: Focus on accounts with 500-50,000 followers for best conversion rates.

## 🐳 Docker Commands

```bash
# Start services
docker-compose up -d

# Stop services
docker-compose down

# View logs
docker-compose logs -f postgres

# Restart database
docker-compose restart postgres

# Remove all data (careful!)
docker-compose down -v
```

## 📞 Support & Next Steps

### If Something Doesn't Work
1. Check database: `docker-compose ps`
2. View logs: `docker-compose logs postgres`
3. Verify connection: `python database.py`
4. Test API: Visit http://localhost:8000/docs

### Ready for Phase 2?
Phase 2 features (coming soon):
- Google Maps business discovery
- Location-based filtering by city/pincode
- Automated email outreach
- Web dashboard with React
- Performance tracking charts
- Redis caching for scalability

### Want to Scale?
Consider:
- Deploying to cloud (AWS, GCP, DigitalOcean)
- Adding Redis for caching
- Implementing queue system (Celery + RabbitMQ)
- Setting up monitoring (Prometheus, Grafana)
- Adding CI/CD pipeline

---

**Need help?** Check the full README.md for detailed documentation.
**API Docs:** http://localhost:8000/docs
