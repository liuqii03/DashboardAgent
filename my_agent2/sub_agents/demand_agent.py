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
    5. Suggest what types of listings owner could add

    :param owner_id: ID of the owner to analyze
    :return: Dictionary with market trends and suggestions
    """
    # Get all listings in the market
    all_listings = db.get_all_listings()
    
    # Get owner's listings
    owner_listings = db.get_listings_by_owner(owner_id)
    
    if not all_listings:
        return {
            "owner_id": owner_id,
            "message": "No market data available for analysis.",
            "suggestions": []
        }
    
    # Analyze market by listing type
    type_stats = defaultdict(lambda: {
        "count": 0,
        "total_bookings": 0,
        "total_revenue": 0.0,
        "avg_price": 0.0,
        "listings": []
    })
    
    for listing in all_listings:
        listing_type = listing.type or "Other"
        type_stats[listing_type]["count"] += 1
        type_stats[listing_type]["listings"].append(listing)
        
        # Get bookings for this listing
        bookings = db.get_bookings(listing.listingId)
        type_stats[listing_type]["total_bookings"] += len(bookings)
        
        for booking in bookings:
            if booking.status == "CONFIRMED":
                type_stats[listing_type]["total_revenue"] += float(booking.totalPrice)
    
    # Calculate averages and trends
    trending_types = []
    for listing_type, stats in type_stats.items():
        if stats["count"] > 0:
            stats["avg_bookings"] = stats["total_bookings"] / stats["count"]
            stats["avg_revenue"] = stats["total_revenue"] / stats["count"]
            
            # Calculate average price
            prices = [l.basePrice for l in stats["listings"] if l.basePrice > 0]
            stats["avg_price"] = sum(prices) / len(prices) if prices else 0
            
            # Calculate trend score (higher = more trending)
            trend_score = (stats["avg_bookings"] * 2) + (stats["avg_revenue"] / 100)
            
            trending_types.append({
                "type": listing_type,
                "listing_count": stats["count"],
                "total_bookings": stats["total_bookings"],
                "avg_bookings": round(stats["avg_bookings"], 1),
                "total_revenue": round(stats["total_revenue"], 2),
                "avg_revenue": round(stats["avg_revenue"], 2),
                "avg_price": round(stats["avg_price"], 2),
                "trend_score": round(trend_score, 2)
            })
    
    # Sort by trend score
    trending_types.sort(key=lambda x: x["trend_score"], reverse=True)
    
    # Analyze owner's current portfolio
    owner_types = set()
    owner_revenue = 0.0
    owner_bookings = 0
    
    for listing in owner_listings:
        owner_types.add(listing.type or "Other")
        bookings = db.get_bookings(listing.listingId)
        owner_bookings += len(bookings)
        for booking in bookings:
            if booking.status == "CONFIRMED":
                owner_revenue += float(booking.totalPrice)
    
    # Generate suggestions
    suggestions = []
    
    # Find trending types owner doesn't have
    for trend in trending_types[:5]:  # Top 5 trending
        if trend["type"] not in owner_types and trend["avg_bookings"] >= 1:
            suggestions.append({
                "type": trend["type"],
                "reason": f"High demand with {trend['avg_bookings']:.1f} avg bookings per listing",
                "potential_revenue": f"${trend['avg_revenue']:.2f} avg revenue per listing",
                "market_price": f"${trend['avg_price']:.2f} average price",
                "priority": "High" if trend["trend_score"] > 5 else "Medium"
            })
    
    # If owner has trending types, suggest expanding
    for trend in trending_types[:3]:
        if trend["type"] in owner_types:
            owner_count = sum(1 for l in owner_listings if l.type == trend["type"])
            if owner_count < 3:  # Room to expand
                suggestions.append({
                    "type": trend["type"],
                    "reason": f"You already have {owner_count} {trend['type']} listing(s). This type is trending!",
                    "potential_revenue": f"Consider adding more to capitalize on demand",
                    "market_price": f"${trend['avg_price']:.2f} average price",
                    "priority": "Medium"
                })
    
    # Build summary
    top_trending = trending_types[:3] if trending_types else []
    
    summary_parts = [
        f"📈 **Market Trend Analysis**\n\n",
        f"**Your Portfolio:**\n",
        f"  • Total Listings: {len(owner_listings)}\n",
        f"  • Types: {', '.join(owner_types) if owner_types else 'None'}\n",
        f"  • Total Bookings: {owner_bookings}\n",
        f"  • Total Revenue: ${owner_revenue:.2f}\n\n",
        f"**Top Trending Listing Types:**\n"
    ]
    
    for i, trend in enumerate(top_trending, 1):
        emoji = "🔥" if trend["trend_score"] > 5 else "📊"
        summary_parts.append(
            f"  {i}. {emoji} **{trend['type']}** - {trend['total_bookings']} bookings, "
            f"${trend['total_revenue']:.2f} total revenue\n"
        )
    
    if suggestions:
        summary_parts.append(f"\n**Suggestions to Increase Revenue:**\n")
        for i, sug in enumerate(suggestions[:3], 1):
            priority_emoji = "🚀" if sug["priority"] == "High" else "💡"
            summary_parts.append(
                f"  {i}. {priority_emoji} **{sug['type']}**: {sug['reason']}\n"
                f"     Potential: {sug['potential_revenue']}\n"
            )
    else:
        summary_parts.append(f"\n✅ Your portfolio covers the trending types well!\n")
    
    summary = "".join(summary_parts)
    
    return {
        "owner_id": owner_id,
        "owner_listings_count": len(owner_listings),
        "owner_types": list(owner_types),
        "owner_total_bookings": owner_bookings,
        "owner_total_revenue": round(owner_revenue, 2),
        "trending_types": trending_types[:5],
        "suggestions": suggestions[:5],
        "summary": summary,
        "message": "Market trend analysis complete."
    }


# Create the DemandTrendAgent LLM agent
demand_agent = LlmAgent(
    model="gemini-2.5-flash",
    name="DemandTrendAgent",
    description="Analyzes market trends to identify trending listing types and suggests what owners can rent to increase revenue.",
    instruction=(
        "You are a market trend analyst for peer-to-peer rentals. Your role is to help owners understand market demand and make strategic decisions.\n\n"
        "Your analysis includes:\n"
        "- Identifying which listing types are currently trending in the market\n"
        "- Analyzing booking patterns across different listing categories\n"
        "- Comparing the owner's portfolio with market trends\n"
        "- Suggesting what types of listings the owner could add to increase revenue\n\n"
        "When responding to a query:\n"
        "1. If the owner ID is not clear, politely ask the user to provide it.\n"
        "2. Use the `analyze_market_trends` tool to get market analysis.\n"
        "3. Present clearly:\n"
        "   - Current portfolio summary\n"
        "   - Top trending listing types in the market\n"
        "   - Specific suggestions for new listings\n"
        "   - Priority recommendations\n\n"
        "IMPORTANT: This is a read-only advisory agent. You provide insights and suggestions, "
        "but you cannot make changes to listings or the database.\n\n"
        "Be encouraging and provide actionable insights that help owners grow their rental business."
    ),
    tools=[analyze_market_trends],
)

