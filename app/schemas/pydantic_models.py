from pydantic import BaseModel, Field
from typing import List, Optional, Dict
from datetime import datetime
import asyncio


class AnalyzeRequest(BaseModel):
    username: str = Field(..., description="Instagram username without @", min_length=1, max_length=30)
    force_refresh: bool = Field(False, description="Force re-fetch even if cached")


class BatchAnalyzeRequest(BaseModel):
    usernames: List[str] = Field(..., description="List of Instagram usernames", min_items=1, max_items=50)
    min_opportunity_score: float = Field(0.0, ge=0.0, le=10.0, description="Minimum opportunity score to include")


class AnalysisResponse(BaseModel):
    username: str
    full_name: Optional[str] = None
    followers: int
    following: int
    posts: int
    is_business: bool
    engagement_rate: float
    average_likes: float
    average_comments: float
    posting_frequency: str
    avg_posting_interval_days: float
    last_post_days: int
    growth_potential: str
    issues: List[str]
    recommendations: List[str]
    opportunity_score: float
    analyzed_at: str


class BatchAnalysisResponse(BaseModel):
    success: bool
    total_analyzed: int
    successful: int
    failed: int
    results: List[AnalysisResponse]
    errors: Optional[List[Dict[str, str]]] = None


class OpportunityResponse(BaseModel):
    id: int
    username: str
    opportunity_score: float
    growth_potential: str
    engagement_rate: float
    followers: int
    issues: List[str]
    contacted: bool
    analyzed_at: str


class MarkContactedRequest(BaseModel):
    notes: Optional[str] = None


class HealthResponse(BaseModel):
    status: str
    timestamp: str
    database_connected: bool
    cache_size: int


# Helper Functions
def convert_analysis_to_response(analysis: Dict) -> AnalysisResponse:
    """Convert analysis dict to Pydantic response model"""
    return AnalysisResponse(
        username=analysis['username'],
        full_name=analysis.get('full_name'),
        followers=analysis['followers'],
        following=analysis['following'],
        posts=analysis['posts'],
        is_business=analysis.get('is_business', False),
        engagement_rate=analysis['engagement_rate'],
        average_likes=analysis['average_likes'],
        average_comments=analysis['average_comments'],
        posting_frequency=analysis['posting_frequency'],
        avg_posting_interval_days=analysis['avg_posting_interval_days'],
        last_post_days=analysis['last_post_days'],
        growth_potential=analysis['growth_potential'],
        issues=analysis['issues'],
        recommendations=analysis['recommendations'],
        opportunity_score=analysis['opportunity_score'],
        analyzed_at=analysis['analyzed_at']
    )


async def analyze_profile_async(username: str, force_refresh: bool = False) -> Dict:
    """Async wrapper for profile analysis"""
    # Check cache first
    if not force_refresh and username in analysis_cache:
        cached = analysis_cache[username]
        cache_age = (datetime.now() - datetime.fromisoformat(cached['analyzed_at'])).total_seconds()
        
        if cache_age < 86400:  # 24 hours
            return cached
    
    # Run analysis in thread pool (instaloader is synchronous)
    loop = asyncio.get_event_loop()
    results = await loop.run_in_executor(None, analyzer.analyze_username, username)
    
    if 'error' not in results:
        # Cache the results
        analysis_cache[username] = results
        
        # Store in database asynchronously
        await store_analysis_in_db(results)
    
    return results


async def store_analysis_in_db(analysis: Dict):
    """Store analysis results in database"""
    try:
        # Store profile
        profile_data = {
            'username': analysis['username'],
            'full_name': analysis.get('full_name', ''),
            'followers': analysis['followers'],
            'following': analysis['following'],
            'total_posts': analysis['posts'],
            'is_business': analysis.get('is_business', False)
        }
        db.add_profile(profile_data)
        
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
        db.add_analysis(analysis_data)
    except Exception as e:
        print(f"Error storing analysis in DB: {e}")
