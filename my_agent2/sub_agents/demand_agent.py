from google.adk.agents import LlmAgent

"""
Demand tools for the analytics dashboard.

These functions interface with the in-memory database to fetch demand
metrics for any listing and to update the price of a listing. They
allow agents to make data-driven decisions based on recent booking
activity.

In a real-world application, these would query or update a persistent
database or external service. Here, they operate on the `database.db`
global instance defined in `database.py`.
"""

from typing import Dict, Any

from ..database.database import db


def fetch_demand_data(listing_id: str) -> Dict[str, Any]:
    """
    Retrieve demand data for a listing based on recent bookings.

    Demand is calculated as the proportion of booked days to the last
    30-day period. If the occupancy is high (greater than 60%), demand
    is considered high; if between 30% and 60%, medium; otherwise low.

    :param listing_id: Identifier of the listing to check.
    :return: A dictionary with demand information including the demand
             level, occupancy rate, and a message summarizing the
             result.
    """
    bookings = db.get_bookings(listing_id)
    # Calculate total booked days in the last 30 days
    total_days_booked = 0
    period_days = 30
    for booking in bookings:
        # Clamp booking duration to a positive number of days
        days = (booking.endDate - booking.startDate).days
        total_days_booked += max(days, 0)
    occupancy = total_days_booked / period_days if period_days > 0 else 0.0
    # Determine demand level based on occupancy threshold
    if occupancy > 0.6:
        demand_level = "high"
    elif occupancy > 0.3:
        demand_level = "medium"
    else:
        demand_level = "low"
    message = (
        f"Demand is {demand_level} for listing '{listing_id}' "
        f"(current occupancy {occupancy*100:.0f}%)."
    )
    return {
        "listing_id": listing_id,
        "demand_level": demand_level,
        "current_occupancy": occupancy,
        "message": message,
    }


def update_price(listing_id: str, increase_percent: float = 10.0) -> Dict[str, Any]:
    """
    Increase the base price of a listing by a given percentage.

    Delegates to the database instance to perform the price update and
    returns the result. This operation does not apply the update
    directly until the user explicitly confirms they want to apply it.

    :param listing_id: Identifier of the listing to update.
    :param increase_percent: Percentage to increase the price by.
    :return: A dictionary with status and message from the database.
    """
    return db.update_listing_price(listing_id, increase_percent)

# Instantiate the demand pricing agent
demand_agent = LlmAgent(
    # Use a lightweight model suitable for natural language routing and analysis.
    model="gemini-2.5-flash",
    name="DemandPricingAgent",
    description="Analyzes demand for any listing and recommends price adjustments when appropriate.",
    instruction=(
        "You are an expert in dynamic demand and pricing for peer‑to‑peer rentals. Your goal is to help owners optimise pricing based on current demand.\n\n"
        "Follow these guidelines when responding to a user:\n"
        "1. Identify which listing the user is referring to by parsing a listing ID or name from their message.\n" 
        "   If it is not clear, politely ask the user to specify the listing ID (e.g. 'veh001' or 'cam001').\n"
        "   When you ask for the listing ID, wait for the user to reply and then remember the ID they provide. Use that listing ID in subsequent steps.\n"
        "   If you are being called as part of a multi‑aspect analysis and the listing ID was provided earlier, do not ask for the ID again – simply use the existing ID for your analysis.\n"
        "2. Use the `fetch_demand_data` tool with the listing_id parameter to retrieve demand metrics \n"
        "   (occupancy rate and demand level). Summarise these results concisely for the user.\n"
        "3. If the demand level is **high** (e.g. occupancy > 60%), recommend a price increase. \n"
        "   Suggest a reasonable percentage (for example 5–10%) and explain why increasing the price can \n"
        "   maximise earnings in periods of high demand.\n"
        "4. After making your recommendation, ask the owner if they would like you to apply the price increase. \n"
        "   Only call the `update_price` tool with the listing_id and increase_percent if the user explicitly confirms.\n"
        "5. If demand is **medium** or **low**, explain that no price adjustment is necessary at this time.\n\n"
        "If the user’s question is actually about booking durations, occupancy trends, discount strategies, or review sentiment, \n"
        "do not attempt to answer. Instead, call the ADK function `transfer_to_agent` with the name of the \n"
        "appropriate agent: 'BookingTrendAgent' for booking questions or 'ReviewAnalysisAgent' for review questions, \n"
        "and explain that you specialise in pricing.\n"
        "If the user asks to analyse **all aspects** or mentions multiple domains (pricing, bookings and reviews), after you provide your analysis, call \n"
        "`transfer_to_agent` with 'BookingTrendAgent' to continue the multi‑aspect analysis chain. This will allow the BookingTrendAgent \n"
        "to perform its analysis next.\n"
        "When the user’s intent is unclear, ask a clarifying question before proceeding. "
        "Always remain clear and helpful, and never assume actions without user confirmation."
    ),
    tools=[fetch_demand_data, update_price],
)

