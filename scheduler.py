"""
Automated Scheduler for Instagram Profile Crawling
Runs analysis on scheduled intervals (daily, weekly, monthly)
"""

import schedule
import time
from datetime import datetime, timedelta
from instagram_analyzer import InstagramAnalyzer
from database import DatabaseManager, AnalysisHistory
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('crawler.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


class CrawlerScheduler:
    """Manages scheduled crawling and analysis of Instagram profiles"""
    
    def __init__(self):
        self.analyzer = InstagramAnalyzer()
        self.db = DatabaseManager()
        
    def analyze_and_store(self, username):
        """Analyze a profile and store results in database"""
        try:
            logger.info(f"Analyzing @{username}...")
            
            # Get analysis
            analysis = self.analyzer.analyze_username(username)
            
            if 'error' in analysis:
                logger.error(f"Failed to analyze @{username}: {analysis['error']}")
                return None
            
            # Store profile data
            profile_data = {
                'username': analysis['username'],
                'full_name': analysis.get('full_name', ''),
                'followers': analysis['followers'],
                'following': analysis['following'],
                'total_posts': analysis['posts'],
                'is_business': analysis.get('is_business', False)
            }
            self.db.add_profile(profile_data)
            
            # Store analysis
            analysis_data = {
                'username': analysis['username'],
                'followers': analysis['followers'],
                'following': analysis['following'],
                'posts': analysis['posts'],
                'engagement_rate': analysis['engagement_rate'],
                'average_likes': analysis['average_likes'],
                'average_comments': analysis['average_comments'],
                'posting_frequency': analysis['posting_frequency'],
                'last_post_days': analysis['last_post_days'],
                'growth_potential': analysis['growth_potential'],
                'opportunity_score': analysis['opportunity_score'],
                'issues': analysis['issues'],
                'recommendations': analysis['recommendations']
            }
            self.db.add_analysis(analysis_data)
            
            logger.info(f"✓ @{username} analyzed - Opportunity Score: {analysis['opportunity_score']}/10")
            return analysis
            
        except Exception as e:
            logger.error(f"Error analyzing @{username}: {str(e)}")
            return None
    
    def run_crawl_job(self, job):
        """Execute a scheduled crawl job"""
        logger.info(f"Starting crawl job: {job.name}")
        
        try:
            # Get businesses matching the criteria
            businesses = self.db.search_businesses(
                city=job.location_city,
                area=job.location_area,
                pincode=job.pincode,
                category=job.business_category
            )
            
            logger.info(f"Found {len(businesses)} businesses to analyze")
            
            analyzed_count = 0
            opportunities_found = 0
            
            for business in businesses:
                if not business.instagram_username:
                    continue
                
                # Analyze the profile
                analysis = self.analyze_and_store(business.instagram_username)
                
                if analysis:
                    analyzed_count += 1
                    
                    # Check if it meets opportunity criteria
                    if analysis['opportunity_score'] >= job.min_opportunity_score:
                        opportunities_found += 1
                        logger.info(f"🎯 OPPORTUNITY: @{analysis['username']} - Score: {analysis['opportunity_score']}/10")
                
                # Rate limiting - wait between requests
                time.sleep(5)  # 5 seconds between profiles
            
            # Update job status
            from sqlalchemy import update
            self.db.session.execute(
                update(job.__class__)
                .where(job.__class__.id == job.id)
                .values(
                    last_run=datetime.now(),
                    next_run=self._calculate_next_run(job.frequency),
                    profiles_found=analyzed_count
                )
            )
            self.db.session.commit()
            
            logger.info(f"Completed crawl job: {job.name}")
            logger.info(f"  Analyzed: {analyzed_count} profiles")
            logger.info(f"  Opportunities: {opportunities_found} profiles")
            
        except Exception as e:
            logger.error(f"Error in crawl job {job.name}: {str(e)}")
    
    def _calculate_next_run(self, frequency):
        """Calculate next run time based on frequency"""
        now = datetime.now()
        
        if frequency == 'daily':
            return now + timedelta(days=1)
        elif frequency == 'weekly':
            return now + timedelta(weeks=1)
        elif frequency == 'monthly':
            return now + timedelta(days=30)
        else:
            return now + timedelta(weeks=1)  # Default to weekly
    
    def check_and_run_jobs(self):
        """Check for jobs that need to run"""
        logger.info("Checking for scheduled jobs...")
        
        jobs = self.db.get_active_jobs()
        now = datetime.now()
        
        for job in jobs:
            # Run if next_run is None or past due
            if job.next_run is None or job.next_run <= now:
                self.run_crawl_job(job)
    
    def analyze_monitored_profiles(self):
        """Analyze all profiles being monitored"""
        logger.info("Running analysis on monitored profiles...")
        
        jobs = self.db.get_active_jobs()
        
        for job in jobs:
            if job.usernames_to_monitor:
                for username in job.usernames_to_monitor:
                    self.analyze_and_store(username)
                    time.sleep(5)  # Rate limiting
    
    def generate_weekly_report(self):
        """Generate weekly report of opportunities"""
        logger.info("Generating weekly opportunities report...")
        
        # Get top opportunities from last 7 days
        one_week_ago = datetime.now() - timedelta(days=7)
        
        opportunities = self.db.get_top_opportunities(limit=50, min_score=6.0)
        
        # Filter to only those analyzed in last 7 days
        recent_opportunities = [
            opp for opp in opportunities
            if opp.analyzed_at >= one_week_ago and not opp.contacted
        ]
        
        if recent_opportunities:
            logger.info(f"\n{'='*60}")
            logger.info(f"WEEKLY OPPORTUNITIES REPORT - {datetime.now().strftime('%Y-%m-%d')}")
            logger.info(f"{'='*60}")
            logger.info(f"Found {len(recent_opportunities)} high-value opportunities:\n")
            
            for i, opp in enumerate(recent_opportunities[:20], 1):
                logger.info(f"{i}. @{opp.username}")
                logger.info(f"   Score: {opp.opportunity_score}/10 | Followers: {opp.followers:,}")
                logger.info(f"   Engagement: {opp.engagement_rate}% | Potential: {opp.growth_potential}")
                logger.info(f"   Top Issues: {', '.join(opp.issues[:2])}")
                logger.info("")
            
            logger.info(f"{'='*60}\n")
        else:
            logger.info("No new opportunities found this week.")
    
    def start(self):
        """Start the scheduler"""
        logger.info("Starting Instagram Crawler Scheduler...")
        logger.info("Scheduled tasks:")
        logger.info("  • Check jobs: Every 1 hour")
        logger.info("  • Monitored profiles: Every day at 09:00")
        logger.info("  • Weekly report: Every Monday at 08:00")
        
        # Schedule tasks
        schedule.every(1).hours.do(self.check_and_run_jobs)
        schedule.every().day.at("09:00").do(self.analyze_monitored_profiles)
        schedule.every().monday.at("08:00").do(self.generate_weekly_report)
        
        # Run immediately on start
        self.check_and_run_jobs()
        
        # Keep running
        logger.info("Scheduler is running. Press Ctrl+C to stop.\n")
        
        try:
            while True:
                schedule.run_pending()
                time.sleep(60)  # Check every minute
                
        except KeyboardInterrupt:
            logger.info("\nScheduler stopped by user.")
        finally:
            self.db.close()


def main():
    """Main entry point"""
    scheduler = CrawlerScheduler()
    scheduler.start()


if __name__ == "__main__":
    main()
