from google.adk.agents import LlmAgent

"""
Pricing Agent for the analytics dashboard.

This agent handles dynamic pricing recommendations:
- Identifies high-demand periods (weekends, holidays) by counting bookings
- Suggests price adjustments (±10%) based on demand and conversion rates
- Outputs: current price, suggested price, reasons, and notes
- Can take action to update prices when user clicks "Take Action"
"""

from typing import Dict, Any
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

from ..database.api_db import api_db as db

# Malaysia timezone
MALAYSIA_TZ = ZoneInfo("Asia/Kuala_Lumpur")


def analyze_pricing(listing_id: str) -> Dict[str, Any]:
    """
    Analyze pricing for a listing and provide recommendations.

    Core Logic:
    1. Identify high-demand periods (weekends, holidays) by counting bookings
    2. Calculate demand level based on booking patterns
    3. Suggest price adjustment (±10%) based on demand
    4. Output: current price, suggested price, reasons, notes

    :param listing_id: Identifier of the listing to analyze
    :return: Dictionary with pricing analysis and recommendations
    """
    bookings = db.get_bookings(listing_id)
    listing = db.get_listing(listing_id)
    
    if not listing:
        return {
            "listing_id": listing_id,
            "error": True,
            "message": f"Listing '{listing_id}' not found."
        }
    
    listing_title = listing.title
    current_price = float(listing.pricePerDay) if hasattr(listing, 'pricePerDay') else float(listing.basePrice)
    
    # Analyze booking patterns
    total_bookings = len(bookings)
    weekend_bookings = 0
    weekday_bookings = 0
    total_days_booked = 0
    total_revenue = 0.0
    
    # Malaysian Public Holidays 2026 (with buffer days for travel)
    # Format: (start_date, end_date, holiday_name)
    malaysian_holidays = [
        (datetime(2026, 1, 1), datetime(2026, 1, 2), "New Year"),
        (datetime(2026, 1, 14), datetime(2026, 1, 15), "Thaipusam"),
        (datetime(2026, 2, 1), datetime(2026, 2, 2), "Federal Territory Day"),
        (datetime(2026, 2, 17), datetime(2026, 2, 20), "Chinese New Year"),
        (datetime(2026, 3, 20), datetime(2026, 3, 23), "Hari Raya Aidilfitri"),
        (datetime(2026, 5, 1), datetime(2026, 5, 2), "Labour Day"),
        (datetime(2026, 5, 12), datetime(2026, 5, 13), "Wesak Day"),
        (datetime(2026, 5, 27), datetime(2026, 5, 30), "Hari Raya Haji"),
        (datetime(2026, 6, 1), datetime(2026, 6, 2), "Agong Birthday"),
        (datetime(2026, 6, 17), datetime(2026, 6, 18), "Awal Muharram"),
        (datetime(2026, 8, 26), datetime(2026, 8, 27), "Maulidur Rasul"),
        (datetime(2026, 8, 31), datetime(2026, 9, 1), "Merdeka Day"),
        (datetime(2026, 9, 16), datetime(2026, 9, 17), "Malaysia Day"),
        (datetime(2026, 11, 8), datetime(2026, 11, 9), "Deepavali"),
        (datetime(2026, 12, 25), datetime(2026, 12, 26), "Christmas"),
    ]
    
    # School holidays in Malaysia 2026 (approximate)
    school_holidays = [
        (datetime(2026, 3, 13), datetime(2026, 3, 22), "March School Holiday"),
        (datetime(2026, 5, 23), datetime(2026, 6, 7), "Mid-Year School Holiday"),
        (datetime(2026, 8, 15), datetime(2026, 8, 23), "August School Holiday"),
        (datetime(2026, 11, 21), datetime(2026, 12, 31), "Year-End School Holiday"),
    ]
    
    holiday_bookings = 0
    school_holiday_bookings = 0
    matched_holidays = []
    recent_bookings = 0  # Last 30 days
    recent_days_booked = 0  # Days booked in last 30 days (for occupancy)
    
    # Get current time in Malaysia timezone
    now = datetime.now(MALAYSIA_TZ).replace(tzinfo=None)
    thirty_days_ago = now - timedelta(days=30)
    
    for booking in bookings:
        days = max((booking.endDate - booking.startDate).days, 0)
        total_days_booked += days
        
        if booking.status == "CONFIRMED":
            total_revenue += float(booking.totalPrice)
        
        # Check if weekend booking
        start_weekday = booking.startDate.weekday()
        if start_weekday >= 5:  # Saturday=5, Sunday=6
            weekend_bookings += 1
        else:
            weekday_bookings += 1
        
        # Check if Malaysian public holiday booking
        booking_start = booking.startDate.replace(tzinfo=None)
        booking_end = booking.endDate.replace(tzinfo=None)
        
        for holiday_start, holiday_end, holiday_name in malaysian_holidays:
            if holiday_start <= booking_start <= holiday_end:
                holiday_bookings += 1
                if holiday_name not in matched_holidays:
                    matched_holidays.append(holiday_name)
                break
        
        # Check if school holiday booking
        for school_start, school_end, school_name in school_holidays:
            if school_start <= booking_start <= school_end:
                school_holiday_bookings += 1
                break
        
        # Check if recent booking (within last 30 days)
        if booking_start >= thirty_days_ago:
            recent_bookings += 1
            # Calculate days booked within the 30-day window
            overlap_start = max(booking_start, thirty_days_ago)
            overlap_end = min(booking_end, now)
            if overlap_end > overlap_start:
                recent_days_booked += (overlap_end - overlap_start).days
    
    # Calculate occupancy rate (last 30 days only)
    # Days booked in last 30 days / 30 days
    occupancy_rate = min(recent_days_booked / 30.0, 1.0) if recent_days_booked > 0 else 0.0
    
    # Calculate conversion rate (bookings per view - simplified as bookings/10)
    conversion_rate = min(total_bookings / 10.0, 1.0) if total_bookings > 0 else 0.0
    
    # Determine demand level
    demand_indicators = []
    demand_score = 0
    
    if occupancy_rate >= 0.7:
        demand_score += 3
        demand_indicators.append("High occupancy rate (≥70%)")
    elif occupancy_rate >= 0.4:
        demand_score += 1
        demand_indicators.append("Moderate occupancy rate")
    
    if weekend_bookings > weekday_bookings:
        demand_score += 1
        demand_indicators.append("Strong weekend demand")
    
    if holiday_bookings > 0:
        demand_score += 2
        demand_indicators.append(f"{holiday_bookings} public holiday bookings ({', '.join(matched_holidays[:2])})")
    
    if school_holiday_bookings > 0:
        demand_score += 1
        demand_indicators.append(f"{school_holiday_bookings} school holiday bookings")
    
    if recent_bookings >= 3:
        demand_score += 2
        demand_indicators.append("Strong recent booking activity")
    elif recent_bookings >= 1:
        demand_score += 1
        demand_indicators.append("Some recent booking activity")
    
    # Determine recommendation
    if demand_score >= 5:
        demand_level = "High"
        adjustment_percent = 10.0
        adjustment_direction = "increase"
    elif demand_score >= 3:
        demand_level = "Medium"
        adjustment_percent = 5.0
        adjustment_direction = "increase"
    elif demand_score >= 1:
        demand_level = "Low"
        adjustment_percent = 0.0
        adjustment_direction = "maintain"
    else:
        demand_level = "Very Low"
        adjustment_percent = -10.0
        adjustment_direction = "decrease"
    
    # Calculate suggested price
    suggested_price = current_price * (1 + adjustment_percent / 100)
    price_difference = suggested_price - current_price
    
    # Build reasons
    reasons = []
    if adjustment_direction == "increase":
        reasons.append(f"Demand level is {demand_level}")
        reasons.extend(demand_indicators)
        reasons.append(f"Current occupancy: {occupancy_rate*100:.0f}%")
    elif adjustment_direction == "decrease":
        reasons.append("Low booking activity detected")
        reasons.append("Price reduction may attract more renters")
        reasons.append(f"Current occupancy: {occupancy_rate*100:.0f}%")
    else:
        reasons.append("Current pricing appears optimal for demand level")
        reasons.append(f"Occupancy rate: {occupancy_rate*100:.0f}%")
    
    # Return clean JSON structure
    return {
        "title": f"Pricing Analysis for '{listing_title}'",
        "current_price": current_price,
        "suggested_price": round(suggested_price, 2),
        "price_difference": round(price_difference, 2),
        "adjustment_percent": adjustment_percent,
        "adjustment_direction": adjustment_direction,
        "demand_level": demand_level,
        "reasons": reasons,
        "can_take_action": adjustment_percent != 0
    }


