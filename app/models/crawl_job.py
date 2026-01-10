from sqlalchemy import create_engine, Column, Integer, String, Float, Boolean, DateTime, Text, JSON
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime

from app.core.config_db import Base

class CrawlJob(Base):
    """Scheduled crawl jobs for automation"""
    __tablename__ = 'crawl_jobs'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(200), nullable=False)
    
    # Target criteria
    location_city = Column(String(100), index=True)
    location_area = Column(String(100))
    pincode = Column(String(20), index=True)
    business_category = Column(String(100), index=True)
    
    # Crawl settings
    frequency = Column(String(20), default='weekly')
    min_followers = Column(Integer, default=500)
    max_followers = Column(Integer)
    min_opportunity_score = Column(Float, default=5.0)
    
    # Status
    is_active = Column(Boolean, default=True, index=True)
    last_run = Column(DateTime)
    next_run = Column(DateTime)
    profiles_found = Column(Integer, default=0)
    
    # Results (stored as JSON)
    usernames_to_monitor = Column(JSON)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'location_city': self.location_city,
            'location_area': self.location_area,
            'pincode': self.pincode,
            'business_category': self.business_category,
            'frequency': self.frequency,
            'min_followers': self.min_followers,
            'max_followers': self.max_followers,
            'min_opportunity_score': self.min_opportunity_score,
            'is_active': self.is_active,
            'last_run': self.last_run.isoformat() if self.last_run else None,
            'next_run': self.next_run.isoformat() if self.next_run else None,
            'profiles_found': self.profiles_found,
            'usernames_to_monitor': self.usernames_to_monitor,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }
