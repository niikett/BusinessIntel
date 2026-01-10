from sqlalchemy import create_engine, Column, Integer, String, Float, Boolean, DateTime, Text, JSON
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime

from app.core.config_db import Base

class Business(Base):
    """Store business information found via location search"""
    __tablename__ = 'businesses'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    business_name = Column(String(200), nullable=False)
    category = Column(String(100), index=True)
    
    # Contact information
    phone = Column(String(50))
    email = Column(String(200))
    website = Column(String(500))
    
    # Location
    address = Column(Text)
    city = Column(String(100), index=True)
    area = Column(String(100), index=True)
    pincode = Column(String(20), index=True)
    latitude = Column(Float)
    longitude = Column(Float)
    
    # Social media
    instagram_username = Column(String(100), index=True)
    facebook_url = Column(String(500))
    twitter_username = Column(String(100))
    
    # Source
    source = Column(String(100))
    
    # Timestamps
    discovered_at = Column(DateTime, default=datetime.utcnow)
    last_updated = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'business_name': self.business_name,
            'category': self.category,
            'phone': self.phone,
            'email': self.email,
            'website': self.website,
            'address': self.address,
            'city': self.city,
            'area': self.area,
            'pincode': self.pincode,
            'latitude': self.latitude,
            'longitude': self.longitude,
            'instagram_username': self.instagram_username,
            'facebook_url': self.facebook_url,
            'twitter_username': self.twitter_username,
            'source': self.source,
            'discovered_at': self.discovered_at.isoformat(),
            'last_updated': self.last_updated.isoformat()
        }
