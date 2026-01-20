"""
API service for handling UI card actions and routing to appropriate agents.

This module provides the interface between the frontend UI and the agent system.
It directly calls agent tools based on action codes for fast, predictable responses.

Flow:
1. UI sends action code + parameters (listing_id, owner_id, etc.)
2. Service looks up which tool to call
3. Service calls the tool directly and returns JSON
4. For PRICING_APPLY, the tool updates the database
"""

from typing import Dict, Any, Optional
from dataclasses import dataclass, asdict
import json

from .action_codes import (
    ActionCode, 
    get_action_config, 
    get_target_agent, 
    get_required_params,
    has_action_button,
    is_write_action
)

# Import the tool functions directly
from ..sub_agents.pricing_agent import analyze_pricing, apply_price_change
from ..sub_agents.demand_agent import analyze_market_trends
from ..sub_agents.review_agent import analyze_reviews


@dataclass
class CardActionRequest:
    """
    Request model for card action.
    
    Attributes:
        action_code: The action code from the UI card (e.g., "PRICING_ANALYZE")
        listing_id: The listing ID (for pricing and review agents)
        owner_id: The owner ID (for demand agent)
        new_price: New price to apply (for PRICING_APPLY action)
    """
    action_code: str
    listing_id: Optional[str] = None
    owner_id: Optional[int] = None
    new_price: Optional[float] = None
    token_id: str = None


@dataclass 
class CardActionResponse:
    """
    Response model for card action.
    
    Attributes:
        success: Whether the action was processed successfully
        action_code: The action code that was processed
        agent: Which agent handled the request
        data: The JSON response from the agent tool
        show_action_button: Whether to show "Take Action" button
        error: Error message if failed
    """
    success: bool
    action_code: str
    agent: str
    data: Dict[str, Any]
    show_action_button: bool = False
    error: Optional[str] = None


def process_card_action(request: CardActionRequest) -> CardActionResponse:
    """
    Process a card action from the UI by directly calling the appropriate tool.
    
    This function:
    1. Looks up the action code configuration
    2. Validates required parameters
    3. Calls the appropriate tool function directly
    4. Returns the JSON response
    
    :param request: CardActionRequest with action details
    :return: CardActionResponse with tool's JSON response
    """
    try:
        # Get action configuration
        config = get_action_config(request.action_code)
        
        if not config:
            return CardActionResponse(
                success=False,
                action_code=request.action_code,
                agent="",
                data={},
                error=f"Unknown action code: {request.action_code}"
            )
        
        agent_name = config["agent"]
        tool_name = config["tool"]
        
        # Route to appropriate tool based on action code
        if request.action_code == ActionCode.PRICING_ANALYZE.value or request.action_code == ActionCode.PRICING_ANALYZE:
            # Pricing Analysis - requires listing_id
            if not request.listing_id:
                return CardActionResponse(
                    success=False,
                    action_code=request.action_code,
                    agent=agent_name,
                    data={},
                    error="listing_id is required for pricing analysis"
                )
            
            result = analyze_pricing(request.listing_id, request.token_id)
            
            # Show action button if price change is recommended
            show_button = result.get("can_take_action", False)
            
            return CardActionResponse(
                success=True,
                action_code=request.action_code,
                agent=agent_name,
                data=result,
                show_action_button=show_button
            )
        
        elif request.action_code == ActionCode.PRICING_APPLY.value or request.action_code == ActionCode.PRICING_APPLY:
            # Apply Price Change - requires listing_id and new_price
            if not request.listing_id or request.new_price is None:
                return CardActionResponse(
                    success=False,
                    action_code=request.action_code,
                    agent=agent_name,
                    data={},
                    error="listing_id and new_price are required to apply price change"
                )
            
            result = apply_price_change(request.listing_id, request.new_price, request.token_id)
            
            return CardActionResponse(
                success=result.get("success", False),
                action_code=request.action_code,
                agent=agent_name,
                data=result,
                show_action_button=False
            )
        
        elif request.action_code == ActionCode.MARKET_ANALYZE.value or request.action_code == ActionCode.MARKET_ANALYZE:
            # Market Trend Analysis - requires owner_id
            if not request.owner_id:
                return CardActionResponse(
                    success=False,
                    action_code=request.action_code,
                    agent=agent_name,
                    data={},
                    error="owner_id is required for market analysis"
                )
            
            result = analyze_market_trends(request.owner_id, request.token_id)
            
            return CardActionResponse(
                success=True,
                action_code=request.action_code,
                agent=agent_name,
                data=result,
                show_action_button=False
            )
        
        elif request.action_code == ActionCode.REVIEW_ANALYZE.value or request.action_code == ActionCode.REVIEW_ANALYZE:
            # Review Analysis - requires listing_id
            if not request.listing_id:
                return CardActionResponse(
                    success=False,
                    action_code=request.action_code,
                    agent=agent_name,
                    data={},
                    error="listing_id is required for review analysis"
                )
            
            result = analyze_reviews(request.listing_id)
            
            return CardActionResponse(
                success=True,
                action_code=request.action_code,
                agent=agent_name,
                data=result,
                show_action_button=False
            )
        
        else:
            return CardActionResponse(
                success=False,
                action_code=request.action_code,
                agent="",
                data={},
                error=f"Unhandled action code: {request.action_code}"
            )
        
    except Exception as e:
        return CardActionResponse(
            success=False,
            action_code=request.action_code,
            agent="",
            data={},
            error=str(e)
        )


def response_to_dict(response: CardActionResponse) -> Dict[str, Any]:
    """Convert CardActionResponse to dictionary for JSON serialization."""
    return asdict(response)
