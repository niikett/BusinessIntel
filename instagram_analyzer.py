"""
Instagram Profile Analyzer
A Python-based tool to analyze Instagram profiles and identify growth opportunities
"""

import instaloader
from datetime import datetime, timedelta
import statistics
from typing import Dict, List, Optional
import json
import os
from dotenv import load_dotenv

load_dotenv()

IG_USERNAME = os.getenv("IG_USERNAME")

class InstagramAnalyzer:
    def __init__(self):
        if not IG_USERNAME:
            raise RuntimeError("IG_USERNAME not set in .env")

        self.loader = instaloader.Instaloader()
        try:
            self.loader.load_session_from_file(IG_USERNAME)
            print(f"✅ Instagram session loaded for {IG_USERNAME}")
        except FileNotFoundError:
            raise RuntimeError(
                f"Instagram session not found. Run: instaloader --login {IG_USERNAME}"
            )


        
    def fetch_profile_data(self, username: str) -> Optional[Dict]:
        """
        Fetch public Instagram profile data
        
        Args:
            username: Instagram username (without @)
            
        Returns:
            Dictionary containing profile metrics or None if error
        """
        try:
            profile = instaloader.Profile.from_username(self.loader.context, username)
            
            # Get recent posts (last 12 posts)
            posts = []
            post_count = 0
            for post in profile.get_posts():
                if post_count >= 12:
                    break
                posts.append({
                    'likes': post.likes,
                    'comments': post.comments,
                    'date': post.date,
                    'is_video': post.is_video,
                    'caption': post.caption[:100] if post.caption else ""  # First 100 chars
                })
                post_count += 1
            
            # Calculate metrics
            profile_data = {
                'username': profile.username,
                'full_name': profile.full_name,
                'biography': profile.biography,
                'followers': profile.followers,
                'following': profile.followees,
                'total_posts': profile.mediacount,
                'is_verified': profile.is_verified,
                'is_business': profile.is_business_account,
                'profile_pic_url': profile.profile_pic_url,
                'recent_posts': posts,
                'fetch_time': datetime.now().isoformat()
            }
            
            return profile_data
            
        except instaloader.exceptions.ProfileNotExistsException:
            print(f"Profile @{username} does not exist")
            return None
        except instaloader.exceptions.ConnectionException as e:
            print(f"Connection error: {e}")
            return None
        except Exception as e:
            print(f"Error fetching profile: {e}")
            return None
    
    def analyze_profile(self, profile_data: Dict) -> Dict:
        """
        Analyze profile data and generate insights
        
        Args:
            profile_data: Dictionary with profile information
            
        Returns:
            Dictionary containing analysis results
        """
        if not profile_data or not profile_data.get('recent_posts'):
            return {
                'error': 'Insufficient data for analysis',
                'opportunity_score': 0
            }
        
        posts = profile_data['recent_posts']
        followers = profile_data['followers']
        
        # Calculate engagement metrics
        total_likes = sum(p['likes'] for p in posts)
        total_comments = sum(p['comments'] for p in posts)
        avg_likes = total_likes / len(posts) if posts else 0
        avg_comments = total_comments / len(posts) if posts else 0
        avg_engagement = avg_likes + avg_comments
        
        # Engagement rate calculation
        engagement_rate = (avg_engagement / followers * 100) if followers > 0 else 0
        
        # Posting frequency analysis
        if len(posts) >= 2:
            post_dates = [p['date'] for p in posts]
            date_diffs = [(post_dates[i] - post_dates[i+1]).days 
                         for i in range(len(post_dates)-1)]
            avg_posting_interval = statistics.mean(date_diffs) if date_diffs else 0
        else:
            avg_posting_interval = 30  # Default if not enough data
        
        # Last post recency
        last_post_days = (datetime.now(posts[0]['date'].tzinfo) - posts[0]['date']).days if posts else 999
        
        # Determine posting frequency category
        if avg_posting_interval <= 1.5:
            posting_frequency = "daily"
        elif avg_posting_interval <= 4:
            posting_frequency = "2-3 times/week"
        elif avg_posting_interval <= 9:
            posting_frequency = "weekly"
        else:
            posting_frequency = "irregular"
        
        # Identify issues
        issues = []
        if engagement_rate < 2.0:
            issues.append("Low engagement rate - audience not interacting with content")
        if avg_posting_interval > 5:
            issues.append("Inconsistent posting schedule - losing audience interest")
        if last_post_days > 7:
            issues.append(f"Inactive account - last post was {last_post_days} days ago")
        if profile_data['following'] > profile_data['followers'] * 1.5:
            issues.append("Following too many accounts compared to followers")
        if avg_comments < avg_likes * 0.02:
            issues.append("Very low comment-to-like ratio - weak community engagement")
        if profile_data['total_posts'] < 50:
            issues.append("Limited content library - not enough posts to attract followers")
        
        # Generate recommendations
        recommendations = []
        if engagement_rate < 3.0:
            recommendations.append("Implement strategic hashtag research and use 20-30 relevant hashtags per post")
        if avg_posting_interval > 3:
            recommendations.append("Establish consistent posting schedule - aim for 4-5 posts per week minimum")
        if avg_comments < avg_likes * 0.05:
            recommendations.append("Create content that encourages conversation - ask questions, run polls, engage with comments")
        if last_post_days > 3:
            recommendations.append("Resume regular posting immediately to re-engage dormant audience")
        
        recommendations.append("Analyze top-performing posts and replicate successful content themes")
        recommendations.append("Optimize posting times based on when followers are most active")
        recommendations.append("Invest in high-quality visual content - use professional photography/videography")
        
        # Calculate growth potential
        if engagement_rate < 1.5 and avg_posting_interval > 7:
            growth_potential = "low"
        elif engagement_rate < 3.0 or avg_posting_interval > 4:
            growth_potential = "medium"
        else:
            growth_potential = "high"
        
        # Calculate opportunity score (1-10)
        # Higher score = better opportunity for you to pitch services
        score = 5  # Base score
        
        if engagement_rate < 2.0:
            score += 1.5
        if avg_posting_interval > 5:
            score += 1.5
        if last_post_days > 7:
            score += 1
        if profile_data['followers'] > 1000 and engagement_rate < 2.5:
            score += 1  # Established account performing poorly
        if profile_data['is_business']:
            score += 0.5  # Business account = better lead
        
        score = min(10, max(1, round(score, 1)))  # Clamp between 1-10
        
        return {
            'username': profile_data['username'],
            'full_name': profile_data['full_name'],
            'followers': followers,
            'following': profile_data['following'],
            'posts': profile_data['total_posts'],
            'is_business': profile_data['is_business'],
            'engagement_rate': round(engagement_rate, 2),
            'average_likes': round(avg_likes, 1),
            'average_comments': round(avg_comments, 1),
            'posting_frequency': posting_frequency,
            'avg_posting_interval_days': round(avg_posting_interval, 1),
            'last_post_days': last_post_days,
            'growth_potential': growth_potential,
            'issues': issues[:5],  # Top 5 issues
            'recommendations': recommendations[:6],  # Top 6 recommendations
            'opportunity_score': score,
            'analyzed_at': datetime.now().isoformat()
        }
    
    def analyze_username(self, username: str) -> Dict:
        """
        Complete analysis workflow for a username
        
        Args:
            username: Instagram username
            
        Returns:
            Analysis results dictionary
        """
        print(f"Fetching data for @{username}...")
        profile_data = self.fetch_profile_data(username)
        
        if not profile_data:
            return {'error': f'Could not fetch profile @{username}'}
        
        print(f"Analyzing profile...")
        analysis = self.analyze_profile(profile_data)
        
        return analysis
    
    def export_report(self, analysis: Dict, filename: str = None) -> str:
        """
        Export analysis to JSON file
        
        Args:
            analysis: Analysis results
            filename: Output filename (optional)
            
        Returns:
            Path to exported file
        """
        if not filename:
            username = analysis.get('username', 'unknown')
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f"instagram_analysis_{username}_{timestamp}.json"
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(analysis, f, indent=2, ensure_ascii=False)
        
        print(f"Report exported to: {filename}")
        return filename


