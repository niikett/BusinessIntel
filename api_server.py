"""
FastAPI Server for Instagram Analyzer
Provides async REST endpoints for profile analysis
"""

from fastapi import FastAPI, HTTPException, BackgroundTasks, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime
import asyncio

from instagram_analyzer import InstagramAnalyzer
from database import DatabaseManager, AnalysisHistory

# Initialize FastAPI app
app = FastAPI(
    title="Instagram Profile Analyzer API",
    description="Analyze Instagram profiles to identify growth opportunities for marketing outreach",
    version="2.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify your frontend domain
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize services
analyzer = InstagramAnalyzer()
db = DatabaseManager()

# In-memory cache (in production, use Redis)
analysis_cache: Dict[str, Dict[str, Any]] = {}


# Pydantic Models for request/response validation
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


# API Endpoints
@app.get("/", tags=["Info"])
async def root():
    """API root endpoint"""
    return {
        "service": "Instagram Profile Analyzer API",
        "version": "2.0.0",
        "framework": "FastAPI",
        "database": "PostgreSQL",
        "docs": "/docs",
        "endpoints": {
            "analyze": "POST /api/analyze",
            "batch_analyze": "POST /api/batch-analyze",
            "opportunities": "GET /api/opportunities",
            "profile_history": "GET /api/profile/{username}/history",
            "mark_contacted": "POST /api/profile/{username}/contact",
            "health": "GET /api/health"
        }
    }


@app.get("/api/health", response_model=HealthResponse, tags=["Health"])
async def health_check():
    """Health check endpoint"""
    db_connected = True
    try:
        # Test database connection
        db.session.execute("SELECT 1")
    except:
        db_connected = False
    
    return HealthResponse(
        status="healthy" if db_connected else "degraded",
        timestamp=datetime.now().isoformat(),
        database_connected=db_connected,
        cache_size=len(analysis_cache)
    )


@app.post("/api/analyze", response_model=AnalysisResponse, tags=["Analysis"])
async def analyze_single_profile(request: AnalyzeRequest):
    """
    Analyze a single Instagram profile
    
    - **username**: Instagram username (without @)
    - **force_refresh**: Force re-fetch even if cached (default: False)
    """
    try:
        results = await analyze_profile_async(request.username, request.force_refresh)
        
        if 'error' in results:
            raise HTTPException(status_code=404, detail=results['error'])
        
        return convert_analysis_to_response(results)
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/batch-analyze", response_model=BatchAnalysisResponse, tags=["Analysis"])
async def batch_analyze_profiles(request: BatchAnalyzeRequest):
    """
    Analyze multiple Instagram profiles in batch
    
    - **usernames**: List of Instagram usernames (max 50)
    - **min_opportunity_score**: Filter results by minimum score
    """
    try:
        results = []
        errors = []
        
        # Analyze all profiles concurrently
        tasks = [analyze_profile_async(username) for username in request.usernames]
        analyses = await asyncio.gather(*tasks, return_exceptions=True)
        
        for username, analysis in zip(request.usernames, analyses):
            if isinstance(analysis, Exception):
                errors.append({
                    'username': username,
                    'error': str(analysis)
                })
            elif 'error' in analysis:
                errors.append({
                    'username': username,
                    'error': analysis['error']
                })
            else:
                # Apply filter
                if analysis['opportunity_score'] >= request.min_opportunity_score:
                    results.append(convert_analysis_to_response(analysis))
        
        # Sort by opportunity score
        results.sort(key=lambda x: x.opportunity_score, reverse=True)
        
        return BatchAnalysisResponse(
            success=True,
            total_analyzed=len(request.usernames),
            successful=len(results),
            failed=len(errors),
            results=results,
            errors=errors if errors else None
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/opportunities", response_model=List[OpportunityResponse], tags=["Opportunities"])
async def get_opportunities(
    limit: int = Query(20, ge=1, le=100, description="Number of results to return"),
    min_score: float = Query(5.0, ge=0.0, le=10.0, description="Minimum opportunity score")
):
    """
    Get top opportunities from database
    
    - **limit**: Maximum number of results (1-100)
    - **min_score**: Minimum opportunity score (0-10)
    """
    try:
        opportunities = db.get_top_opportunities(limit=limit, min_score=min_score)
        
        return [
            OpportunityResponse(
                id=opp.id,
                username=opp.username,
                opportunity_score=opp.opportunity_score,
                growth_potential=opp.growth_potential,
                engagement_rate=opp.engagement_rate,
                followers=opp.followers,
                issues=opp.issues,
                contacted=opp.contacted,
                analyzed_at=opp.analyzed_at.isoformat()
            )
            for opp in opportunities
        ]
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/profile/{username}/history", tags=["Profile"])
async def get_profile_history(
    username: str,
    limit: int = Query(10, ge=1, le=50, description="Number of historical records")
):
    """
    Get analysis history for a specific profile
    
    - **username**: Instagram username
    - **limit**: Number of historical records to return
    """
    try:
        history = db.get_profile_history(username, limit=limit)
        
        if not history:
            raise HTTPException(status_code=404, detail=f"No history found for @{username}")
        
        return [
            {
                'id': h.id,
                'username': h.username,
                'followers': h.followers,
                'engagement_rate': h.engagement_rate,
                'opportunity_score': h.opportunity_score,
                'growth_potential': h.growth_potential,
                'analyzed_at': h.analyzed_at.isoformat()
            }
            for h in history
        ]
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/profile/{username}/contact", tags=["Lead Management"])
async def mark_profile_contacted(username: str, request: MarkContactedRequest):
    """
    Mark a profile as contacted
    
    - **username**: Instagram username
    - **notes**: Optional notes about the contact
    """
    try:
        success = db.mark_contacted(username, notes=request.notes)
        
        if not success:
            raise HTTPException(
                status_code=404, 
                detail=f"Profile @{username} not found in database. Analyze it first."
            )
        
        return {
            'success': True,
            'message': f'@{username} marked as contacted',
            'username': username,
            'contacted_at': datetime.now().isoformat()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.delete("/api/cache/clear", tags=["Admin"])
async def clear_cache():
    """Clear the analysis cache"""
    global analysis_cache
    count = len(analysis_cache)
    analysis_cache = {}
    
    return {
        'success': True,
        'message': f'Cleared {count} cached analyses',
        'cleared_count': count
    }


@app.get("/api/cache/stats", tags=["Admin"])
async def cache_stats():
    """Get cache statistics"""
    return {
        'success': True,
        'cached_profiles': len(analysis_cache),
        'profiles': list(analysis_cache.keys()),
        'total_size_mb': sum(len(str(v)) for v in analysis_cache.values()) / 1024 / 1024
    }


# Startup and Shutdown Events
@app.on_event("startup")
async def startup_event():
    """Run on application startup"""
    print("\n" + "="*60)
    print("Instagram Analyzer API - FastAPI Server")
    print("="*60)
    print(f"Database: PostgreSQL")
    print(f"Documentation: http://localhost:8000/docs")
    print("="*60 + "\n")


@app.on_event("shutdown")
async def shutdown_event():
    """Run on application shutdown"""
    db.close()
    print("\nDatabase connection closed. Goodbye!")


if __name__ == "__main__":
    import uvicorn
    import os
    
    port = int(os.getenv("PORT", 8000))
    host = os.getenv("HOST", "0.0.0.0")
    
    uvicorn.run(
        "api_server:app",
        host=host,
        port=port,
        reload=True,  # Auto-reload on code changes (development only)
        log_level="info"
    )
