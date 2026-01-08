# UI Integration Guide for Dashboard Agent

## Overview

This guide explains how to integrate the Dashboard Agent with your UI. Each insight card maps to a specific **action code** that routes to the appropriate sub-agent.

## Action Code Mapping

| Card Type | Action Code | Target Agent | Description |
|-----------|-------------|--------------|-------------|
| High Demand Alert | `DEMAND_001` | DemandPricingAgent | Analyze demand and suggest price optimization |
| Demand Prediction | `DEMAND_002` | DemandPricingAgent | Get demand prediction for listing |
| Booking Duration Trend | `BOOKING_001` | BookingTrendAgent | Analyze booking trends and discount options |
| Booking Discount | `BOOKING_002` | BookingTrendAgent | Apply longer-term discount |
| Review Highlight | `REVIEW_001` | ReviewAnalysisAgent | Analyze review sentiment and themes |
| Review Flag Issue | `REVIEW_002` | ReviewAnalysisAgent | Flag and analyze review issues |

## API Endpoints

### 1. Handle Card Action (Main endpoint)

```
POST /card-action
```

**Request Body:**
```json
{
  "action_code": "DEMAND_001",
  "listing_id": "veh001",
  "user_id": "user_123",
  "additional_context": {
    "car_name": "Honda City 2020",
    "demand_percent": 20
  }
}
```

**Response:**
```json
{
  "success": true,
  "agent_response": "Based on the analysis, your Honda City 2020 has high demand...",
  "target_agent": "DemandPricingAgent",
  "action_code": "DEMAND_001",
  "session_id": "session_user_123_veh001"
}
```

### 2. Get All Action Codes

```
GET /action-codes
```

Returns all available action codes for UI reference.

### 3. Preview Action

```
GET /preview-action/{action_code}?listing_id=veh001
```

Preview what an action will do without executing it.

### 4. General Chat

```
POST /chat?message=What's my demand?&user_id=user_123&listing_id=veh001
```

Free-form conversation with the agent.

## Frontend Integration Examples

### React/TypeScript Example

```typescript
// types.ts
interface CardActionRequest {
  action_code: string;
  listing_id: string;
  user_id: string;
  additional_context?: Record<string, any>;
}

interface CardActionResponse {
  success: boolean;
  agent_response: string;
  target_agent: string;
  action_code: string;
  session_id: string;
  error?: string;
}

// Action codes enum
export const ActionCodes = {
  DEMAND_HIGH_ALERT: 'DEMAND_001',
  DEMAND_PREDICTION: 'DEMAND_002',
  BOOKING_DURATION_TREND: 'BOOKING_001',
  BOOKING_DISCOUNT: 'BOOKING_002',
  REVIEW_HIGHLIGHT: 'REVIEW_001',
  REVIEW_FLAG_ISSUE: 'REVIEW_002',
} as const;

// api.ts
const API_BASE_URL = 'http://localhost:8000';

export async function handleCardAction(request: CardActionRequest): Promise<CardActionResponse> {
  const response = await fetch(`${API_BASE_URL}/card-action`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify(request),
  });
  return response.json();
}

// InsightCard.tsx
import React, { useState } from 'react';
import { handleCardAction } from './api';
import { ActionCodes } from './types';

interface InsightCardProps {
  type: 'demand' | 'booking' | 'review';
  title: string;
  description: string;
  listingId: string;
  userId: string;
  additionalContext?: Record<string, any>;
}

const actionCodeMap = {
  demand: ActionCodes.DEMAND_HIGH_ALERT,
  booking: ActionCodes.BOOKING_DURATION_TREND,
  review: ActionCodes.REVIEW_HIGHLIGHT,
};

export function InsightCard({ 
  type, 
  title, 
  description, 
  listingId, 
  userId,
  additionalContext 
}: InsightCardProps) {
  const [isLoading, setIsLoading] = useState(false);
  const [agentResponse, setAgentResponse] = useState<string | null>(null);

  const handleTakeAction = async () => {
    setIsLoading(true);
    try {
      const response = await handleCardAction({
        action_code: actionCodeMap[type],
        listing_id: listingId,
        user_id: userId,
        additional_context: additionalContext,
      });
      
      if (response.success) {
        setAgentResponse(response.agent_response);
        // Optionally open a chat modal or navigate to chat view
      } else {
        console.error('Action failed:', response.error);
      }
    } catch (error) {
      console.error('Error handling action:', error);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="insight-card">
      <div className="card-icon">{/* Icon based on type */}</div>
      <h3>{title}</h3>
      <p>{description}</p>
      <button 
        onClick={handleTakeAction} 
        disabled={isLoading}
        className="take-action-btn"
      >
        {isLoading ? 'Processing...' : 'Take Action'}
      </button>
      {agentResponse && (
        <div className="agent-response">
          <p>{agentResponse}</p>
        </div>
      )}
    </div>
  );
}

// Usage in your dashboard
function ActionableInsights({ listingId, userId }: { listingId: string; userId: string }) {
  return (
    <div className="actionable-insights">
      <h2>Actionable Insights</h2>
      
      <InsightCard
        type="demand"
        title="High Demand Alert"
        description="Your car 'Honda City 2020' has 20% higher demand next week. Consider adjusting price to maximize earnings."
        listingId={listingId}
        userId={userId}
        additionalContext={{
          car_name: "Honda City 2020",
          demand_percent: 20
        }}
      />
      
      <InsightCard
        type="booking"
        title="Booking Duration Trend"
        description="Average booking duration increased by 18%. Offer longer-term discounts to attract extended rentals."
        listingId={listingId}
        userId={userId}
        additionalContext={{
          increase_percent: 18
        }}
      />
      
      <InsightCard
        type="review"
        title="Review Highlight"
        description="Users often mention 'cleanliness' in your reviews — you're performing well in that area. Keep it up!"
        listingId={listingId}
        userId={userId}
        additionalContext={{
          highlight_theme: "cleanliness"
        }}
      />
    </div>
  );
}
```

