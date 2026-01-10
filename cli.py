"""
Instagram Analyzer CLI
Simple command-line interface for the Instagram analyzer
"""

import argparse
import sys
from instagram_analyzer import InstagramAnalyzer
from database import DatabaseManager
from datetime import datetime, timedelta
import json


class AnalyzerCLI:
    """Command-line interface for Instagram analyzer"""
    
    def __init__(self):
        self.analyzer = InstagramAnalyzer()
        self.db = DatabaseManager()
    
    def analyze(self, username, export=False):
        """Analyze a single profile"""
        print(f"\n🔍 Analyzing @{username}...\n")
        
        results = self.analyzer.analyze_username(username)
        
        if 'error' in results:
            print(f"❌ Error: {results['error']}\n")
            return
        
        # Display results
        self._display_analysis(results)
        
        # Store in database
        profile_data = {
            'username': results['username'],
            'full_name': results.get('full_name', ''),
            'followers': results['followers'],
            'following': results['following'],
            'total_posts': results['posts'],
            'is_business': results.get('is_business', False)
        }
        self.db.add_profile(profile_data)
        
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
        self.db.add_analysis(analysis_data)
        
        print("✅ Analysis saved to database\n")
        
        # Export if requested
        if export:
            filename = self.analyzer.export_report(results)
            print(f"📄 Report exported to: {filename}\n")
    
    def batch_analyze(self, usernames_file, min_score=5.0):
        """Analyze multiple profiles from a file"""
        try:
            with open(usernames_file, 'r') as f:
                usernames = [line.strip() for line in f if line.strip()]
            
            print(f"\n📊 Batch analyzing {len(usernames)} profiles...\n")
            
            opportunities = []
            
            for i, username in enumerate(usernames, 1):
                print(f"[{i}/{len(usernames)}] Analyzing @{username}...")
                
                results = self.analyzer.analyze_username(username)
                
                if 'error' not in results:
                    if results['opportunity_score'] >= min_score:
                        opportunities.append(results)
                        print(f"  ✓ Score: {results['opportunity_score']}/10 - OPPORTUNITY")
                    else:
                        print(f"  ✓ Score: {results['opportunity_score']}/10")
                    
                    # Store in database
                    profile_data = {
                        'username': results['username'],
                        'full_name': results.get('full_name', ''),
                        'followers': results['followers'],
                        'following': results['following'],
                        'total_posts': results['posts'],
                        'is_business': results.get('is_business', False)
                    }
                    self.db.add_profile(profile_data)
                    
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
                    self.db.add_analysis(analysis_data)
                else:
                    print(f"  ✗ Error: {results['error']}")
            
            # Display summary
            print(f"\n{'='*60}")
            print(f"BATCH ANALYSIS COMPLETE")
            print(f"{'='*60}")
            print(f"Total analyzed: {len(usernames)}")
            print(f"Opportunities found (score >= {min_score}): {len(opportunities)}")
            
            if opportunities:
                print(f"\nTop Opportunities:")
                opportunities.sort(key=lambda x: x['opportunity_score'], reverse=True)
                for i, opp in enumerate(opportunities[:10], 1):
                    print(f"  {i}. @{opp['username']} - Score: {opp['opportunity_score']}/10")
            
            print()
            
        except FileNotFoundError:
            print(f"❌ File not found: {usernames_file}\n")
        except Exception as e:
            print(f"❌ Error: {str(e)}\n")
    
    def show_opportunities(self, limit=20, min_score=5.0):
        """Show top opportunities from database"""
        opportunities = self.db.get_top_opportunities(limit=limit, min_score=min_score)
        
        if not opportunities:
            print(f"\n📊 No opportunities found with score >= {min_score}\n")
            return
        
        print(f"\n{'='*80}")
        print(f"TOP {len(opportunities)} OPPORTUNITIES (Score >= {min_score})")
        print(f"{'='*80}\n")
        
        for i, opp in enumerate(opportunities, 1):
            contacted = "✓ CONTACTED" if opp.contacted else "⭕ NOT CONTACTED"
            
            print(f"{i}. @{opp.username} - {contacted}")
            print(f"   Score: {opp.opportunity_score}/10 | Growth: {opp.growth_potential.upper()}")
            print(f"   Followers: {opp.followers:,} | Engagement: {opp.engagement_rate}%")
            print(f"   Analyzed: {opp.analyzed_at.strftime('%Y-%m-%d %H:%M')}")
            print(f"   Issues: {', '.join(opp.issues[:2])}")
            print()
        
        print(f"{'='*80}\n")
    
    def show_history(self, username):
        """Show analysis history for a profile"""
        history = self.db.get_profile_history(username)
        
        if not history:
            print(f"\n📊 No history found for @{username}\n")
            return
        
        print(f"\n{'='*60}")
        print(f"ANALYSIS HISTORY: @{username}")
        print(f"{'='*60}\n")
        
        for i, analysis in enumerate(history, 1):
            print(f"{i}. {analysis.analyzed_at.strftime('%Y-%m-%d %H:%M')}")
            print(f"   Followers: {analysis.followers:,} | Engagement: {analysis.engagement_rate}%")
            print(f"   Score: {analysis.opportunity_score}/10 | Growth: {analysis.growth_potential}")
            print()
        
        print(f"{'='*60}\n")
    
    def mark_contacted(self, username, notes=None):
        """Mark a profile as contacted"""
        success = self.db.mark_contacted(username, notes)
        
        if success:
            print(f"✅ @{username} marked as contacted\n")
        else:
            print(f"❌ Profile @{username} not found in database\n")
    
    def _display_analysis(self, results):
        """Display formatted analysis results"""
        print("="*60)
        print(f"ANALYSIS REPORT: @{results['username']}")
        print("="*60)
        
        print(f"\n📊 PROFILE STATS:")
        print(f"  Full Name: {results.get('full_name', 'N/A')}")
        print(f"  Followers: {results['followers']:,}")
        print(f"  Following: {results['following']:,}")
        print(f"  Total Posts: {results['posts']:,}")
        if 'is_business' in results:
            print(f"  Business Account: {'Yes' if results['is_business'] else 'No'}")
        
        print(f"\n📈 ENGAGEMENT METRICS:")
        print(f"  Engagement Rate: {results['engagement_rate']}%")
        print(f"  Average Likes: {results['average_likes']:.0f}")
        print(f"  Average Comments: {results['average_comments']:.0f}")
        
        print(f"\n📅 ACTIVITY:")
        print(f"  Posting Frequency: {results['posting_frequency']}")
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
        
        print("\n" + "="*60 + "\n")


