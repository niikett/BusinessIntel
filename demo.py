#!/usr/bin/env python3
"""
Instagram Analyzer - Quick Start Demo
Simple examples showing how to use the analyzer
"""

from instagram_analyzer import InstagramAnalyzer
from database import DatabaseManager
import time


def demo_single_analysis():
    """Demo: Analyze a single Instagram profile"""
    print("\n" + "="*60)
    print("DEMO 1: Single Profile Analysis")
    print("="*60 + "\n")
    
    analyzer = InstagramAnalyzer()
    
    # Example usernames - replace with real usernames you want to test
    # Note: These should be public Instagram accounts
    username = "instagram"  # Instagram's official account (public, always available)
    
    print(f"Analyzing @{username}...\n")
    
    results = analyzer.analyze_username(username)
    
    if 'error' in results:
        print(f"Error: {results['error']}")
        return
    
    # Display key findings
    print(f"✓ Analysis Complete!")
    print(f"\nKey Metrics:")
    print(f"  • Followers: {results['followers']:,}")
    print(f"  • Engagement Rate: {results['engagement_rate']}%")
    print(f"  • Opportunity Score: {results['opportunity_score']}/10")
    print(f"  • Growth Potential: {results['growth_potential'].upper()}")
    
    print(f"\nTop 3 Issues:")
    for i, issue in enumerate(results['issues'][:3], 1):
        print(f"  {i}. {issue}")
    
    print(f"\nTop 3 Recommendations:")
    for i, rec in enumerate(results['recommendations'][:3], 1):
        print(f"  {i}. {rec}")


def demo_batch_analysis():
    """Demo: Analyze multiple profiles"""
    print("\n" + "="*60)
    print("DEMO 2: Batch Analysis")
    print("="*60 + "\n")
    
    analyzer = InstagramAnalyzer()
    db = DatabaseManager()
    
    # Example usernames - replace with actual business accounts you want to analyze
    usernames = [
        "instagram",
        "natgeo",
        "nasa"
    ]
    
    print(f"Analyzing {len(usernames)} profiles...\n")
    
    opportunities = []
    
    for i, username in enumerate(usernames, 1):
        print(f"[{i}/{len(usernames)}] @{username}...")
        
        results = analyzer.analyze_username(username)
        
        if 'error' not in results:
            # Store in database
            profile_data = {
                'username': results['username'],
                'full_name': results.get('full_name', ''),
                'followers': results['followers'],
                'following': results['following'],
                'total_posts': results['posts'],
                'is_business': results.get('is_business', False)
            }
            db.add_profile(profile_data)
            
            analysis_data = {
                'username': results['username'],
                'followers': results['followers'],
                'following': results['following'],
                'posts': results['posts'],
                'engagement_rate': results['engagement_rate'],
                'average_likes': results['average_likes'],
                'average_comments': results['average_comments'],
                'posting_frequency': results['posting_frequency'],
                'last_post_days': results['last_post_days'],
                'growth_potential': results['growth_potential'],
                'opportunity_score': results['opportunity_score'],
                'issues': results['issues'],
                'recommendations': results['recommendations']
            }
            db.add_analysis(analysis_data)
            
            opportunities.append(results)
            print(f"  ✓ Score: {results['opportunity_score']}/10")
        else:
            print(f"  ✗ Error: {results['error']}")
        
        # Rate limiting - important!
        if i < len(usernames):
            print("  Waiting 5 seconds...")
            time.sleep(5)
    
    # Show results
    print(f"\n{'='*60}")
    print("RESULTS SUMMARY")
    print(f"{'='*60}\n")
    
    opportunities.sort(key=lambda x: x['opportunity_score'], reverse=True)
    
    print("Profiles ranked by opportunity score:\n")
    for i, opp in enumerate(opportunities, 1):
        print(f"{i}. @{opp['username']}")
        print(f"   Score: {opp['opportunity_score']}/10 | Engagement: {opp['engagement_rate']}%")
        print(f"   Followers: {opp['followers']:,}\n")
    
    db.close()


