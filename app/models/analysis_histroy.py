from sqlalchemy import create_engine, Column, Integer, String, Float, Boolean, DateTime, Text, JSON
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime

from app.core.config_db import Base

class AnalysisHistory(Base):
    """Store historical analysis results"""
    __tablename__ = 'analysis_history'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    username = Column(String(100), nullable=False, index=True)
    
    # Metrics at time of analysis
    followers = Column(Integer)
    following = Column(Integer)
    posts = Column(Integer)
    engagement_rate = Column(Float)
    average_likes = Column(Float)
    average_comments = Column(Float)
    
    # Analysis results
    posting_frequency = Column(String(50))
    last_post_days = Column(Integer)
    growth_potential = Column(String(20))
    opportunity_score = Column(Float, index=True)
    
    # Detailed findings (stored as JSON)
    issues = Column(JSON)
    recommendations = Column(JSON)
    
    # Lead status
    contacted = Column(Boolean, default=False, index=True)
    contacted_date = Column(DateTime)
    response_received = Column(Boolean, default=False)
    converted_to_client = Column(Boolean, default=False)
    notes = Column(Text)
    
    # Timestamp
    analyzed_at = Column(DateTime, default=datetime.utcnow, index=True)
    
    def to_dict(self):
        return {
            'id': self.id,
            'username': self.username,
            'followers': self.followers,
            'following': self.following,
            'posts': self.posts,
            'engagement_rate': self.engagement_rate,
            'average_likes': self.average_likes,
            'average_comments': self.average_comments,
            'posting_frequency': self.posting_frequency,
            'last_post_days': self.last_post_days,
            'growth_potential': self.growth_potential,
            'opportunity_score': self.opportunity_score,
            'issues': self.issues,
            'recommendations': self.recommendations,
            'contacted': self.contacted,
            'contacted_date': self.contacted_date.isoformat() if self.contacted_date else None,
            'response_received': self.response_received,
            'converted_to_client': self.converted_to_client,
            'notes': self.notes,
            'analyzed_at': self.analyzed_at.isoformat()
        }
