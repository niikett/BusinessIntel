# Instagram Profile Analyzer

A comprehensive Python-based system to analyze Instagram profiles, identify growth opportunities, and automate lead generation for your marketing firm.

## 🏗️ Tech Stack

- **Backend**: FastAPI (Python 3.8+)
- **Database**: PostgreSQL 15
- **ORM**: SQLAlchemy with Alembic migrations
- **Web Scraping**: Instaloader
- **API Docs**: Auto-generated Swagger/OpenAPI
- **Deployment**: Docker-ready with docker-compose

## 🎯 Features

### Current Implementation (Phase 1)
- ✅ **Instagram Profile Analysis**: Scrape and analyze public Instagram profiles
- ✅ **Engagement Metrics**: Calculate engagement rate, average likes/comments
- ✅ **Opportunity Scoring**: Automatic scoring (1-10) based on growth potential
- ✅ **Issue Detection**: Identify specific problems (low engagement, irregular posting, etc.)
- ✅ **Actionable Recommendations**: Generate specific improvement suggestions
- ✅ **PostgreSQL Database**: Production-ready relational database
- ✅ **FastAPI REST API**: High-performance async API with auto-generated docs
- ✅ **CLI Tool**: Command-line interface for easy interaction
- ✅ **Automated Scheduler**: Weekly/monthly automated crawling
- ✅ **Export Reports**: JSON export for client presentations

### Planned Features (Phase 2)
- 🔲 **Location-Based Business Discovery**: Find businesses by city/area/pincode
- 🔲 **Google Maps Integration**: Scrape business data from Google Maps
- 🔲 **Lead Management**: CRM features to track outreach and conversions
- 🔲 **Email Templates**: Automated outreach email generation
- 🔲 **Performance Tracking**: Track follower/engagement changes over time
- 🔲 **Web Dashboard**: React-based admin panel

## 📦 Installation

### Prerequisites
- Python 3.8 or higher
- PostgreSQL 15 (or use Docker)
- pip (Python package installer)

### Option 1: Using Docker (Recommended)

This is the easiest way to get started - Docker will handle PostgreSQL setup for you.

#### Step 1: Install Docker
Download Docker Desktop from https://www.docker.com/products/docker-desktop

#### Step 2: Start PostgreSQL
```bash
docker-compose up -d
```

This starts:
- PostgreSQL on port 5432
- pgAdmin (database UI) on port 5050 at http://localhost:5050

#### Step 3: Install Python Dependencies
```bash
pip install -r requirements.txt
```

#### Step 4: Initialize Database
```bash
# Copy environment file
cp .env.example .env

# Initialize database tables
python database.py
```

### Option 2: Manual PostgreSQL Setup

#### Step 1: Install PostgreSQL
**macOS:**
```bash
brew install postgresql@15
brew services start postgresql@15
```

**Ubuntu/Debian:**
```bash
sudo apt update
sudo apt install postgresql postgresql-contrib
sudo systemctl start postgresql
```

**Windows:**
Download installer from https://www.postgresql.org/download/windows/

#### Step 2: Create Database
```bash
# Access PostgreSQL
psql -U postgres

# Create database
CREATE DATABASE instagram_analyzer;

# Create user (optional)
CREATE USER instagram_user WITH PASSWORD 'your_password';
GRANT ALL PRIVILEGES ON DATABASE instagram_analyzer TO instagram_user;

# Exit
\q
```

#### Step 3: Install Python Dependencies
```bash
pip install -r requirements.txt
```

#### Step 4: Configure Environment
```bash
# Copy and edit .env file
cp .env.example .env

# Edit DATABASE_URL in .env
nano .env
```

Set your DATABASE_URL:
```
DATABASE_URL=postgresql://postgres:your_password@localhost:5432/instagram_analyzer
```

#### Step 5: Initialize Database
```bash
python database.py
```

## 🚀 Usage

### Method 1: Command-Line Interface (Recommended for Testing)

#### Analyze a Single Profile
```bash
python cli.py analyze username123
```

#### Analyze and Export Report
```bash
python cli.py analyze username123 --export
```

#### Batch Analyze from File
Create a text file `usernames.txt` with one username per line:
```
cafe_downtown
fitness_studio_nyc
boutique_fashion
local_restaurant
```

