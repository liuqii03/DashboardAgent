"""
FastAPI endpoints for the Dashboard Agent.

This module provides REST API endpoints for the UI to interact with the agent system.

Endpoints:
- POST /pricing/analyze - Analyze pricing for a listing
- POST /pricing/apply - Apply price change (Take Action)
- POST /market/analyze - Analyze market trends for an owner
- POST /review/analyze - Analyze reviews for a listing
"""

import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, Dict, Any, List

from .action_codes import ActionCode, ACTION_CODE_CONFIG
from .agent_service import (
    CardActionRequest,
    CardActionResponse,
    process_card_action,
    response_to_dict
)


app = FastAPI(
    title="iShare Dashboard Agent API",
    description="API for integrating the dashboard agent with the UI",
    version="2.0.0"
)

# Enable CORS for frontend integration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ============ Request Models ============

class PricingAnalyzeRequest(BaseModel):
    """Request to analyze pricing for a listing."""
    listing_id: str
    
    class Config:
        json_schema_extra = {
            "example": {
                "listing_id": "fdc645fe-c17a-48c6-9ad5-44a908238694"
            }
        }


class PricingApplyRequest(BaseModel):
    """Request to apply price change."""
    listing_id: str
    new_price: float
    
    class Config:
        json_schema_extra = {
            "example": {
                "listing_id": "fdc645fe-c17a-48c6-9ad5-44a908238694",
                "new_price": 110.00
            }
        }


class MarketAnalyzeRequest(BaseModel):
    """Request to analyze market trends for an owner."""
    owner_id: int
    
    class Config:
        json_schema_extra = {
            "example": {
                "owner_id": 1
            }
        }


class ReviewAnalyzeRequest(BaseModel):
    """Request to analyze reviews for a listing."""
    listing_id: str
    
    class Config:
        json_schema_extra = {
            "example": {
                "listing_id": "fdc645fe-c17a-48c6-9ad5-44a908238694"
            }
        }


# ============ Response Models ============

class APIResponse(BaseModel):
    """Standard API response."""
    success: bool
    action_code: str
    agent: str
    data: Dict[str, Any]
    show_action_button: bool = False
    error: Optional[str] = None


# ============ API Endpoints ============

@app.get("/")
def root():
    """Health check endpoint."""
    return {"status": "ok", "service": "iShare Dashboard Agent API", "version": "2.0.0"}


@app.get("/action-codes")
def get_action_codes():
    """
    Get all available action codes and their configurations.
    """
    result = {}
    for code in ActionCode:
        config = ACTION_CODE_CONFIG.get(code, {})
        result[code.value] = {
            "code": code.value,
            "agent": config.get("agent", ""),
            "tool": config.get("tool", ""),
            "description": config.get("description", ""),
            "required_params": config.get("required_params", []),
            "has_action_button": config.get("has_action_button", False),
            "card_type": config.get("card_type", "")
        }
    return result


# ============ PRICING ENDPOINTS ============

@app.post("/pricing/analyze", response_model=APIResponse)
def analyze_pricing(request: PricingAnalyzeRequest):
    """
    Analyze pricing for a listing and get recommendations.
    
    This is triggered when user clicks the "Pricing Analysis" card.
    
    Returns:
    - current_price: Current listing price
    - suggested_price: Recommended price
    - adjustment_percent: Percentage change
    - demand_level: High/Medium/Low
    - reasons: Why this price is recommended
    - can_take_action: Whether price change is recommended
    
    If can_take_action is True, show the "Take Action" button.
    """
    card_request = CardActionRequest(
        action_code=ActionCode.PRICING_ANALYZE.value,
        listing_id=request.listing_id
    )
    
    response = process_card_action(card_request)
    return response_to_dict(response)


@app.post("/pricing/apply", response_model=APIResponse)
def apply_pricing(request: PricingApplyRequest):
    """
    Apply the suggested price change to the database.
    
    This is triggered when user clicks the "Take Action" button.
    
    Returns:
    - success: Whether the price was updated
    - old_price: Previous price
    - new_price: New price
    - message: Confirmation message
    """
    card_request = CardActionRequest(
        action_code=ActionCode.PRICING_APPLY.value,
        listing_id=request.listing_id,
        new_price=request.new_price
    )
    
    response = process_card_action(card_request)
    return response_to_dict(response)


# ============ MARKET TREND ENDPOINTS ============

@app.post("/market/analyze", response_model=APIResponse)
def analyze_market(request: MarketAnalyzeRequest):
    """
    Analyze market trends for an owner.
    
    This is triggered when user clicks the "Market Trend Analysis" card.
    
    Returns:
    - portfolio: Owner's current portfolio summary
    - trending_types: Top trending listing types in market
    - recommendations: Priority recommendations for the owner
    """
    card_request = CardActionRequest(
        action_code=ActionCode.MARKET_ANALYZE.value,
        owner_id=request.owner_id
    )
    
    response = process_card_action(card_request)
    return response_to_dict(response)


# ============ REVIEW ENDPOINTS ============

@app.post("/review/analyze", response_model=APIResponse)
def analyze_reviews(request: ReviewAnalyzeRequest):
    """
    Analyze reviews for a listing.
    
    This is triggered when user clicks the "Review Highlight" card.
    
    Returns:
    - overall_satisfaction: Satisfaction level
    - rating_distribution: Breakdown of ratings
    - sentiment_analysis: Positive/negative sentiment
    - recurring_themes: Common topics in reviews
    - recommendations: Suggestions for improvement
    """
    card_request = CardActionRequest(
        action_code=ActionCode.REVIEW_ANALYZE.value,
        listing_id=request.listing_id
    )
    
    response = process_card_action(card_request)
    return response_to_dict(response)


# Run with: uvicorn my_agent2.api.endpoints:app --reload --port 8001