### Flutter/Dart Example

```dart
// action_codes.dart
class ActionCodes {
  static const String demandHighAlert = 'DEMAND_001';
  static const String demandPrediction = 'DEMAND_002';
  static const String bookingDurationTrend = 'BOOKING_001';
  static const String bookingDiscount = 'BOOKING_002';
  static const String reviewHighlight = 'REVIEW_001';
  static const String reviewFlagIssue = 'REVIEW_002';
}

// agent_service.dart
import 'dart:convert';
import 'package:http/http.dart' as http;

class AgentService {
  final String baseUrl;
  
  AgentService({this.baseUrl = 'http://localhost:8000'});
  
  Future<CardActionResponse> handleCardAction(CardActionRequest request) async {
    final response = await http.post(
      Uri.parse('$baseUrl/card-action'),
      headers: {'Content-Type': 'application/json'},
      body: jsonEncode(request.toJson()),
    );
    return CardActionResponse.fromJson(jsonDecode(response.body));
  }
}

class CardActionRequest {
  final String actionCode;
  final String listingId;
  final String userId;
  final Map<String, dynamic>? additionalContext;
  
  CardActionRequest({
    required this.actionCode,
    required this.listingId,
    required this.userId,
    this.additionalContext,
  });
  
  Map<String, dynamic> toJson() => {
    'action_code': actionCode,
    'listing_id': listingId,
    'user_id': userId,
    'additional_context': additionalContext,
  };
}

class CardActionResponse {
  final bool success;
  final String agentResponse;
  final String targetAgent;
  final String actionCode;
  final String sessionId;
  final String? error;
  
  CardActionResponse.fromJson(Map<String, dynamic> json)
    : success = json['success'],
      agentResponse = json['agent_response'],
      targetAgent = json['target_agent'],
      actionCode = json['action_code'],
      sessionId = json['session_id'],
      error = json['error'];
}
```

## Running the API Server

```bash
# Install dependencies
pip install fastapi uvicorn

# Run the server
uvicorn my_agent2.api.endpoints:app --reload --port 8000
```

## Flow Diagram

```
┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
│   UI Card       │     │   API Endpoint  │     │   Root Agent    │
│  (Take Action)  │────▶│  /card-action   │────▶│                 │
└─────────────────┘     └─────────────────┘     └────────┬────────┘
                                                         │
                              ┌───────────────────────────┼───────────────────────────┐
                              │                           │                           │
                              ▼                           ▼                           ▼
                   ┌─────────────────┐         ┌─────────────────┐         ┌─────────────────┐
                   │ DemandPricing   │         │ BookingTrend    │         │ ReviewAnalysis  │
                   │ Agent           │         │ Agent           │         │ Agent           │
                   │ (DEMAND_001/2)  │         │ (BOOKING_001/2) │         │ (REVIEW_001/2)  │
                   └─────────────────┘         └─────────────────┘         └─────────────────┘
```

## Session Management

The API maintains sessions per user and listing combination. This allows for:
- Continuous conversations after initial card click
- Context preservation across multiple interactions
- Follow-up questions without re-specifying the listing

Session ID format: `session_{user_id}_{listing_id}`