Then run:
```bash
python cli.py batch usernames.txt --min-score 6.0
```

#### View Top Opportunities
```bash
python cli.py opportunities --limit 30 --min-score 7.0
```

#### View Analysis History
```bash
python cli.py history username123
```

#### Mark Profile as Contacted
```bash
python cli.py contact username123 --notes "Sent email on 2024-01-10"
```

### Method 2: Direct Python Script

```python
from instagram_analyzer import InstagramAnalyzer

# Initialize analyzer
analyzer = InstagramAnalyzer()

# Analyze a profile
results = analyzer.analyze_username('example_business')

# Print results
print(f"Opportunity Score: {results['opportunity_score']}/10")
print(f"Engagement Rate: {results['engagement_rate']}%")
print(f"Issues: {results['issues']}")
print(f"Recommendations: {results['recommendations']}")

# Export report
analyzer.export_report(results)
```

### Method 3: FastAPI Server

#### Start the API Server
```bash
# Development mode with auto-reload
python api_server.py

# Or using uvicorn directly
uvicorn api_server:app --reload --host 0.0.0.0 --port 8000
```

Server will run on `http://localhost:8000`

**Interactive API Documentation:**
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

#### API Endpoints

**Analyze Single Profile**
```bash
curl -X POST http://localhost:8000/api/analyze \
  -H "Content-Type: application/json" \
  -d '{"username": "example_business", "force_refresh": false}'
```

**Batch Analyze Multiple Profiles**
```bash
curl -X POST http://localhost:8000/api/batch-analyze \
  -H "Content-Type: application/json" \
  -d '{
    "usernames": ["user1", "user2", "user3"],
    "min_opportunity_score": 5.0
  }'
```

**Get Top Opportunities**
```bash
curl http://localhost:8000/api/opportunities?limit=20&min_score=7.0
```

**Get Profile History**
```bash
curl http://localhost:8000/api/profile/username123/history?limit=10
```

**Mark as Contacted**
```bash
curl -X POST http://localhost:8000/api/profile/username123/contact \
  -H "Content-Type: application/json" \
  -d '{"notes": "Sent pitch email on 2024-01-10"}'
```

**Health Check**
```bash
curl http://localhost:8000/api/health
```

### Method 4: Automated Scheduler

#### Start the Scheduler
```bash
python scheduler.py
```

This will:
- Check for scheduled jobs every hour
- Analyze monitored profiles daily at 09:00
- Generate weekly opportunity reports every Monday at 08:00

#### Create a Scheduled Job Programmatically
```python
from database import DatabaseManager

db = DatabaseManager()

job_data = {
    'name': 'Fitness Studios in Mumbai',
    'location_city': 'Mumbai',
    'business_category': 'fitness',
    'frequency': 'weekly',
    'min_opportunity_score': 6.0,
    'usernames_to_monitor': ['gym1', 'yoga_studio', 'crossfit_mumbai']
}

job = db.create_crawl_job(job_data)
print(f"Created job: {job.name}")
```

## 📊 Understanding the Analysis

### Opportunity Score (1-10)
Higher score = better opportunity for your marketing services

- **8-10**: Excellent lead - significant issues, established audience
- **6-7**: Good lead - multiple improvement areas
- **4-5**: Moderate lead - some issues but decent performance
- **1-3**: Low priority - performing relatively well

### Growth Potential
- **High**: Strong foundation, needs optimization
- **Medium**: Some issues but salvageable
- **Low**: Significant problems or very inactive

### Key Metrics Analyzed
1. **Engagement Rate**: (Avg Likes + Avg Comments) / Followers × 100
2. **Posting Frequency**: Daily, 2-3×/week, weekly, irregular
3. **Content Recency**: Days since last post
4. **Follower Ratio**: Following vs Followers balance
5. **Community Engagement**: Comment-to-like ratio

## 📁 Database Schema

### Tables

**instagram_profiles**
- Profile metadata (username, bio, followers, etc.)
- Contact information
- First and last crawl timestamps

**analysis_history**
- Historical analysis results
- Engagement metrics over time
- Issues and recommendations
- Lead tracking (contacted, converted, etc.)

**crawl_jobs**
- Scheduled automated crawls
- Location/category targeting
- Frequency settings
- Monitored usernames