def main():
    parser = argparse.ArgumentParser(
        description='Instagram Profile Analyzer - Identify growth opportunities',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Analyze a single profile
  python cli.py analyze username123
  
  # Analyze and export report
  python cli.py analyze username123 --export
  
  # Batch analyze from file
  python cli.py batch usernames.txt --min-score 6.0
  
  # View top opportunities
  python cli.py opportunities --limit 30 --min-score 7.0
  
  # View analysis history
  python cli.py history username123
  
  # Mark as contacted
  python cli.py contact username123 --notes "Sent email on 2024-01-10"
        """
    )
    
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    # Analyze command
    analyze_parser = subparsers.add_parser('analyze', help='Analyze a single profile')
    analyze_parser.add_argument('username', help='Instagram username (without @)')
    analyze_parser.add_argument('--export', action='store_true', help='Export report to JSON')
    
    # Batch command
    batch_parser = subparsers.add_parser('batch', help='Batch analyze profiles from file')
    batch_parser.add_argument('file', help='File containing usernames (one per line)')
    batch_parser.add_argument('--min-score', type=float, default=5.0, 
                             help='Minimum opportunity score to flag (default: 5.0)')
    
    # Opportunities command
    opp_parser = subparsers.add_parser('opportunities', help='Show top opportunities')
    opp_parser.add_argument('--limit', type=int, default=20, help='Number to show (default: 20)')
    opp_parser.add_argument('--min-score', type=float, default=5.0,
                           help='Minimum opportunity score (default: 5.0)')
    
    # History command
    history_parser = subparsers.add_parser('history', help='Show analysis history for a profile')
    history_parser.add_argument('username', help='Instagram username')
    
    # Contact command
    contact_parser = subparsers.add_parser('contact', help='Mark profile as contacted')
    contact_parser.add_argument('username', help='Instagram username')
    contact_parser.add_argument('--notes', help='Optional notes about the contact')
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        sys.exit(1)
    
    cli = AnalyzerCLI()
    
    try:
        if args.command == 'analyze':
            cli.analyze(args.username, export=args.export)
        elif args.command == 'batch':
            cli.batch_analyze(args.file, min_score=args.min_score)
        elif args.command == 'opportunities':
            cli.show_opportunities(limit=args.limit, min_score=args.min_score)
        elif args.command == 'history':
            cli.show_history(args.username)
        elif args.command == 'contact':
            cli.mark_contacted(args.username, notes=args.notes)
    finally:
        cli.db.close()


if __name__ == '__main__':
    main()
