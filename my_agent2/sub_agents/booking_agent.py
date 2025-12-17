from google.adk.agents import LlmAgent

"""
Booking tools for the analytics dashboard.

These functions interface with the in-memory database to fetch booking
statistics for any listing and to apply a discount for longer
bookings. They support agents in making recommendations to improve
occupancy and booking duration.

In production, these would interface with a booking management system
or database.
"""

from typing import Dict, Any

from ..database.database import db


def fetch_booking_data(listing_id: str) -> Dict[str, Any]:
    """
    Retrieve booking data for a listing including average booking
    duration and occupancy rate.

    :param listing_id: Identifier of the listing to check.
    :return: A dictionary with average duration (days), occupancy rate,
             and a message summarizing the results.
    """
    bookings = db.get_bookings(listing_id)
    if not bookings:
        # No bookings means zero occupancy and undefined average duration
        return {
            "listing_id": listing_id,
            "avg_duration_days": 0.0,
            "occupancy_rate": 0.0,
            "message": (
                f"There are no bookings for listing '{listing_id}' at the moment. "
                "Occupancy is 0%."
            ),
        }
    total_days = 0
    for booking in bookings:
        days = (booking.endDate - booking.startDate).days
        total_days += max(days, 0)
    avg_duration = total_days / len(bookings)
    occupancy = total_days / 30.0  # occupancy over 30-day period
    message = (
        f"Avg booking duration: {avg_duration:.1f} days, "
        f"occupancy: {occupancy*100:.0f}% for listing '{listing_id}'."
    )
    return {
        "listing_id": listing_id,
        "avg_duration_days": avg_duration,
        "occupancy_rate": occupancy,
        "message": message,
    }


def apply_discount(listing_id: str, discount_percent: float = 10.0) -> Dict[str, Any]:
    """
    Apply a discount to a listing to encourage longer bookings.

    Delegates to the database to record the discount and returns the
    result. This tool does not automatically change the listing's
    availability or pricing logic; it merely records the discount
    percent for demonstration purposes.

    :param listing_id: Identifier of the listing to discount.
    :param discount_percent: Percentage discount to apply.
    :return: A dictionary with status and message from the database.
    """
    return db.apply_discount(listing_id, discount_percent)

# Instantiate the booking trend agent
booking_agent = LlmAgent(
    # Use a lightweight model appropriate for trend analysis and delegation
    model="gemini-2.5-flash",
    name="BookingTrendAgent",
    description="Analyzes booking patterns and suggests discounts when appropriate.",
    instruction=(
        "You are an expert in monitoring booking trends and utilisation for any listing.\n\n"
        "Follow these steps when responding to a user query:\n"
        "1. Determine which listing the user is asking about by looking for a listing ID or name in their message. \n"
        "   If it is not clear, politely ask the user to specify the listing ID.\n"
        "   When you ask for the listing ID, wait for the user to reply and then remember the ID they provide. Use that listing ID in subsequent steps.\n"
        "   If you are being called as part of a multi‑aspect analysis and the listing ID has already been provided, do not ask for the ID again – simply use the provided ID for your analysis.\n"
        "2. Use the `fetch_booking_data` tool with the listing_id parameter to get the average booking duration and \n"
        "   occupancy rate for that listing. Summarise these metrics clearly for the user.\n"
        "3. If the average booking duration is shorter than two days or the occupancy rate is below 50%, recommend \n"
        "   offering a discount to encourage longer bookings and improve utilisation. Suggest a specific discount \n"
        "   percentage (for example 10–20%) and explain why it could help.\n"
        "4. Ask the owner if they would like you to apply the discount. Only call the `apply_discount` tool with the \n"
        "   listing_id and discount_percent when the user explicitly confirms.\n"
        "5. If booking trends are healthy (average duration ≥ 2 days and occupancy ≥ 50%), explain that no discount \n"
        "   is needed at this time.\n\n"
        "If the user’s query is actually about pricing, demand or reviews, do not attempt to answer it. \n"
        "Instead, call `transfer_to_agent` with 'DemandPricingAgent' for pricing questions or 'ReviewAnalysisAgent' \n"
        "for review questions, explaining that you specialise in booking trends.\n"
        "If the user asks to analyse **all aspects** or mentions multiple domains (pricing, bookings and reviews), after you provide your analysis, call \n"
        "`transfer_to_agent` with 'ReviewAnalysisAgent' to continue the multi‑aspect analysis chain. This will allow the ReviewAnalysisAgent \n"
        "to perform its analysis next.\n"
        "When the user’s intent is unclear, ask a clarifying question before proceeding. Always provide clear, "
        "concise recommendations and never take action without explicit user approval."
    ),
    tools=[fetch_booking_data, apply_discount],
)