**businesses**
- Business information from location searches
- Contact details
- Social media links
- Geographic data

## 🔒 Rate Limiting & Best Practices

### Instagram API Limits
Instagram has rate limits. Follow these guidelines:

1. **Add delays between requests**: 5-10 seconds minimum
2. **Don't analyze too many profiles**: <100 per hour recommended
3. **Use caching**: Re-use recent analysis results
4. **Schedule wisely**: Spread crawls throughout the day

### Avoiding Blocks
```python
# Good: Add delays
import time
for username in usernames:
    analyze(username)
    time.sleep(10)  # 10 second delay

# Bad: Rapid-fire requests
for username in usernames:
    analyze(username)  # Will likely get blocked
```

## 📈 Workflow for Lead Generation

### Step 1: Discover Profiles
```bash
# Option A: Manual list
python cli.py batch target_businesses.txt

# Option B: Create scheduled job for automatic discovery
# (Phase 2 feature - location-based search)
```

### Step 2: Review Opportunities
```bash
python cli.py opportunities --min-score 7.0
```

### Step 3: Generate Reports
For each high-opportunity profile:
```bash
python cli.py analyze business_name --export
```

### Step 4: Track Outreach
```bash
python cli.py contact business_name --notes "Sent pitch email"
```

### Step 5: Monitor Results
Schedule weekly crawls to track improvements/changes

## 🛠️ Troubleshooting

### "Profile not found" Error
- Verify username is correct (without @)
- Check if profile is private (tool only works on public profiles)
- Ensure account exists

### Connection Errors
- Check internet connection
- Instagram might be temporarily blocking requests (add delays)
- Try again after waiting 1 hour

### Low/No Results
- Profile might be too new (< 10 posts)
- Private account
- No recent activity

### Database Locked
- Close other connections to database
- Restart scheduler if running

## 📝 Example Output

```
==============================================================
ANALYSIS REPORT: @local_cafe_downtown
==============================================================

📊 PROFILE STATS:
  Full Name: Downtown Cafe & Bakery
  Followers: 2,450
  Following: 3,200
  Total Posts: 87
  Business Account: Yes

📈 ENGAGEMENT METRICS:
  Engagement Rate: 1.8%
  Average Likes: 35
  Average Comments: 9

📅 ACTIVITY:
  Posting Frequency: irregular
  Last Post: 12 days ago

🎯 OPPORTUNITY ASSESSMENT:
  Growth Potential: MEDIUM
  Opportunity Score: 7.5/10

⚠️  KEY ISSUES:
  1. Low engagement rate - audience not interacting with content
  2. Inconsistent posting schedule - losing audience interest
  3. Inactive account - last post was 12 days ago
  4. Following too many accounts compared to followers

✅ RECOMMENDATIONS:
  1. Implement strategic hashtag research and use 20-30 relevant hashtags per post
  2. Establish consistent posting schedule - aim for 4-5 posts per week minimum
  3. Create content that encourages conversation - ask questions, run polls
  4. Resume regular posting immediately to re-engage dormant audience
  5. Analyze top-performing posts and replicate successful content themes
  6. Optimize posting times based on when followers are most active

==============================================================
```

## 🔮 Future Enhancements

### Phase 2: Location-Based Discovery
- Google Maps API integration
- Business directory scraping
- Geographic filtering
- Category-based search

### Phase 3: Advanced Analytics
- Competitor analysis
- Hashtag performance tracking
- Best time to post recommendations
- Content type analysis (images vs videos)

### Phase 4: Full CRM
- Email campaign integration
- Client conversion tracking
- Revenue attribution
- Automated follow-ups

## 📄 License

Proprietary - For internal use by your marketing firm

## 🤝 Support

For issues or questions, check the logs:
- API Server: Console output
- Scheduler: `crawler.log`
- Database: Use SQLite viewer to inspect data

## 💡 Tips

1. **Start Small**: Test with 5-10 profiles before scaling up
2. **Focus on Quality**: High opportunity scores (7+) convert better
3. **Track Everything**: Use the database to track all interactions
4. **Be Patient**: Instagram rate limits require slow, steady crawling
5. **Personalize Outreach**: Use specific issues from reports in your pitch

---

Built with Python 3 • Instagram Analysis • Lead Generation
