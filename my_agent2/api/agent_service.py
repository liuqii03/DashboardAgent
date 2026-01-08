"""
API service for handling UI card actions and routing to appropriate agents.

This module provides the interface between the frontend UI and the agent system.
It handles action codes from card clicks and routes them to the correct sub-agent.
"""

from typing import Dict, Any, Optional
from dataclasses import dataclass

from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.genai import types

from .action_codes import ActionCode, get_action_config, get_target_agent
from ..agent import root_agent


# Initialize session service and runner
session_service = InMemorySessionService()

runner = Runner(
    agent=root_agent,
    app_name="iShare_Dashboard",
    session_service=session_service,
)


@dataclass
class CardActionRequest:
    """
    Request model for card action.
    
    Attributes:
        action_code: The action code from the UI card (e.g., "DEMAND_001")
        listing_id: The listing ID this action relates to
        user_id: The user making the request
        additional_context: Optional dict with extra context (e.g., car_name, percentages)
    """
    action_code: str
    listing_id: str
    user_id: str = "default_user"
    additional_context: Optional[Dict[str, Any]] = None


@dataclass
class CardActionResponse:
    """
    Response model for card action.
    
    Attributes:
        success: Whether the action was processed successfully
        agent_response: The text response from the agent
        target_agent: Which agent handled the request
        action_code: The action code that was processed
        session_id: Session ID for follow-up conversations
    """
    success: bool
    agent_response: str
    target_agent: str
    action_code: str
    session_id: str
    error: Optional[str] = None


async def process_card_action(request: CardActionRequest) -> CardActionResponse:
    """
    Process a card action from the UI.
    
    This function:
    1. Looks up the action code configuration
    2. Builds the appropriate prompt with context
    3. Routes to the correct sub-agent via the root agent
    4. Returns the agent's response
    
    :param request: CardActionRequest with action details
    :return: CardActionResponse with agent's response
    """
    try:
        # Get action configuration
        config = get_action_config(request.action_code)
        
        if not config:
            return CardActionResponse(
                success=False,
                agent_response="",
                target_agent="",
                action_code=request.action_code,
                session_id="",
                error=f"Unknown action code: {request.action_code}"
            )
        
        target_agent = config["agent"]
        
        # Build the prompt with context
        context_data = {
            "listing_id": request.listing_id,
            **(request.additional_context or {})
        }
        
        # Format the context template if all required fields are present
        try:
            context_message = config["context_template"].format(**context_data)
        except KeyError:
            context_message = f"Analyzing listing {request.listing_id}"
        
        # Build the full prompt that routes to the specific agent
        prompt = f"""
[ACTION CODE: {request.action_code}]
[TARGET AGENT: {target_agent}]
[LISTING ID: {request.listing_id}]

Context: {context_message}

User request: {config["default_prompt"]}

Please route this directly to {target_agent} for listing {request.listing_id}.
"""
        
        # Create or get session
        session_id = f"session_{request.user_id}_{request.listing_id}"
        session = await session_service.get_session(
            app_name="iShare_Dashboard",
            user_id=request.user_id,
            session_id=session_id
        )
        
        if session is None:
            session = await session_service.create_session(
                app_name="iShare_Dashboard",
                user_id=request.user_id,
                session_id=session_id
            )
        
        # Run the agent
        content = types.Content(
            role="user",
            parts=[types.Part.from_text(text=prompt)]
        )
        
        response_text = ""
        async for event in runner.run_async(
            user_id=request.user_id,
            session_id=session_id,
            new_message=content
        ):
            if hasattr(event, 'content') and event.content:
                if hasattr(event.content, 'parts'):
                    for part in event.content.parts:
                        if hasattr(part, 'text') and part.text:
                            response_text += part.text
        
        return CardActionResponse(
            success=True,
            agent_response=response_text,
            target_agent=target_agent,
            action_code=request.action_code,
            session_id=session_id
        )
        
    except Exception as e:
        return CardActionResponse(
            success=False,
            agent_response="",
            target_agent="",
            action_code=request.action_code,
            session_id="",
            error=str(e)
        )


def build_direct_agent_prompt(action_code: str, listing_id: str, **context) -> Dict[str, Any]:
    """
    Build a prompt structure for direct agent invocation.
    
    This is useful when you want to get the prompt details without 
    actually calling the agent (e.g., for frontend preview).
    
    :param action_code: The action code
    :param listing_id: The listing ID
    :param context: Additional context parameters
    :return: Dictionary with prompt details
    """
    config = get_action_config(action_code)
    
    if not config:
        return {"error": f"Unknown action code: {action_code}"}
    
    context_data = {"listing_id": listing_id, **context}
    
    try:
        context_message = config["context_template"].format(**context_data)
    except KeyError:
        context_message = f"Analyzing listing {listing_id}"
    
    return {
        "action_code": action_code,
        "target_agent": config["agent"],
        "prompt": config["default_prompt"],
        "context": context_message,
        "card_type": config["card_type"],
        "description": config["action_description"],
        "listing_id": listing_id
    }
