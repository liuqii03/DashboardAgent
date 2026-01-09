from google.adk.agents import LlmAgent

"""
Review Analysis Agent for the analytics dashboard.

This agent analyzes customer reviews to provide insights on:
- Average rating and rating distribution
- Satisfaction levels (Satisfied/Neutral/Dissatisfied)
- Sentiment analysis on review text
- Recurring themes summary

This is a READ-ONLY agent - no actions can be taken.
"""

from typing import Dict, Any, List

from ..database.api_db import api_db as db


def analyze_reviews(listing_id: str) -> Dict[str, Any]:
    """
    Analyze reviews for a listing with comprehensive metrics.

    Core Logic:
    1. Compute average rating and rating distribution (5-star, 4-star, etc.)
    2. Define satisfaction levels:
       - "Satisfied" if average rating ≥ 4
       - "Neutral" if average rating between 3 and 4
       - "Dissatisfied" if average rating < 3
    3. Perform sentiment analysis on review text
    4. Highlight recurring themes

    :param listing_id: Identifier of the listing to analyze
    :return: Dictionary with review analysis results
    """
    reviews = db.get_reviews(listing_id)
    listing = db.get_listing(listing_id)
    
    listing_title = listing.title if listing else listing_id
    
    if not reviews:
        return {
            "title": f"Review Analysis for '{listing_title}'",
            "overall_satisfaction": {
                "level": "No Reviews",
                "emoji": "❓",
                "average_rating": None,
                "max_rating": 5.0
            },
            "total_reviews": 0,
            "rating_distribution": {
                "5_star": {"count": 0, "percentage": 0},
                "4_star": {"count": 0, "percentage": 0},
                "3_star": {"count": 0, "percentage": 0},
                "2_star": {"count": 0, "percentage": 0},
                "1_star": {"count": 0, "percentage": 0}
            },
            "sentiment_analysis": {
                "overall": "No Data",
                "positive_mentions": 0,
                "negative_mentions": 0
            },
            "recurring_themes": [],
            "key_insights": ["No reviews available for analysis"],
            "recommendations": [
                "Encourage your first guests to leave reviews",
                "Offer excellent service to earn positive feedback",
                "Follow up with guests after checkout to request reviews"
            ],
            "summary": f"No reviews have been submitted for '{listing_title}' yet. Focus on delivering great experiences to earn your first reviews."
        }
    
    # 1. Compute average rating and distribution
    ratings = [r.rating for r in reviews]
    avg_rating = sum(ratings) / len(ratings)
    total_reviews = len(reviews)
    
    rating_distribution = {
        "5_star": {"count": ratings.count(5), "percentage": (ratings.count(5) / total_reviews) * 100},
        "4_star": {"count": ratings.count(4), "percentage": (ratings.count(4) / total_reviews) * 100},
        "3_star": {"count": ratings.count(3), "percentage": (ratings.count(3) / total_reviews) * 100},
        "2_star": {"count": ratings.count(2), "percentage": (ratings.count(2) / total_reviews) * 100},
        "1_star": {"count": ratings.count(1), "percentage": (ratings.count(1) / total_reviews) * 100},
    }
    
    # 2. Define satisfaction level
    if avg_rating >= 4:
        satisfaction_level = "Satisfied"
        satisfaction_emoji = "😊"
    elif avg_rating >= 3:
        satisfaction_level = "Neutral"
        satisfaction_emoji = "😐"
    else:
        satisfaction_level = "Dissatisfied"
        satisfaction_emoji = "😞"
    
    # 3. Perform sentiment analysis on review text
    positive_keywords = [
        "excellent", "great", "amazing", "perfect", "love", "wonderful", 
        "clean", "comfortable", "quality", "recommend", "spotless", "good",
        "friendly", "helpful", "responsive", "smooth", "easy", "best"
    ]
    negative_keywords = [
        "dirty", "bad", "poor", "terrible", "worst", "disappointing",
        "missing", "broken", "filthy", "uncomfortable", "awful", "slow",
        "rude", "late", "damaged", "problem", "issue", "complaint"
    ]
    
    positive_mentions = []
    negative_mentions = []
    
    for review in reviews:
        comment = (review.comment or "").lower()
        for word in positive_keywords:
            if word in comment:
                positive_mentions.append(word)
        for word in negative_keywords:
            if word in comment:
                negative_mentions.append(word)
    
    total_sentiment_words = len(positive_mentions) + len(negative_mentions)
    if total_sentiment_words > 0:
        positive_ratio = len(positive_mentions) / total_sentiment_words
        if positive_ratio >= 0.7:
            sentiment = "Very Positive"
        elif positive_ratio >= 0.5:
            sentiment = "Mostly Positive"
        elif positive_ratio >= 0.3:
            sentiment = "Mixed"
        else:
            sentiment = "Mostly Negative"
    else:
        sentiment = "Neutral"
    
    # 4. Identify recurring themes
    theme_definitions = {
        "Cleanliness": ["clean", "tidy", "spotless", "dirty", "filthy", "messy", "dust"],
        "Comfort": ["comfortable", "cozy", "uncomfortable", "soft", "bed", "sleep"],
        "Quality": ["quality", "excellent", "good", "poor", "bad", "condition"],
        "Communication": ["responsive", "helpful", "communication", "quick", "slow", "friendly", "rude"],
        "Value": ["worth", "value", "price", "expensive", "cheap", "affordable"],
        "Location": ["location", "convenient", "accessible", "far", "near"],
        "Amenities": ["amenities", "wifi", "parking", "pool", "kitchen", "missing"]
    }
    
    theme_counts = {}
    theme_sentiment = {}
    
    for theme, keywords in theme_definitions.items():
        count = 0
        positive = 0
        negative = 0
        for review in reviews:
            comment = (review.comment or "").lower()
            if any(kw in comment for kw in keywords):
                count += 1
                if review.rating >= 4:
                    positive += 1
                elif review.rating <= 2:
                    negative += 1
        if count > 0:
            theme_counts[theme] = count
            theme_sentiment[theme] = "positive" if positive > negative else ("negative" if negative > positive else "mixed")
    
    # Sort themes by frequency
    recurring_themes = sorted(theme_counts.items(), key=lambda x: x[1], reverse=True)[:5]
    
    # Analyze individual reviews to extract specific issues and praise
    specific_issues = []
    specific_praise = []
    
    issue_keywords = {
        "dirty": "cleanliness issue",
        "filthy": "cleanliness issue", 
        "messy": "cleanliness issue",
        "dust": "dust accumulation",
        "uncomfortable": "comfort issue",
        "broken": "broken item/facility",
        "missing": "missing item/amenity",
        "slow": "slow response/service",
        "rude": "staff/host attitude",
        "expensive": "pricing concern",
        "noisy": "noise issue",
        "small": "space too small",
        "old": "outdated facilities",
        "smell": "odor issue",
        "bug": "pest issue",
        "leak": "water leak issue",
        "cold": "temperature issue",
        "hot": "temperature issue",
        "wifi": "wifi/internet issue",
        "parking": "parking issue",
        "late": "late check-in/response"
    }
    
    praise_keywords = {
        "clean": "cleanliness",
        "spotless": "excellent cleanliness",
        "comfortable": "comfort",
        "cozy": "cozy atmosphere",
        "friendly": "friendly host",
        "helpful": "helpful service",
        "responsive": "quick response",
        "great": "great experience",
        "excellent": "excellent quality",
        "perfect": "perfect stay",
        "amazing": "amazing experience",
        "recommend": "highly recommended",
        "convenient": "convenient location",
        "spacious": "spacious room",
        "quiet": "peaceful environment",
        "value": "good value"
    }
    
    # Extract specific feedback from each review
    for review in reviews:
        comment = (review.comment or "").lower()
        rating = review.rating
        
        # Extract issues from low-rated reviews (1-3 stars)
        if rating <= 3:
            for keyword, issue_desc in issue_keywords.items():
                if keyword in comment:
                    # Extract context around the keyword
                    specific_issues.append({
                        "issue": issue_desc,
                        "rating": rating,
                        "from_review": review.comment[:100] + "..." if len(review.comment or "") > 100 else review.comment
                    })
        
        # Extract praise from high-rated reviews (4-5 stars)
        if rating >= 4:
            for keyword, praise_desc in praise_keywords.items():
                if keyword in comment:
                    specific_praise.append({
                        "praise": praise_desc,
                        "rating": rating
                    })
    
    # Remove duplicates and count occurrences
    issue_counts = {}
    for item in specific_issues:
        issue = item["issue"]
        if issue not in issue_counts:
            issue_counts[issue] = {"count": 0, "examples": []}
        issue_counts[issue]["count"] += 1
        if len(issue_counts[issue]["examples"]) < 2:  # Keep max 2 examples
            issue_counts[issue]["examples"].append(item["from_review"])
    
    praise_counts = {}
    for item in specific_praise:
        praise = item["praise"]
        praise_counts[praise] = praise_counts.get(praise, 0) + 1
    
    # Build key insights based on actual review content
    key_insights = []
    recommendations = []
    
    # Sort issues by frequency
    sorted_issues = sorted(issue_counts.items(), key=lambda x: x[1]["count"], reverse=True)
    sorted_praise = sorted(praise_counts.items(), key=lambda x: x[1], reverse=True)
    
    if satisfaction_level == "Satisfied":
        key_insights.append("Customers are highly satisfied with this listing")
        if sorted_praise:
            top_praises = [p[0] for p in sorted_praise[:3]]
            key_insights.append(f"Most praised aspects: {', '.join(top_praises)}")
        recommendations.append("Continue maintaining your high standards")
        recommendations.append("Consider raising prices given the positive feedback")
        recommendations.append("Encourage guests to share their positive experiences")
    else:
        # Provide specific insights based on actual issues found
        if sorted_issues:
            top_issues = [i[0] for i in sorted_issues[:3]]
            key_insights.append(f"Main issues identified: {', '.join(top_issues)}")
        
        if sorted_praise:
            top_praises = [p[0] for p in sorted_praise[:2]]
            key_insights.append(f"Positive aspects to maintain: {', '.join(top_praises)}")
        
        # Generate specific recommendations based on actual issues
        for issue, data in sorted_issues[:5]:
            count = data["count"]
            if issue == "cleanliness issue":
                recommendations.append(f"Cleanliness mentioned {count}x - Deep clean before each guest, consider professional cleaning service")
            elif issue == "dust accumulation":
                recommendations.append(f"Dust mentioned {count}x - Focus on dusting surfaces, air vents, and hidden areas")
            elif issue == "comfort issue":
                recommendations.append(f"Comfort mentioned {count}x - Upgrade mattress/pillows or add extra bedding options")
            elif issue == "broken item/facility":
                recommendations.append(f"Broken items mentioned {count}x - Inspect and repair/replace damaged items immediately")
            elif issue == "missing item/amenity":
                recommendations.append(f"Missing items mentioned {count}x - Check amenity checklist and restock essentials")
            elif issue == "slow response/service":
                recommendations.append(f"Slow response mentioned {count}x - Set up auto-replies and check messages more frequently")
            elif issue == "staff/host attitude":
                recommendations.append(f"Attitude mentioned {count}x - Focus on friendly, professional communication")
            elif issue == "pricing concern":
                recommendations.append(f"Pricing mentioned {count}x - Review your pricing or add more value/amenities")
            elif issue == "noise issue":
                recommendations.append(f"Noise mentioned {count}x - Provide earplugs or improve sound insulation")
            elif issue == "temperature issue":
                recommendations.append(f"Temperature mentioned {count}x - Check AC/heating system, provide fans or extra blankets")
            elif issue == "wifi/internet issue":
                recommendations.append(f"WiFi mentioned {count}x - Upgrade internet plan or add WiFi extenders")
            elif issue == "odor issue":
                recommendations.append(f"Odor mentioned {count}x - Deep clean carpets/fabrics, use air fresheners")
            elif issue == "pest issue":
                recommendations.append(f"Pest mentioned {count}x - Call pest control immediately")
            elif issue == "water leak issue":
                recommendations.append(f"Leak mentioned {count}x - Fix plumbing issues urgently")
            elif issue == "space too small":
                recommendations.append(f"Space mentioned {count}x - Update listing to set proper expectations about room size")
            elif issue == "outdated facilities":
                recommendations.append(f"Outdated facilities mentioned {count}x - Consider renovations or modernizing decor")
            elif issue == "parking issue":
                recommendations.append(f"Parking mentioned {count}x - Clarify parking situation in listing or provide alternatives")
            elif issue == "late check-in/response":
                recommendations.append(f"Late response mentioned {count}x - Use automated check-in or be more punctual")
    
    # Add general recommendations if no specific issues found
    if not recommendations:
        if satisfaction_level == "Neutral":
            recommendations.append("Respond to guest feedback and ask for specific improvement suggestions")
            recommendations.append("Small touches like welcome snacks can improve ratings")
        elif satisfaction_level == "Dissatisfied":
            recommendations.append("Reach out to recent guests to understand their concerns")
            recommendations.append("Consider pausing bookings until issues are resolved")
    
    # Build summary text
    summary = f"Based on {total_reviews} reviews with an average rating of {avg_rating:.1f}/5.0, "
    summary += f"the overall satisfaction is {satisfaction_level}. "
    
    if sorted_issues:
        summary += f"Key issues found: {', '.join([i[0] for i in sorted_issues[:3]])}. "
    if sorted_praise:
        summary += f"Guests appreciate: {', '.join([p[0] for p in sorted_praise[:2]])}. "
    if recommendations:
        summary += f"Priority action: {recommendations[0].split(' - ')[0] if ' - ' in recommendations[0] else recommendations[0]}"
    
    # Return clean JSON structure in exact sequence
    return {
        "title": f"Review Analysis for '{listing_title}'",
        "overall_satisfaction": {
            "level": satisfaction_level,
            "emoji": satisfaction_emoji,
            "average_rating": round(avg_rating, 1),
            "max_rating": 5.0
        },
        "total_reviews": total_reviews,
        "rating_distribution": {
            "5_star": {"count": rating_distribution["5_star"]["count"], "percentage": round(rating_distribution["5_star"]["percentage"])},
            "4_star": {"count": rating_distribution["4_star"]["count"], "percentage": round(rating_distribution["4_star"]["percentage"])},
            "3_star": {"count": rating_distribution["3_star"]["count"], "percentage": round(rating_distribution["3_star"]["percentage"])},
            "2_star": {"count": rating_distribution["2_star"]["count"], "percentage": round(rating_distribution["2_star"]["percentage"])},
            "1_star": {"count": rating_distribution["1_star"]["count"], "percentage": round(rating_distribution["1_star"]["percentage"])}
        },
        "sentiment_analysis": {
            "overall": sentiment,
            "positive_mentions": len(positive_mentions),
            "negative_mentions": len(negative_mentions)
        },
        "recurring_themes": [
            {
                "theme": t,
                "mention_count": c,
                "sentiment": theme_sentiment.get(t, "neutral")
            } for t, c in recurring_themes
        ],
        "key_insights": key_insights,
        "recommendations": recommendations,
        "summary": summary
    }


# Create the ReviewAnalysisAgent LLM agent
review_agent = LlmAgent(
    model="gemini-2.5-flash",
    name="ReviewAnalysisAgent",
    description="Analyzes customer reviews to provide satisfaction levels, rating distributions, sentiment analysis, and recurring themes in JSON format.",
    instruction=(
        "You are a customer review analysis specialist. Your role is to analyze customer feedback for rental listings.\n\n"
        "When responding to a query:\n"
        "1. If the listing ID is not provided, ask the user for it.\n"
        "2. Use the `analyze_reviews` tool to get the review analytics.\n"
        "3. Return ONLY the JSON object from the tool result - do not wrap it in another object.\n"
        "4. Do not add any text before or after the JSON.\n"
        "5. Do not use markdown code blocks.\n\n"
        "Example output format:\n"
        '{"listing_id": "...", "listing_title": "...", "total_reviews": 10, ...}\n\n'
        "This is a read-only agent. Return the tool result as-is without modification."
    ),
    tools=[analyze_reviews],
)