def demo_database_queries():
    """Demo: Query database for opportunities"""
    print("\n" + "="*60)
    print("DEMO 3: Database Queries")
    print("="*60 + "\n")
    
    db = DatabaseManager()
    
    # Get top opportunities
    print("Top Opportunities (Score >= 5.0):\n")
    
    opportunities = db.get_top_opportunities(limit=10, min_score=5.0)
    
    if not opportunities:
        print("No opportunities found in database yet.")
        print("Run the batch analysis demo first!\n")
    else:
        for i, opp in enumerate(opportunities, 1):
            contacted = "✓ Contacted" if opp.contacted else "⭕ Not Contacted"
            print(f"{i}. @{opp.username} - {contacted}")
            print(f"   Score: {opp.opportunity_score}/10")
            print(f"   Analyzed: {opp.analyzed_at.strftime('%Y-%m-%d %H:%M')}\n")
    
    db.close()


def demo_export_report():
    """Demo: Export analysis report"""
    print("\n" + "="*60)
    print("DEMO 4: Export Report")
    print("="*60 + "\n")
    
    analyzer = InstagramAnalyzer()
    
    username = "instagram"
    
    print(f"Analyzing and exporting report for @{username}...\n")
    
    results = analyzer.analyze_username(username)
    
    if 'error' not in results:
        filepath = analyzer.export_report(results)
        print(f"✓ Report exported successfully!")
        print(f"  File: {filepath}")
        print(f"\nYou can now:")
        print(f"  • Open the JSON file to view raw data")
        print(f"  • Share it with your team")
        print(f"  • Use it in your CRM system")
    else:
        print(f"Error: {results['error']}")


def demo_track_lead():
    """Demo: Track a lead through the pipeline"""
    print("\n" + "="*60)
    print("DEMO 5: Lead Tracking")
    print("="*60 + "\n")
    
    db = DatabaseManager()
    
    username = "instagram"
    
    print(f"Marking @{username} as contacted...\n")
    
    success = db.mark_contacted(
        username,
        notes="Sent pitch email on 2024-01-10. Offering Instagram growth package."
    )
    
    if success:
        print(f"✓ Lead tracking updated!")
        print(f"\nYou can now:")
        print(f"  • Filter contacted vs non-contacted leads")
        print(f"  • Track conversion rates")
        print(f"  • Monitor follow-up schedules")
    else:
        print(f"Profile not found. Analyze it first!")
    
    db.close()


def main():
    """Run all demos"""
    print("\n" + "="*70)
    print(" "*15 + "INSTAGRAM ANALYZER - DEMO SUITE")
    print("="*70)
    print("\nThis demo shows you how to use the Instagram Analyzer system.")
    print("Make sure you have:")
    print("  ✓ Installed requirements (pip install -r requirements.txt)")
    print("  ✓ Initialized database (python database.py)")
    print("\n" + "="*70)
    
    demos = [
        ("Single Profile Analysis", demo_single_analysis),
        ("Batch Analysis (Multiple Profiles)", demo_batch_analysis),
        ("Database Queries", demo_database_queries),
        ("Export Report", demo_export_report),
        ("Lead Tracking", demo_track_lead)
    ]
    
    print("\nAvailable Demos:")
    for i, (name, _) in enumerate(demos, 1):
        print(f"  {i}. {name}")
    print(f"  {len(demos)+1}. Run All Demos")
    print(f"  0. Exit")
    
    try:
        choice = input("\nSelect demo to run (0-6): ").strip()
        
        if choice == '0':
            print("\nGoodbye!")
            return
        
        if choice == str(len(demos)+1):
            # Run all demos
            for name, demo_func in demos:
                try:
                    demo_func()
                    input("\nPress Enter to continue to next demo...")
                except KeyboardInterrupt:
                    print("\n\nDemo interrupted by user.")
                    break
                except Exception as e:
                    print(f"\n❌ Error in demo: {str(e)}")
                    input("\nPress Enter to continue...")
        else:
            # Run specific demo
            idx = int(choice) - 1
            if 0 <= idx < len(demos):
                name, demo_func = demos[idx]
                try:
                    demo_func()
                except Exception as e:
                    print(f"\n❌ Error: {str(e)}")
            else:
                print("Invalid choice!")
    
    except ValueError:
        print("Invalid input!")
    except KeyboardInterrupt:
        print("\n\nExiting...")
    
    print("\n" + "="*70)
    print("Demo complete! Check README.md for more usage examples.")
    print("="*70 + "\n")


if __name__ == "__main__":
    main()
