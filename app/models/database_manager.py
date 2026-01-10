from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from datetime import datetime

from app.core.config import settings
from app.core.config_db import Base
from app.models.analysis_histroy import *
from app.models.business import *
from app.models.crawl_job import *
from app.models.database_manager import *
from app.models.instagram_profile import *

class DatabaseManager:
    def __init__(self, db_url=None):
        self.db_url = db_url or settings.database_url
        self.engine = create_engine(self.db_url, echo=False, pool_pre_ping=True)
        Base.metadata.create_all(self.engine)
        Session = sessionmaker(bind=self.engine)
        self.session = Session()
    
    def add_profile(self, profile_data):
        """Add or update Instagram profile"""
        existing = self.session.query(InstagramProfile).filter_by(
            username=profile_data['username']
        ).first()
        
        if existing:
            # Update existing
            for key, value in profile_data.items():
                if hasattr(existing, key) and key != 'id':
                    setattr(existing, key, value)
            existing.last_crawled = datetime.utcnow()
            profile = existing
        else:
            # Create new
            profile = InstagramProfile(**profile_data)
            self.session.add(profile)
        
        self.session.commit()
        return profile
    
    def add_analysis(self, analysis_data):
        """Store analysis result"""
        analysis = AnalysisHistory(**analysis_data)
        self.session.add(analysis)
        self.session.commit()
        return analysis
    
    def get_profile_history(self, username, limit=10):
        """Get analysis history for a profile"""
        return self.session.query(AnalysisHistory).filter_by(
            username=username
        ).order_by(AnalysisHistory.analyzed_at.desc()).limit(limit).all()
    
    def get_top_opportunities(self, limit=20, min_score=5.0):
        """Get profiles with highest opportunity scores"""
        from sqlalchemy import func
        
        # Get most recent analysis for each username
        subquery = self.session.query(
            AnalysisHistory.username,
            func.max(AnalysisHistory.analyzed_at).label('max_date')
        ).group_by(AnalysisHistory.username).subquery()
        
        results = self.session.query(AnalysisHistory).join(
            subquery,
            (AnalysisHistory.username == subquery.c.username) &
            (AnalysisHistory.analyzed_at == subquery.c.max_date)
        ).filter(
            AnalysisHistory.opportunity_score >= min_score
        ).order_by(
            AnalysisHistory.opportunity_score.desc()
        ).limit(limit).all()
        
        return results
    
    def mark_contacted(self, username, notes=None):
        """Mark a profile as contacted"""
        analysis = self.session.query(AnalysisHistory).filter_by(
            username=username
        ).order_by(AnalysisHistory.analyzed_at.desc()).first()
        
        if analysis:
            analysis.contacted = True
            analysis.contacted_date = datetime.utcnow()
            if notes:
                analysis.notes = notes
            self.session.commit()
            return True
        return False
    
    def add_business(self, business_data):
        """Add business to database"""
        business = Business(**business_data)
        self.session.add(business)
        self.session.commit()
        return business
    
    def search_businesses(self, city=None, area=None, pincode=None, category=None):
        """Search for businesses by location/category"""
        query = self.session.query(Business)
        
        if city:
            query = query.filter(Business.city.ilike(f'%{city}%'))
        if area:
            query = query.filter(Business.area.ilike(f'%{area}%'))
        if pincode:
            query = query.filter_by(pincode=pincode)
        if category:
            query = query.filter(Business.category.ilike(f'%{category}%'))
        
        return query.all()
    
    def create_crawl_job(self, job_data):
        """Create a scheduled crawl job"""
        job = CrawlJob(**job_data)
        self.session.add(job)
        self.session.commit()
        return job
    
    def get_active_jobs(self):
        """Get all active crawl jobs"""
        return self.session.query(CrawlJob).filter_by(is_active=True).all()
    
    def close(self):
        """Close database session"""
        self.session.close()
