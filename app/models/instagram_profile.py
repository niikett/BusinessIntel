from sqlalchemy import create_engine, Column, Integer, String, Float, Boolean, DateTime, Text, JSON
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime

from app.core.config_db import Base


class InstagramProfile(Base):
    """Store Instagram profile data"""
    __tablename__ = 'instagram_profiles'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    username = Column(String(100), unique=True, nullable=False, index=True)
    full_name = Column(String(200))
    biography = Column(Text)
    
    # Metrics
    followers = Column(Integer)
    following = Column(Integer)
    total_posts = Column(Integer)
    is_verified = Column(Boolean, default=False)
    is_business = Column(Boolean, default=False)
    
    # Contact info (if available)
    email = Column(String(200))
    phone = Column(String(50))
    
    # Timestamps
    first_crawled = Column(DateTime, default=datetime.utcnow)
    last_crawled = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'username': self.username,
            'full_name': self.full_name,
            'biography': self.biography,
            'followers': self.followers,
            'following': self.following,
            'total_posts': self.total_posts,
            'is_verified': self.is_verified,
            'is_business': self.is_business,
            'email': self.email,
            'phone': self.phone,
            'first_crawled': self.first_crawled.isoformat() if self.first_crawled else None,
            'last_crawled': self.last_crawled.isoformat() if self.last_crawled else None
        }
