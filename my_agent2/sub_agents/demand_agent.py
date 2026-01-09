from google.adk.agents import LlmAgent

"""
Demand Trend Agent for the analytics dashboard.

This agent analyzes market trends to help owners understand:
- Which types of listings are currently trending
- What the owner can rent to increase their revenue
- Market insights and suggestions for new listings

This is a READ-ONLY advisory agent.
"""

from typing import Dict, Any, List
from collections import defaultdict

from ..database.api_db import api_db as db


def analyze_market_trends(owner_id: int) -> Dict[str, Any]:
    """
    Analyze market trends to identify trending listing types and provide suggestions.

    Core Logic:
    1. Analyze all listings in the market by type
    2. Calculate booking frequency and revenue by listing type
    3. Identify which types are trending (high demand)
    4. Compare with owner's current listings
    5. Provide priority recommendations

    :param owner_id: ID of the owner to analyze
    :return: Dictionary with market trends and recommendations
    """
    # Get all listings in the market
    all_listings = db.get_all_listings()
    
    # Get owner's listings
    owner_listings = db.get_listings_by_owner(owner_id)
    
    if not all_listings:
        return {
            "title": "Market Trend Analysis",
            "portfolio": {},
            "trending_types": [],
            "recommendations": [],
            "message": "No market data available for analysis."
        }
    
    # Get ALL bookings once (more efficient than calling per listing)
    all_bookings = db.get_all_bookings()
    
    # Group bookings by listing ID for quick lookup
    bookings_by_listing: Dict[str, List] = defaultdict(list)
    for booking in all_bookings:
        bookings_by_listing[booking.listingId].append(booking)
    
    # Analyze market by listing type
    type_stats = defaultdict(lambda: {
        "count": 0,
        "total_bookings": 0,
        "total_revenue": 0.0,
        "listings": []
    })
    
    for listing in all_listings:
        listing_type = listing.type or "Other"
        type_stats[listing_type]["count"] += 1
        type_stats[listing_type]["listings"].append(listing)
        
        # Get bookings for this listing from our pre-fetched data
        listing_bookings = bookings_by_listing.get(listing.listingId, [])
        type_stats[listing_type]["total_bookings"] += len(listing_bookings)
        
        for booking in listing_bookings:
            if booking.status in ["CONFIRMED", "COMPLETED"]:
                type_stats[listing_type]["total_revenue"] += float(booking.totalPrice)
    
    # Calculate trends
    trending_types = []
    for listing_type, stats in type_stats.items():
        if stats["count"] > 0:
            # Calculate trend score (higher = more trending)
            avg_bookings = stats["total_bookings"] / stats["count"]
            avg_revenue = stats["total_revenue"] / stats["count"]
            trend_score = (avg_bookings * 2) + (avg_revenue / 100)
            
            trending_types.append({
                "type": listing_type,
                "listing_count": stats["count"],
                "trend_score": round(trend_score, 2)
            })
    
    # Sort by trend score
    trending_types.sort(key=lambda x: x["trend_score"], reverse=True)
    
    # Analyze owner's current portfolio
    owner_types = set()
    owner_revenue = 0.0
    owner_bookings = 0
    
    # Track owner's bookings per listing for recommendation logic
    owner_listings_with_bookings = {}
    
    for listing in owner_listings:
        owner_types.add(listing.type or "Other")
        listing_bookings = bookings_by_listing.get(listing.listingId, [])
        booking_count = len([b for b in listing_bookings if b.status in ["CONFIRMED", "COMPLETED"]])
        owner_listings_with_bookings[listing.listingId] = {
            "type": listing.type,
            "title": listing.title,
            "bookings": booking_count
        }
        owner_bookings += booking_count
        for booking in listing_bookings:
            if booking.status in ["CONFIRMED", "COMPLETED"]:
                owner_revenue += float(booking.totalPrice)
    
    # Generate priority recommendations
    recommendations = []
    
    for trend in trending_types[:5]:  # Check top 5 trending types
        if trend["type"] in owner_types:
            # Owner HAS this trending type
            owner_count = sum(1 for l in owner_listings if l.type == trend["type"])
            
            # Check if owner has bookings for this type
            owner_type_bookings = sum(
                info["bookings"] for lid, info in owner_listings_with_bookings.items() 
                if info["type"] == trend["type"]
            )
            
            if trend["trend_score"] > 5 and owner_type_bookings > 0:
                # High performer with bookings - encourage!
                recommendations.append({
                    "type": trend["type"],
                    "status": "on_track",
                    "message": f"Excellent! Your {owner_count} {trend['type']} listing(s) are performing well in a high-demand category.",
                    "advice": "Keep maintaining quality and competitive pricing to maximize bookings."
                })
            elif trend["trend_score"] > 0 and owner_type_bookings == 0:
                # In trending category but NO bookings - suggest improvements
                recommendations.append({
                    "type": trend["type"],
                    "status": "needs_improvement",
                    "message": f"Your {owner_count} {trend['type']} listing(s) are in a trending category but have no completed bookings yet.",
                    "advice": "Try these improvements: 1) Add high-quality photos, 2) Write detailed descriptions, 3) Set competitive pricing, 4) Respond quickly to inquiries, 5) Offer flexible booking options."
                })
            elif owner_type_bookings > 0:
                # Has some bookings
                recommendations.append({
                    "type": trend["type"],
                    "status": "on_track",
                    "message": f"Good job! Your {owner_count} {trend['type']} listing(s) are getting bookings.",
                    "advice": "Continue optimizing your listings to capture more bookings."
                })
            else:
                # Low market activity overall
                recommendations.append({
                    "type": trend["type"],
                    "status": "low_demand",
                    "message": f"You have {owner_count} {trend['type']} listing(s). Market activity for this type is currently low.",
                    "advice": "Monitor market trends and consider diversifying your portfolio."
                })
        else:
            # Owner DOESN'T have this trending type - suggest adding if high demand
            if trend["trend_score"] > 3:
                recommendations.append({
                    "type": trend["type"],
                    "status": "opportunity",
                    "message": f"Consider adding {trend['type']} listings to your portfolio.",
                    "advice": f"This category is trending with {trend['listing_count']} listings in the market and a trend score of {trend['trend_score']}."
                })
    
    return {
        "title": "Market Trend Analysis",
        "portfolio": {
            "total_listings": len(owner_listings),
            "types": list(owner_types),
            "total_bookings": owner_bookings,
            "total_revenue": round(owner_revenue, 2)
        },
        "trending_types": trending_types[:5],
        "recommendations": recommendations,
        "message": "Market trend analysis complete."
    }


