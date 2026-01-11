from instagram_analyzer import InstagramAnalyzer
from database import DatabaseManager
from datetime import datetime


def run(username: str):
    analyzer = InstagramAnalyzer()

    print(f"\n🔍 Running analysis for @{username}")
    analysis = analyzer.analyze_username(username)

    if "error" in analysis:
        print("❌ Error:", analysis["error"])
        return

    # ---------------- SAVE TO DATABASE ----------------
    with DatabaseManager() as db:
        db.add_analysis({
            "username": analysis["username"],
            "followers": analysis["followers"],
            "following": analysis["following"],
            "posts": analysis["posts"],
            "engagement_rate": analysis["engagement_rate"],
            "posting_frequency": analysis["posting_frequency"],
            "opportunity_score": analysis["opportunity_score"],
            "issues": analysis["issues"],
            "recommendations": analysis["recommendations"],
            "analyzed_at": datetime.utcnow()
        })

    # ---------------- PRINT OUTPUT ----------------
    print("\n📊 ANALYSIS COMPLETE")
    print("-" * 40)
    print(f"Username          : @{analysis['username']}")
    print(f"Followers         : {analysis['followers']:,}")
    print(f"Engagement Rate   : {analysis['engagement_rate']}%")
    print(f"Posting Frequency : {analysis['posting_frequency']}")
    print(f"Opportunity Score : {analysis['opportunity_score']}/10")

    print("\n⚠️ Issues:")
    for i, issue in enumerate(analysis["issues"], 1):
        print(f"  {i}. {issue}")

    print("\n✅ Recommendations:")
    for i, rec in enumerate(analysis["recommendations"], 1):
        print(f"  {i}. {rec}")

    print("\n💾 Saved to database successfully ✅")


if __name__ == "__main__":
    username = input("Enter Instagram username: ").strip()
    run(username)
