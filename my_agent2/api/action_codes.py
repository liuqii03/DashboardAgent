"""
Action codes for UI integration.

Each card in the UI has a specific action code that maps to a sub-agent.
When a user clicks "Take Action" on a card, the frontend sends the action code
to the backend, which routes it to the appropriate agent.
"""

from enum import Enum
from typing import Dict, Any


class ActionCode(str, Enum):
    """
    Predefined action codes for each insight card type.
    These codes are sent from the UI when user clicks "Take Action".
    """
    # Demand-related actions
    DEMAND_HIGH_ALERT = "DEMAND_001"          # High demand alert - price optimization
    DEMAND_PREDICTION = "DEMAND_002"          # Demand prediction inquiry
    
    # Booking-related actions
    BOOKING_DURATION_TREND = "BOOKING_001"    # Booking duration trend analysis
    BOOKING_DISCOUNT = "BOOKING_002"          # Apply discount for longer bookings
    
    # Review-related actions
    REVIEW_HIGHLIGHT = "REVIEW_001"           # Review highlight/sentiment
    REVIEW_FLAG_ISSUE = "REVIEW_002"          # Flag reviews with issues


# Map action codes to their target agent and default context
ACTION_CODE_CONFIG: Dict[str, Dict[str, Any]] = {
    ActionCode.DEMAND_HIGH_ALERT: {
        "agent": "DemandPricingAgent",
        "default_prompt": "I see there's high demand for my listing. Can you analyze the demand and suggest a price adjustment?",
        "context_template": "High demand detected for {car_name} ({listing_id}). Current demand is {demand_percent}% higher than usual.",
        "card_type": "demand",
        "action_description": "Analyze demand and optimize pricing"
    },
    ActionCode.DEMAND_PREDICTION: {
        "agent": "DemandPricingAgent",
        "default_prompt": "What's the demand prediction for my listing next week?",
        "context_template": "Analyzing demand prediction for {listing_id}.",
        "card_type": "demand",
        "action_description": "Get demand prediction"
    },
    ActionCode.BOOKING_DURATION_TREND: {
        "agent": "BookingTrendAgent",
        "default_prompt": "I noticed the booking duration has increased. Should I offer discounts for longer rentals?",
        "context_template": "Booking duration increased by {increase_percent}% for {listing_id}. Consider offering discounts for extended rentals.",
        "card_type": "booking",
        "action_description": "Analyze booking trends and discount options"
    },
    ActionCode.BOOKING_DISCOUNT: {
        "agent": "BookingTrendAgent",
        "default_prompt": "Apply a discount for longer bookings on my listing.",
        "context_template": "Applying discount strategy for {listing_id}.",
        "card_type": "booking",
        "action_description": "Apply longer-term discount"
    },
    ActionCode.REVIEW_HIGHLIGHT: {
        "agent": "ReviewAnalysisAgent",
        "default_prompt": "Tell me more about my review highlights and what customers are saying.",
        "context_template": "Review analysis for {listing_id}. Common positive theme: {highlight_theme}.",
        "card_type": "review",
        "action_description": "Analyze review sentiment and themes"
    },
    ActionCode.REVIEW_FLAG_ISSUE: {
        "agent": "ReviewAnalysisAgent",
        "default_prompt": "Are there any issues mentioned in my reviews that I should address?",
        "context_template": "Flagging potential issues in reviews for {listing_id}.",
        "card_type": "review",
        "action_description": "Flag and analyze review issues"
    },
}


def get_action_config(action_code: str) -> Dict[str, Any]:
    """
    Get the configuration for a specific action code.
    
    :param action_code: The action code string (e.g., "DEMAND_001")
    :return: Configuration dictionary with agent, prompt, and context info
    """
    # Handle both enum values and string values
    if isinstance(action_code, ActionCode):
        return ACTION_CODE_CONFIG.get(action_code, {})
    
    # Try to match string to enum
    for code in ActionCode:
        if code.value == action_code:
            return ACTION_CODE_CONFIG.get(code, {})
    
    return {}


def get_target_agent(action_code: str) -> str:
    """
    Get the target agent name for a specific action code.
    
    :param action_code: The action code string
    :return: Agent name string
    """
    config = get_action_config(action_code)
    return config.get("agent", "RootAgent")