# Create the DemandTrendAgent LLM agent
demand_agent = LlmAgent(
    model="gemini-2.5-flash",
    name="DemandTrendAgent",
    description="Analyzes market trends to identify trending listing types and provides priority recommendations.",
    instruction=(
        "You are a market trend analyst for peer-to-peer rentals. Your role is to help owners understand market demand and make strategic decisions.\n\n"
        "When responding to a query:\n"
        "1. If the owner ID is not clear, politely ask the user to provide it.\n"
        "2. Use the `analyze_market_trends` tool to get market analysis.\n"
        "3. Return the results in JSON format.\n\n"
        "IMPORTANT: This is a read-only advisory agent. You provide insights and recommendations, "
        "but you cannot make changes to listings or the database.\n\n"
        "OUTPUT FORMAT: You MUST respond with ONLY valid JSON, no markdown formatting, no code blocks, no extra text.\n"
        "Return the exact JSON structure from the tool result:\n"
        "{\n"
        '  "title": "Market Trend Analysis",\n'
        '  "portfolio": { "total_listings": <n>, "types": [...], "total_bookings": <n>, "total_revenue": <n> },\n'
        '  "trending_types": [{ "type": "...", "listing_count": <n>, "total_bookings": <n>, "total_revenue": <n>, "trend_score": <n> }],\n'
        '  "recommendations": [{ "type": "...", "status": "...", "message": "...", "advice": "..." }],\n'
        '  "message": "Market trend analysis complete."\n'
        "}"
    ),
    tools=[analyze_market_trends],
)

