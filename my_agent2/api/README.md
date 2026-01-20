# iShare Dashboard Agent API

A REST API service that provides AI-powered insights for the iShare platform dashboard.

## Overview

This API powers the dashboard cards in iShare, providing:
- **Pricing Analysis** - Dynamic pricing recommendations based on demand and occupancy
- **Market Trends** - Market-wide trend analysis with portfolio recommendations
- **Review Insights** - Sentiment analysis and actionable review summaries

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                        FRONTEND UI                          │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐         │
│  │   Pricing   │  │   Market    │  │   Review    │         │
│  │    Card     │  │   Trend     │  │  Highlight  │         │
│  └──────┬──────┘  └──────┬──────┘  └──────┬──────┘         │
└─────────┼────────────────┼────────────────┼─────────────────┘
          │                │                │
          ▼                ▼                ▼
┌─────────────────────────────────────────────────────────────┐
│              Dashboard Agent API (Port 8001)                │
│         /pricing/*    /market/*    /review/*                │
└─────────────────────────────────────────────────────────────┘
          │                │                │
          ▼                ▼                ▼
┌─────────────────────────────────────────────────────────────┐
│              iShare Backend API (Port 3000)                 │
│         /listings  /bookings  /reviews  /users              │
└─────────────────────────────────────────────────────────────┘
```

## Prerequisites

- Python 3.10+
- iShare backend running on `localhost:3000`
- Virtual environment with dependencies installed

## Quick Start

### 1. Setup Environment

```bash
cd /Users/liuqi/PycharmProjects/DashboardAgent
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### 2. Start the API Server

```bash
source .venv/bin/activate
uvicorn my_agent2.api.endpoints:app --reload --port 8001
```

### 3. Verify Server is Running

```bash
curl http://localhost:8001/
```

Expected response:
```json
{"status": "ok", "service": "iShare Dashboard Agent API", "version": "2.0.0"}
```

### 4. Open Swagger Documentation

Visit: http://localhost:8001/docs

## API Endpoints

### Health Check

```http
GET /
```

Returns API status and version.

---

### Pricing Analysis

Analyze pricing for a listing and get AI-powered recommendations.

```http
POST /pricing/analyze
Content-Type: application/json

{
  "listing_id": "fdc645fe-c17a-48c6-9ad5-44a908238694",
  "token_id": "your-auth-token"
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
    "suggested_price": 105.0,
    "price_difference": 5.0,
    "adjustment_percent": 5.0,
    "adjustment_direction": "increase",
    "demand_level": "Medium",
    "reasons": [
      "Demand level is Medium",
      "3 public holiday bookings",
      "Current occupancy: 17%"
    ],
    "can_take_action": true
  },
  "show_action_button": true,
  "error": null
}
```

**Note:** If `show_action_button` is `true`, display the "Take Action" button in the UI.

---

### Apply Price Change (Take Action)

Apply the suggested price change to the database.

```http
POST /pricing/apply
Content-Type: application/json

{
  "listing_id": "fdc645fe-c17a-48c6-9ad5-44a908238694",
  "new_price": 105.0,
  "token_id": "your-auth-token"
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
    "new_price": 105.0,
    "message": "✅ Price updated successfully from $100.00 to $105.00"
  },
  "show_action_button": false,
  "error": null
}
```

---

### Market Trend Analysis

Analyze market trends for an owner's portfolio.

```http
POST /market/analyze
Content-Type: application/json

{
  "owner_id": 1,
  "token_id": "your-auth-token"
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
      "types": ["ACCOMMODATION", "ITEM", "TRANSPORT"],
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
  "show_action_button": false,
  "error": null
}
```

---

### Review Analysis

Analyze reviews and sentiment for a listing.

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
    "title": "Review Analysis for 'Chill Condo Room'",
    "overall_satisfaction": {
      "level": "Neutral",
      "emoji": "😐",
      "average_rating": 3.7,
      "max_rating": 5.0
    },
    "total_reviews": 10,
    "rating_distribution": {
      "5_star": {"count": 3, "percentage": 30},
      "4_star": {"count": 3, "percentage": 30},
      "3_star": {"count": 2, "percentage": 20},
      "2_star": {"count": 2, "percentage": 20},
      "1_star": {"count": 0, "percentage": 0}
    },
    "sentiment_analysis": {
      "overall": "Very Positive",
      "positive_mentions": 12,
      "negative_mentions": 0
    },
    "recurring_themes": [
      {"theme": "Cleanliness", "mention_count": 4, "sentiment": "positive"},
      {"theme": "Comfort", "mention_count": 3, "sentiment": "positive"}
    ],
    "recommendations": [
      "WiFi mentioned 1x - Upgrade internet plan or add WiFi extenders"
    ],
    "summary": "Based on 10 reviews with average rating 3.7/5.0..."
  },
  "show_action_button": false,
  "error": null
}
```

---

## Action Codes Reference

| Action Code | Endpoint | Agent | Description | Has Action Button |
|-------------|----------|-------|-------------|-------------------|
| `PRICING_ANALYZE` | POST /pricing/analyze | PricingAgent | Analyze pricing | Yes (if change recommended) |
| `PRICING_APPLY` | POST /pricing/apply | PricingAgent | Apply price change | No |
| `MARKET_ANALYZE` | POST /market/analyze | DemandTrendAgent | Market trends | No |
| `REVIEW_ANALYZE` | POST /review/analyze | ReviewAnalysisAgent | Review analysis | No |

## Frontend Integration

### React Example

```jsx
const PricingCard = ({ listingId }) => {
  const [analysis, setAnalysis] = useState(null);

  const handleCardClick = async () => {
    const response = await fetch('http://localhost:8001/pricing/analyze', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ listing_id: listingId, token_id: 'your-auth-token' })
    });
    setAnalysis(await response.json());
  };

  const handleTakeAction = async () => {
    const response = await fetch('http://localhost:8001/pricing/apply', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        listing_id: listingId,
        new_price: analysis.data.suggested_price,
        token_id: 'your-auth-token'
      })
    });
    const result = await response.json();
    alert(result.data.message);
  };

  return (
    <div onClick={handleCardClick}>
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

## Testing

Run the test script:

```bash
python my_agent2/api/test_api.py
```

Or run individual tests with curl (see test_api.py for examples).

## Error Handling

All endpoints return consistent error responses:

```json
{
  "success": false,
  "action_code": "PRICING_ANALYZE",
  "agent": "PricingAgent",
  "data": {},
  "show_action_button": false,
  "error": "listing_id is required for pricing analysis"
}
```

## CORS

CORS is enabled for all origins in development. Configure `allow_origins` in `endpoints.py` for production.

## Environment Variables

Create a `.env` file in the project root if needed:

```env
# iShare API URL (default: http://localhost:3000)
API_BASE_URL=http://localhost:3000
```

## Troubleshooting

### Port already in use
```bash
lsof -ti:8001 | xargs kill -9
```

### iShare backend not running
Ensure the NestJS backend is running on port 3000:
```bash
curl http://localhost:3000/listings
```

### Import errors
Make sure you're in the virtual environment:
```bash
source .venv/bin/activate
```
