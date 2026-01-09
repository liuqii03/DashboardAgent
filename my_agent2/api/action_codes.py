"""
Action codes for UI integration.

Flow:
1. Dashboard shows 3 insight cards (Pricing, Market Trend, Review)
2. User clicks on a card → sends action code to backend
3. Backend routes to appropriate agent and returns JSON response
4. For Pricing Agent: If price change suggested, "Take Action" button appears
5. User clicks "Take Action" → sends PRICING_APPLY action code
6. Agent updates database with new price

Agents:
- PricingAgent: Dynamic pricing with "Take Action" capability
- DemandTrendAgent: Market trends and recommendations (read-only)
- ReviewAnalysisAgent: Review analysis and highlights (read-only)
"""

from enum import Enum
from typing import Dict, Any


class ActionCode(str, Enum):
    """
    Predefined action codes for each insight card type.
    These codes are sent from the UI when user interacts with cards.
    """
    # ============ PRICING CARD ============
    # Triggered when user clicks the Pricing Analysis card
    PRICING_ANALYZE = "PRICING_ANALYZE"
    
    # Triggered when user clicks "Take Action" button after seeing price recommendation
    PRICING_APPLY = "PRICING_APPLY"
    
    # ============ MARKET TREND CARD ============
    # Triggered when user clicks the Market Trend Analysis card
    MARKET_ANALYZE = "MARKET_ANALYZE"
    
    # ============ REVIEW CARD ============
    # Triggered when user clicks the Review Highlight card
    REVIEW_ANALYZE = "REVIEW_ANALYZE"


# Configuration for each action code
ACTION_CODE_CONFIG: Dict[str, Dict[str, Any]] = {
    
    # ========== PRICING AGENT ==========
    ActionCode.PRICING_ANALYZE: {
        "agent": "PricingAgent",
        "tool": "analyze_pricing",
        "description": "Analyze demand and get pricing recommendations",
        "required_params": ["listing_id"],
        "has_action_button": True,  # Shows "Take Action" if price change recommended
        "card_type": "pricing"
    },
    
    ActionCode.PRICING_APPLY: {
        "agent": "PricingAgent",
        "tool": "apply_price_change",
        "description": "Apply the suggested price change to database",
        "required_params": ["listing_id", "new_price"],
        "has_action_button": False,
        "card_type": "pricing",
        "is_write_action": True  # This action modifies database
    },
    
    # ========== DEMAND TREND AGENT ==========
    ActionCode.MARKET_ANALYZE: {
        "agent": "DemandTrendAgent",
        "tool": "analyze_market_trends",
        "description": "Analyze market trends and get recommendations",
        "required_params": ["owner_id"],
        "has_action_button": False,  # Read-only
        "card_type": "demand"
    },
    
    # ========== REVIEW AGENT ==========
    ActionCode.REVIEW_ANALYZE: {
        "agent": "ReviewAnalysisAgent",
        "tool": "analyze_reviews",
        "description": "Analyze reviews and get highlights",
        "required_params": ["listing_id"],
        "has_action_button": False,  # Read-only
        "card_type": "review"
    },
}


def get_action_config(action_code: str) -> Dict[str, Any]:
    """
    Get the configuration for a specific action code.
    
    :param action_code: The action code string (e.g., "PRICING_ANALYZE")
    :return: Configuration dictionary
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
    return config.get("agent", "")


def get_required_params(action_code: str) -> list:
    """
    Get required parameters for an action code.
    
    :param action_code: The action code string
    :return: List of required parameter names
    """
    config = get_action_config(action_code)
    return config.get("required_params", [])


def has_action_button(action_code: str) -> bool:
    """
    Check if this action code can trigger a "Take Action" button.
    
    :param action_code: The action code string
    :return: True if action button should be shown
    """
    config = get_action_config(action_code)
    return config.get("has_action_button", False)


def is_write_action(action_code: str) -> bool:
    """
    Check if this action modifies the database.
    
    :param action_code: The action code string
    :return: True if this action writes to database
    """
    config = get_action_config(action_code)
    return config.get("is_write_action", False)
