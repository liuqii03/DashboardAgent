# UI Integration Guide

## Overview

This document explains how to integrate the Dashboard Agent with your frontend UI.

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                        FRONTEND UI                          │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐         │
│  │   Pricing   │  │   Market    │  │   Review    │         │
│  │  Analysis   │  │   Trend     │  │  Highlight  │         │
│  │    Card     │  │    Card     │  │    Card     │         │
│  └──────┬──────┘  └──────┬──────┘  └──────┬──────┘         │
│         │                │                │                 │
│         │ Click          │ Click          │ Click           │
└─────────┼────────────────┼────────────────┼─────────────────┘
          │                │                │
          ▼                ▼                ▼
┌─────────────────────────────────────────────────────────────┐
│                     REST API (Port 8001)                    │
│  POST /pricing/analyze   POST /market/analyze               │
│  POST /pricing/apply     POST /review/analyze               │
└─────────────────────────────────────────────────────────────┘
          │                │                │
          ▼                ▼                ▼
┌─────────────────────────────────────────────────────────────┐
│                      AGENT SERVICE                          │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐         │
│  │  Pricing    │  │   Demand    │  │   Review    │         │
│  │   Agent     │  │   Agent     │  │   Agent     │         │
│  └─────────────┘  └─────────────┘  └─────────────┘         │
└─────────────────────────────────────────────────────────────┘
          │                │                │
          ▼                ▼                ▼
┌─────────────────────────────────────────────────────────────┐
│              iShare API (localhost:3000)                    │
│         /listings  /bookings  /reviews  /users              │
└─────────────────────────────────────────────────────────────┘
```

## API Endpoints

### 1. Pricing Analysis Card

**When user clicks the Pricing Analysis card:**

```http
POST /pricing/analyze
Content-Type: application/json

{
  "listing_id": "fdc645fe-c17a-48c6-9ad5-44a908238694"
}
```

**Response:**
```json
{
  "success": true,
  "action_code": "PRICING_ANALYZE",
  "agent": "PricingAgent",
  "data": {
    "title": "Pricing Analysis for 'Chill Condo Room'",
    "current_price": 100.0,
    "suggested_price": 110.0,
    "price_difference": 10.0,
    "adjustment_percent": 10.0,
    "adjustment_direction": "increase",
    "demand_level": "High",
    "reasons": [
      "Demand level is High",
      "High occupancy rate (≥70%)",
      "Strong recent booking activity",
      "Current occupancy: 73%"
    ],
    "can_take_action": true
  },
  "show_action_button": true
}
```

**If `show_action_button` is true, display the "Take Action" button.**

---

### 2. Take Action (Apply Price Change)

**When user clicks "Take Action" button:**

```http
POST /pricing/apply
Content-Type: application/json

{
  "listing_id": "fdc645fe-c17a-48c6-9ad5-44a908238694",
  "new_price": 110.0
}
```

**Response:**
```json
{
  "success": true,
  "action_code": "PRICING_APPLY",
  "agent": "PricingAgent",
  "data": {
    "success": true,
    "listing_id": "fdc645fe-c17a-48c6-9ad5-44a908238694",
    "listing_title": "Chill Condo Room",
    "old_price": 100.0,
    "new_price": 110.0,
    "message": "✅ Price updated successfully from RM 100.00 to RM 110.00"
  },
  "show_action_button": false
}
```

---

### 3. Market Trend Analysis Card

**When user clicks the Market Trend Analysis card:**

```http
POST /market/analyze
Content-Type: application/json

{
  "owner_id": 1
}
```

**Response:**
```json
{
  "success": true,
  "action_code": "MARKET_ANALYZE",
  "agent": "DemandTrendAgent",
  "data": {
    "title": "Market Trend Analysis",
    "portfolio": {
      "total_listings": 6,
      "types": ["ACCOMMODATION", "TRANSPORT", "ITEM"],
      "total_bookings": 10,
      "total_revenue": 3300.0
    },
    "trending_types": [
      {"type": "ACCOMMODATION", "listing_count": 5, "trend_score": 10.6},
      {"type": "ITEM", "listing_count": 2, "trend_score": 0.0},
      {"type": "TRANSPORT", "listing_count": 3, "trend_score": 0.0}
    ],
    "recommendations": [
      {
        "type": "ACCOMMODATION",
        "status": "on_track",
        "message": "Excellent! Your 3 ACCOMMODATION listing(s) are performing well.",
        "advice": "Keep maintaining quality and competitive pricing."
      }
    ],
    "message": "Market trend analysis complete."
  },
  "show_action_button": false
}
```

---

### 4. Review Highlight Card

**When user clicks the Review Highlight card:**

```http
POST /review/analyze
Content-Type: application/json

{
  "listing_id": "fdc645fe-c17a-48c6-9ad5-44a908238694"
}
```

**Response:**
```json
{
  "success": true,
  "action_code": "REVIEW_ANALYZE",
  "agent": "ReviewAnalysisAgent",
  "data": {
    "title": "Review Analysis",
    "overall_satisfaction": "Good",
    "average_rating": 4.2,
    "total_reviews": 10,
    "rating_distribution": {
      "5_star": 5,
      "4_star": 3,
      "3_star": 1,
      "2_star": 1,
      "1_star": 0
    },
    "sentiment_analysis": {
      "positive_percent": 80,
      "neutral_percent": 10,
      "negative_percent": 10
    },
    "recurring_themes": ["cleanliness", "location", "value"],
    "recommendations": [
      "Address cleanliness concerns mentioned in reviews",
      "Highlight location advantages in listing"
    ],
    "summary": "Overall positive reviews with minor improvement areas."
  },
  "show_action_button": false
}
```

---

## Action Codes Reference

| Action Code | Endpoint | Agent | Description |
|-------------|----------|-------|-------------|
| `PRICING_ANALYZE` | POST /pricing/analyze | PricingAgent | Analyze pricing and get recommendations |
| `PRICING_APPLY` | POST /pricing/apply | PricingAgent | Apply price change to database |
| `MARKET_ANALYZE` | POST /market/analyze | DemandTrendAgent | Analyze market trends |
| `REVIEW_ANALYZE` | POST /review/analyze | ReviewAnalysisAgent | Analyze reviews |

---

## Frontend Implementation Example (React)

```jsx
// Pricing Card Component
const PricingCard = ({ listingId }) => {
  const [analysis, setAnalysis] = useState(null);
  const [loading, setLoading] = useState(false);

  const handleCardClick = async () => {
    setLoading(true);
    const response = await fetch('http://localhost:8001/pricing/analyze', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ listing_id: listingId })
    });
    const data = await response.json();
    setAnalysis(data);
    setLoading(false);
  };

  const handleTakeAction = async () => {
    const response = await fetch('http://localhost:8001/pricing/apply', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        listing_id: listingId,
        new_price: analysis.data.suggested_price
      })
    });
    const result = await response.json();
    alert(result.data.message);
  };

  return (
    <div className="card" onClick={handleCardClick}>
      <h3>Pricing Analysis</h3>
      {analysis && (
        <>
          <p>Current: RM {analysis.data.current_price}</p>
          <p>Suggested: RM {analysis.data.suggested_price}</p>
          {analysis.show_action_button && (
            <button onClick={handleTakeAction}>Take Action</button>
          )}
        </>
      )}
    </div>
  );
};
```

---

## Running the API Server

```bash
cd /Users/liuqi/PycharmProjects/DashboardAgent
source .venv/bin/activate
uvicorn my_agent2.api.endpoints:app --reload --port 8001
```

API will be available at: `http://localhost:8001`

Swagger docs: `http://localhost:8001/docs`
