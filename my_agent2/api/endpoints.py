"""
FastAPI endpoints for the Dashboard Agent.

This module provides REST API endpoints for the UI to interact with the agent system.
"""

import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, Dict, Any

from .action_codes import ActionCode, ACTION_CODE_CONFIG
from .agent_service import (
    CardActionRequest,
    process_card_action,
    build_direct_agent_prompt
)


app = FastAPI(
    title="iShare Dashboard Agent API",
    description="API for integrating the dashboard agent with the UI",
    version="1.0.0"
)

# Enable CORS for frontend integration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Pydantic models for API requests/responses
class CardActionRequestModel(BaseModel):
    """Request model for card action endpoint."""
    action_code: str
    listing_id: str
    user_id: str = "default_user"
    additional_context: Optional[Dict[str, Any]] = None
    
    class Config:
        json_schema_extra = {
            "example": {
                "action_code": "DEMAND_001",
                "listing_id": "veh001",
                "user_id": "user_123",
                "additional_context": {
                    "car_name": "Honda City 2020",
                    "demand_percent": 20
                }
            }
        }


class CardActionResponseModel(BaseModel):
    """Response model for card action endpoint."""
    success: bool
    agent_response: str
    target_agent: str
    action_code: str
    session_id: str
    error: Optional[str] = None


class ActionCodeInfo(BaseModel):
    """Information about an action code."""
    code: str
    agent: str
    card_type: str
    description: str
    default_prompt: str


# API Endpoints

@app.get("/")
async def root():
    """Health check endpoint."""
    return {"status": "ok", "service": "iShare Dashboard Agent API"}


@app.get("/action-codes", response_model=Dict[str, ActionCodeInfo])
async def get_action_codes():
    """
    Get all available action codes.
    
    Returns a dictionary of all action codes that can be used
    to trigger specific agent actions from UI cards.
    """
    result = {}
    for code in ActionCode:
        config = ACTION_CODE_CONFIG.get(code, {})
        result[code.value] = ActionCodeInfo(
            code=code.value,
            agent=config.get("agent", ""),
            card_type=config.get("card_type", ""),
            description=config.get("action_description", ""),
            default_prompt=config.get("default_prompt", "")
        )
    return result


@app.post("/card-action", response_model=CardActionResponseModel)
async def handle_card_action(request: CardActionRequestModel):
    """
    Handle a card action from the UI.
    
    This endpoint is called when a user clicks "Take Action" on an insight card.
    It routes the request to the appropriate sub-agent based on the action code.
    
    **Action Codes:**
    - `DEMAND_001`: High Demand Alert - triggers DemandPricingAgent
    - `DEMAND_002`: Demand Prediction - triggers DemandPricingAgent
    - `BOOKING_001`: Booking Duration Trend - triggers BookingTrendAgent
    - `BOOKING_002`: Booking Discount - triggers BookingTrendAgent
    - `REVIEW_001`: Review Highlight - triggers ReviewAnalysisAgent
    - `REVIEW_002`: Review Flag Issue - triggers ReviewAnalysisAgent
    """
    card_request = CardActionRequest(
        action_code=request.action_code,
        listing_id=request.listing_id,
        user_id=request.user_id,
        additional_context=request.additional_context
    )
    
    response = await process_card_action(card_request)
    
    return CardActionResponseModel(
        success=response.success,
        agent_response=response.agent_response,
        target_agent=response.target_agent,
        action_code=response.action_code,
        session_id=response.session_id,
        error=response.error
    )


@app.get("/preview-action/{action_code}")
async def preview_action(action_code: str, listing_id: str):
    """
    Preview what an action will do without executing it.
    
    Useful for showing users what will happen when they click a button.
    """
    result = build_direct_agent_prompt(action_code, listing_id)
    
    if "error" in result:
        raise HTTPException(status_code=400, detail=result["error"])
    
    return result


@app.post("/chat")
async def chat_with_agent(
    message: str,
    user_id: str = "default_user",
    listing_id: Optional[str] = None
):
    """
    General chat endpoint for free-form conversation with the agent.
    
    This endpoint allows users to have a natural conversation with the agent
    without using predefined action codes.
    """
    from google.adk.runners import Runner
    from google.adk.sessions import InMemorySessionService
    from google.genai import types
    from ..agent import root_agent
    
    session_service = InMemorySessionService()
    runner = Runner(
        agent=root_agent,
        app_name="iShare_Dashboard",
        session_service=session_service,
    )
    
    session_id = f"chat_{user_id}"
    if listing_id:
        session_id = f"chat_{user_id}_{listing_id}"
    
    session = await session_service.get_session(
        app_name="iShare_Dashboard",
        user_id=user_id,
        session_id=session_id
    )
    
    if session is None:
        session = await session_service.create_session(
            app_name="iShare_Dashboard",
            user_id=user_id,
            session_id=session_id
        )
    
    content = types.Content(
        role="user",
        parts=[types.Part.from_text(text=message)]
    )
    
    response_text = ""
    async for event in runner.run_async(
        user_id=user_id,
        session_id=session_id,
        new_message=content
    ):
        if hasattr(event, 'content') and event.content:
            if hasattr(event.content, 'parts'):
                for part in event.content.parts:
                    if hasattr(part, 'text') and part.text:
                        response_text += part.text
    
    return {
        "response": response_text,
        "session_id": session_id
    }


# Run with: uvicorn my_agent2.api.endpoints:app --reload