def main():
    """Example usage"""
    analyzer = InstagramAnalyzer()
    
    # Example: Analyze a profile
    username = input("Enter Instagram username (without @): ").strip()
    
    if not username:
        print("No username provided")
        return
    
    # Perform analysis
    results = analyzer.analyze_username(username)
    
    if 'error' in results:
        print(f"\nError: {results['error']}")
        return
    
    # Display results
    print("\n" + "="*60)
    print(f"ANALYSIS REPORT: @{results['username']}")
    print("="*60)
    
    print(f"\n📊 PROFILE STATS:")
    print(f"  Full Name: {results['full_name']}")
    print(f"  Followers: {results['followers']:,}")
    print(f"  Following: {results['following']:,}")
    print(f"  Total Posts: {results['posts']:,}")
    print(f"  Business Account: {'Yes' if results['is_business'] else 'No'}")
    
    print(f"\n📈 ENGAGEMENT METRICS:")
    print(f"  Engagement Rate: {results['engagement_rate']}%")
    print(f"  Average Likes: {results['average_likes']:.0f}")
    print(f"  Average Comments: {results['average_comments']:.0f}")
    
    print(f"\n📅 ACTIVITY:")
    print(f"  Posting Frequency: {results['posting_frequency']}")
    print(f"  Avg Days Between Posts: {results['avg_posting_interval_days']}")
    print(f"  Last Post: {results['last_post_days']} days ago")
    
    print(f"\n🎯 OPPORTUNITY ASSESSMENT:")
    print(f"  Growth Potential: {results['growth_potential'].upper()}")
    print(f"  Opportunity Score: {results['opportunity_score']}/10")
    
    print(f"\n⚠️  KEY ISSUES:")
    for i, issue in enumerate(results['issues'], 1):
        print(f"  {i}. {issue}")
    
    print(f"\n✅ RECOMMENDATIONS:")
    for i, rec in enumerate(results['recommendations'], 1):
        print(f"  {i}. {rec}")
    
    print("\n" + "="*60)
    
    # Export option
    export = input("\nExport report to JSON? (y/n): ").strip().lower()
    if export == 'y':
        filepath = analyzer.export_report(results)
        print(f"✓ Report saved to {filepath}")


if __name__ == "__main__":
    main()
