"""
Action codes for UI integration.

Each card in the UI has a specific action code that maps to a sub-agent.
When a user clicks on a card, the frontend sends the action code
to the backend, which routes it to the appropriate agent.

Agents:
- ReviewAnalysisAgent: Analyzes reviews (read-only, no actions)
- PricingAgent: Dynamic pricing with "Take Action" capability
- DemandTrendAgent: Market trends and suggestions (read-only)
"""

from enum import Enum
from typing import Dict, Any


class ActionCode(str, Enum):
    """
    Predefined action codes for each insight card type.
    These codes are sent from the UI when user interacts with cards.
    """
    # Pricing-related actions (HAS TAKE ACTION BUTTON)
    PRICING_ANALYSIS = "PRICING_001"          # Analyze pricing and get recommendations
    PRICING_APPLY = "PRICING_002"             # Apply suggested price change
    
    # Demand/Market trend actions (READ-ONLY)
    DEMAND_TRENDS = "DEMAND_001"              # View market trends
    DEMAND_SUGGESTIONS = "DEMAND_002"         # Get suggestions for new listings
    
    # Review-related actions (READ-ONLY)
    REVIEW_ANALYSIS = "REVIEW_001"            # Review analysis and sentiment
    REVIEW_SUMMARY = "REVIEW_002"             # Get review summary


# Map action codes to their target agent and default context
ACTION_CODE_CONFIG: Dict[str, Dict[str, Any]] = {
    # PRICING AGENT - Has "Take Action" capability
    ActionCode.PRICING_ANALYSIS: {
        "agent": "PricingAgent",
        "default_prompt": "Analyze the pricing for my listing and suggest adjustments based on demand.",
        "context_template": "Pricing analysis for {listing_title} ({listing_id}). Current price: ${current_price}.",
        "card_type": "pricing",
        "action_description": "Analyze demand and get pricing recommendations",
        "has_action_button": True
    },
    ActionCode.PRICING_APPLY: {
        "agent": "PricingAgent",
        "default_prompt": "Apply the suggested price change to my listing.",
        "context_template": "Applying price change for {listing_id}. New price: ${suggested_price}.",
        "card_type": "pricing",
        "action_description": "Apply the suggested price",
        "has_action_button": True,
        "is_action_call": True
    },
    
    # DEMAND TREND AGENT - Read-only
    ActionCode.DEMAND_TRENDS: {
        "agent": "DemandTrendAgent",
        "default_prompt": "What listing types are currently trending in the market?",
        "context_template": "Analyzing market trends for owner {owner_id}.",
        "card_type": "demand",
        "action_description": "View trending listing types",
        "has_action_button": False
    },
    ActionCode.DEMAND_SUGGESTIONS: {
        "agent": "DemandTrendAgent",
        "default_prompt": "What can I rent to increase my revenue based on current market trends?",
        "context_template": "Generating suggestions for owner {owner_id} to increase revenue.",
        "card_type": "demand",
        "action_description": "Get suggestions for new listings",
        "has_action_button": False
    },
    
    # REVIEW AGENT - Read-only
    ActionCode.REVIEW_ANALYSIS: {
        "agent": "ReviewAnalysisAgent",
        "default_prompt": "Analyze the reviews for my listing and provide a summary.",
        "context_template": "Review analysis for {listing_title} ({listing_id}).",
        "card_type": "review",
        "action_description": "Analyze reviews and sentiment",
        "has_action_button": False
    },
    ActionCode.REVIEW_SUMMARY: {
        "agent": "ReviewAnalysisAgent",
        "default_prompt": "Give me a summary of customer feedback and recurring themes.",
        "context_template": "Summarizing reviews for {listing_id}.",
        "card_type": "review",
        "action_description": "Get review summary with themes",
        "has_action_button": False
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