def apply_price_change(listing_id: str, new_price: float) -> Dict[str, Any]:
    """
    Apply the suggested price change to a listing.
    This is called when user clicks "Take Action" button.

    :param listing_id: Identifier of the listing to update
    :param new_price: The new price to set
    :return: Dictionary with update result
    """
    listing = db.get_listing(listing_id)
    
    if not listing:
        return {
            "success": False,
            "message": f"Listing '{listing_id}' not found."
        }
    
    old_price = float(listing.pricePerDay) if hasattr(listing, 'pricePerDay') else float(listing.basePrice)
    
    # Calculate the percentage change for the database update
    if old_price > 0:
        percent_change = ((new_price - old_price) / old_price) * 100
    else:
        percent_change = 0
    
    # Call the database update function
    result = db.update_listing_price(listing_id, percent_change)
    
    if result.get("status") == "success":
        return {
            "success": True,
            "listing_id": listing_id,
            "listing_title": listing.title,
            "old_price": old_price,
            "new_price": new_price,
            "message": f"✅ Price updated successfully for '{listing.title}' from ${old_price:.2f} to ${new_price:.2f}."
        }
    else:
        return {
            "success": False,
            "message": result.get("message", "Failed to update price.")
        }


# Create the PricingAgent LLM agent
pricing_agent = LlmAgent(
    model="gemini-2.5-flash",
    name="PricingAgent",
    description="Analyzes demand patterns and provides dynamic pricing recommendations in JSON format.",
    instruction=(
        "You are a dynamic pricing specialist for peer-to-peer rentals.\n\n"
        "When responding to a query:\n"
        "1. If the listing ID is not provided, ask the user for it.\n"
        "2. Use the `analyze_pricing` tool to get pricing analysis.\n"
        "3. Return ONLY the JSON object from the tool result - do not wrap it in another object.\n"
        "4. Do not add any text before or after the JSON.\n"
        "5. Do not use markdown code blocks.\n\n"
        "ACTION CAPABILITY:\n"
        "When the user wants to apply the price change, use the `apply_price_change` tool "
        "with the listing_id and the suggested new_price to update the database.\n\n"
        "Return the tool result as-is in JSON format."
    ),
    tools=[analyze_pricing, apply_price_change],
)
