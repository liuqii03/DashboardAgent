"""
API module for the Dashboard Agent.

This module provides REST API endpoints and action code mappings
for integrating the agent system with frontend UI components.
"""

from .action_codes import ActionCode, get_action_config, get_target_agent
from .agent_service import (
    CardActionRequest,
    CardActionResponse,
    process_card_action,
    build_direct_agent_prompt
)
from .endpoints import app

__all__ = [
    "ActionCode",
    "get_action_config",
    "get_target_agent",
    "CardActionRequest",
    "CardActionResponse",
    "process_card_action",
    "build_direct_agent_prompt",
    "app"
]
