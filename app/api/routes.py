from fastapi import APIRouter, HTTPException, Query

from app.models import *
from app.schemas import *
from app.core.config_db import get_db

router = APIRouter(
    prefix="/attendances", 
    tags=["attendances"]
)


@router.get("/", tags=["Info"])
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


@router.get("/api/health", response_model=HealthResponse, tags=["Health"])
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


@router.post("/api/analyze", response_model=AnalysisResponse, tags=["Analysis"])
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


@router.post("/api/batch-analyze", response_model=BatchAnalysisResponse, tags=["Analysis"])
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


@router.get("/api/opportunities", response_model=List[OpportunityResponse], tags=["Opportunities"])
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


@router.get("/api/profile/{username}/history", tags=["Profile"])
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


@router.post("/api/profile/{username}/contact", tags=["Lead Management"])
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


@router.delete("/api/cache/clear", tags=["Admin"])
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


@router.get("/api/cache/stats", tags=["Admin"])
async def cache_stats():
    """Get cache statistics"""
    return {
        'success': True,
        'cached_profiles': len(analysis_cache),
        'profiles': list(analysis_cache.keys()),
        'total_size_mb': sum(len(str(v)) for v in analysis_cache.values()) / 1024 / 1024
    }


# Startup and Shutdown Events
@router.on_event("startup")
async def startup_event():
    """Run on application startup"""
    print("\n" + "="*60)
    print("Instagram Analyzer API - FastAPI Server")
    print("="*60)
    print(f"Database: PostgreSQL")
    print(f"Documentation: http://localhost:8000/docs")
    print("="*60 + "\n")


@router.on_event("shutdown")
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
