from datetime import datetime, timedelta
from typing import List, Optional, Dict, Any

from sqlalchemy import (
    Column,
    Integer,
    String,
    Float,
    Boolean,
    DateTime,
    Text,
    JSON,
    desc,
    func,
)

from config_db import Base, SessionLocal, init_db


# ========================= MODELS =========================

class AnalysisHistory(Base):
    __tablename__ = "analysis_history"

    id = Column(Integer, primary_key=True)
    username = Column(String(100), nullable=False, index=True)

    followers = Column(Integer)
    following = Column(Integer)
    posts = Column(Integer)
    engagement_rate = Column(Float)

    posting_frequency = Column(String(50))
    opportunity_score = Column(Float, index=True)

    issues = Column(JSON)
    recommendations = Column(JSON)

    contacted = Column(Boolean, default=False)
    contacted_date = Column(DateTime)

    converted_to_client = Column(Boolean, default=False)
    conversion_date = Column(DateTime)
    notes = Column(Text)

    analyzed_at = Column(DateTime, default=datetime.utcnow, index=True)


class Business(Base):
    __tablename__ = "businesses"

    id = Column(Integer, primary_key=True)
    business_name = Column(String(200), nullable=False)
    category = Column(String(100), index=True)

    city = Column(String(100), index=True)
    area = Column(String(100))
    state = Column(String(100))
    pincode = Column(String(20))

    instagram_username = Column(String(100), index=True)

    is_active = Column(Boolean, default=True, index=True)
    last_analyzed = Column(DateTime)
    current_opportunity_score = Column(Float)
    analysis_count = Column(Integer, default=0)

    discovered_at = Column(DateTime, default=datetime.utcnow)
    last_updated = Column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow
    )


class CrawlJob(Base):
    __tablename__ = "crawl_jobs"

    id = Column(Integer, primary_key=True)
    name = Column(String(200), nullable=False)

    location_city = Column(String(100), index=True)
    business_category = Column(String(100), index=True)

    is_active = Column(Boolean, default=True, index=True)
    last_run = Column(DateTime)

    created_at = Column(DateTime, default=datetime.utcnow)


class InstagramProfile(Base):
    __tablename__ = "instagram_profiles"

    id = Column(Integer, primary_key=True)
    username = Column(String(100), unique=True, nullable=False, index=True)

    followers = Column(Integer)
    following = Column(Integer)
    total_posts = Column(Integer)

    first_crawled = Column(DateTime, default=datetime.utcnow)
    last_crawled = Column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow
    )


# ========================= DATABASE MANAGER =========================

class DatabaseManager:
    def __init__(self):
        self.session = SessionLocal()

    def __del__(self):
        try:
            self.session.close()
        except Exception:
            pass

    # ---------- Instagram Profiles ----------

    def add_profile(self, data: Dict[str, Any]) -> InstagramProfile:
        profile = (
            self.session.query(InstagramProfile)
            .filter_by(username=data["username"])
            .first()
        )

        if profile:
            for k, v in data.items():
                if hasattr(profile, k):
                    setattr(profile, k, v)
            profile.last_crawled = datetime.utcnow()
        else:
            profile = InstagramProfile(**data)
            self.session.add(profile)

        self.session.commit()
        self.session.refresh(profile)
        return profile

    def get_profile(self, username: str) -> Optional[InstagramProfile]:
        return (
            self.session.query(InstagramProfile)
            .filter_by(username=username)
            .first()
        )

    # ---------- Analysis ----------

    def add_analysis(self, data: Dict[str, Any]) -> AnalysisHistory:
        analysis = AnalysisHistory(**data)
        self.session.add(analysis)
        self.session.commit()
        self.session.refresh(analysis)
        return analysis

    def get_top_opportunities(
        self, min_score: float = 5.0, limit: int = 20
    ) -> List[AnalysisHistory]:

        subq = (
            self.session.query(
                AnalysisHistory.username,
                func.max(AnalysisHistory.analyzed_at).label("latest"),
            )
            .group_by(AnalysisHistory.username)
            .subquery()
        )

        return (
            self.session.query(AnalysisHistory)
            .join(
                subq,
                (AnalysisHistory.username == subq.c.username)
                & (AnalysisHistory.analyzed_at == subq.c.latest),
            )
            .filter(AnalysisHistory.opportunity_score >= min_score)
            .order_by(AnalysisHistory.opportunity_score.desc())
            .limit(limit)
            .all()
        )

    def mark_converted(self, username: str, notes: Optional[str] = None) -> bool:
        analysis = (
            self.session.query(AnalysisHistory)
            .filter_by(username=username)
            .order_by(AnalysisHistory.analyzed_at.desc())
            .first()
        )

        if not analysis:
            return False

        analysis.converted_to_client = True
        analysis.conversion_date = datetime.utcnow()
        if notes:
            analysis.notes = notes

        self.session.commit()
        return True

    # ---------- Business ----------

    def get_businesses_needing_analysis(
        self, limit: int = 50
    ) -> List[Business]:

        cutoff = datetime.utcnow() - timedelta(days=7)

        return (
            self.session.query(Business)
            .filter(
                Business.instagram_username.isnot(None),
                Business.is_active.is_(True),
                (Business.last_analyzed.is_(None))
                | (Business.last_analyzed < cutoff),
            )
            .limit(limit)
            .all()
        )

    def update_business_analysis(
        self, business_id: int, score: float
    ) -> bool:

        business = self.session.query(Business).get(business_id)
        if not business:
            return False

        business.current_opportunity_score = score
        business.last_analyzed = datetime.utcnow()
        business.analysis_count += 1

        self.session.commit()
        return True

    # ---------- Stats ----------

    def get_profile_history(
        self, username: str, limit: int = 10
    ) -> List[AnalysisHistory]:
        """
        Return historical analysis records for a username
        """
        return (
            self.session.query(AnalysisHistory)
            .filter(AnalysisHistory.username == username)
            .order_by(desc(AnalysisHistory.analyzed_at))
            .limit(limit)
            .all()
        )


    def mark_contacted(
        self, username: str, notes: Optional[str] = None
    ) -> bool:
        """
        Mark the latest analysis of a profile as contacted
        """
        analysis = (
            self.session.query(AnalysisHistory)
            .filter(AnalysisHistory.username == username)
            .order_by(AnalysisHistory.analyzed_at.desc())
            .first()
        )

        if not analysis:
            return False

        analysis.contacted = True
        analysis.contacted_date = datetime.utcnow()

        if notes:
            analysis.notes = notes

        self.session.commit()
        return True



    def get_stats(self) -> Dict[str, Any]:
        return {
            "profiles": self.session.query(InstagramProfile).count(),
            "analyses": self.session.query(AnalysisHistory).count(),
            "businesses": self.session.query(Business).count(),
            "active_jobs": self.session.query(CrawlJob)
            .filter(CrawlJob.is_active.is_(True))
            .count(),
        }

    # ---------- Context Manager ----------

    def close(self):
        self.session.close()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, tb):
        self.close()


# ========================= BOOTSTRAP =========================

if __name__ == "__main__":
    print("Initializing database...")
    init_db()

    with DatabaseManager() as db:
        print("Database ready ✅")
        print("Stats:", db.get_stats())
