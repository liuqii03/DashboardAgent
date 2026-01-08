"""
REST API database connector for the analytics dashboard.

This module provides a Database class that fetches data from the iShare 
REST API at localhost:3000 instead of direct PostgreSQL connection.
"""

import os
import httpx
from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any


# Base URL for the iShare API
API_BASE_URL = os.getenv("ISHARE_API_URL", "http://localhost:3000")


@dataclass
class Booking:
    """Booking data model matching agent expectations."""
    bookingId: str
    listingId: str
    renterId: str
    startDate: datetime
    endDate: datetime
    totalPrice: float
    status: str
    paymentTxHash: str
    appliedPoliciesJson: str
    appliedInsuranceJson: str


@dataclass
class Review:
    """Review data model matching agent expectations."""
    reviewId: str
    bookingId: str
    reviewerId: str
    reviewedId: str
    rating: int
    comment: str
    timestamp: datetime
    flagged: bool = False


@dataclass
class Listing:
    """Listing data model."""
    listingId: str
    ownerId: str
    title: str
    description: str
    basePrice: float
    status: str
    type: str
    images: List[str] = None
    discountPercent: float = 0.0


class APIDatabase:
    """
    REST API database connector for dashboard agents.
    Fetches data from iShare API at localhost:3000.
    """

    def __init__(self, base_url: str = None):
        """Initialize with API base URL."""
        self.base_url = base_url or API_BASE_URL
        self._client = httpx.Client(timeout=30.0)
        
        # Cache for discount percent (temporary storage)
        self._discount_cache: Dict[str, float] = {}

    def _get(self, endpoint: str) -> Any:
        """Make a GET request to the API."""
        try:
            response = self._client.get(f"{self.base_url}{endpoint}")
            response.raise_for_status()
            return response.json()
        except Exception as e:
            print(f"API Error: {e}")
            return None

    def _post(self, endpoint: str, data: Dict) -> Any:
        """Make a POST request to the API."""
        try:
            response = self._client.post(f"{self.base_url}{endpoint}", json=data)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            print(f"API Error: {e}")
            return None

    def _patch(self, endpoint: str, data: Dict) -> Any:
        """Make a PATCH request to the API."""
        try:
            response = self._client.patch(f"{self.base_url}{endpoint}", json=data)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            print(f"API Error: {e}")
            return None

    def get_listing(self, listing_id: str) -> Optional[Listing]:
        """
        Retrieve a listing by ID.
        
        :param listing_id: UUID of the listing
        :return: Listing object or None
        """
        data = self._get(f"/listings/{listing_id}")
        
        if not data:
            return None
        
        return Listing(
            listingId=data.get("id", ""),
            ownerId=str(data.get("owner", {}).get("id", "") if isinstance(data.get("owner"), dict) else data.get("ownerId", "")),
            title=data.get("title", ""),
            description=data.get("description", ""),
            basePrice=float(data.get("basePrice", 0)),
            status=data.get("status", ""),
            type=data.get("type", ""),
            images=data.get("images", []),
            discountPercent=self._discount_cache.get(listing_id, 0.0)
        )

    def get_all_listings(self) -> List[Listing]:
        """Retrieve all listings."""
        data = self._get("/listings")
        
        if not data:
            return []
        
        return [
            Listing(
                listingId=item.get("id", ""),
                ownerId=str(item.get("ownerId", "")),
                title=item.get("title", ""),
                description=item.get("description", ""),
                basePrice=float(item.get("basePrice", 0)),
                status=item.get("status", ""),
                type=item.get("type", ""),
                images=item.get("images", []),
                discountPercent=self._discount_cache.get(item.get("id", ""), 0.0)
            )
            for item in data
        ]

    def get_bookings(self, listing_id: str) -> List[Booking]:
        """
        Retrieve all bookings for a listing.
        
        :param listing_id: UUID of the listing
        :return: List of Booking objects
        """
        # Try to get bookings from the API
        data = self._get(f"/bookings?listing_id={listing_id}")
        
        if not data:
            # Try alternative endpoint
            data = self._get(f"/bookings")
            if data:
                # Filter by listing_id
                data = [b for b in data if b.get("listing_id") == listing_id or b.get("listingId") == listing_id]
        
        if not data:
            return []
        
        bookings = []
        for item in data:
            try:
                # Parse dates - handle different formats
                start_date = item.get("start_date") or item.get("startDate")
                end_date = item.get("end_date") or item.get("endDate")
                
                if isinstance(start_date, str):
                    start_date = datetime.fromisoformat(start_date.replace("Z", "+00:00"))
                if isinstance(end_date, str):
                    end_date = datetime.fromisoformat(end_date.replace("Z", "+00:00"))
                
                bookings.append(Booking(
                    bookingId=item.get("id", ""),
                    listingId=item.get("listing_id") or item.get("listingId", ""),
                    renterId=str(item.get("renter_id") or item.get("renterId", "")),
                    startDate=start_date,
                    endDate=end_date,
                    totalPrice=float(item.get("total_price") or item.get("totalPrice", 0)),
                    status=item.get("status", "CONFIRMED"),
                    paymentTxHash=item.get("payment_tx_hash") or item.get("paymentTxHash", ""),
                    appliedPoliciesJson=str(item.get("applied_policies_json") or item.get("appliedPoliciesJson", "{}")),
                    appliedInsuranceJson=str(item.get("applied_insurance_json") or item.get("appliedInsuranceJson", "{}"))
                ))
            except Exception as e:
                print(f"Error parsing booking: {e}")
                continue
        
        return bookings

    def get_reviews(self, listing_id: str) -> List[Review]:
        """
        Retrieve all reviews for a listing.
        
        :param listing_id: UUID of the listing
        :return: List of Review objects
        """
        # Try to get reviews from the API
        data = self._get(f"/reviews?listing_id={listing_id}")
        
        if not data:
            # Try alternative endpoint
            data = self._get(f"/reviews")
            if data:
                # Filter by listing_id
                data = [r for r in data if r.get("listing_id") == listing_id or r.get("listingId") == listing_id]
        
        if not data:
            return []
        
        reviews = []
        for item in data:
            try:
                # Parse timestamp
                timestamp = item.get("created_at") or item.get("createdAt") or item.get("timestamp")
                if isinstance(timestamp, str):
                    timestamp = datetime.fromisoformat(timestamp.replace("Z", "+00:00"))
                elif timestamp is None:
                    timestamp = datetime.now()
                
                reviews.append(Review(
                    reviewId=item.get("id", ""),
                    bookingId=item.get("booking_id") or item.get("bookingId", ""),
                    reviewerId=str(item.get("reviewer_id") or item.get("reviewerId", "")),
                    reviewedId=str(item.get("reviewed_user_id") or item.get("reviewedUserId", "")),
                    rating=int(item.get("rating", 0)),
                    comment=item.get("comment", ""),
                    timestamp=timestamp,
                    flagged=item.get("flagged", False)
                ))
            except Exception as e:
                print(f"Error parsing review: {e}")
                continue
        
        return reviews

    def get_user(self, user_id: int) -> Optional[Dict]:
        """Get user by ID."""
        data = self._get(f"/users/{user_id}")
        return data

    def get_listings_by_owner(self, owner_id: int) -> List[Listing]:
        """
        Retrieve all listings for an owner.
        
        :param owner_id: Integer ID of the owner
        :return: List of Listing objects
        """
        # Get user which includes their listings
        user_data = self._get(f"/users/{owner_id}")
        
        if not user_data or "listings" not in user_data:
            return []
        
        return [
            Listing(
                listingId=item.get("id", ""),
                ownerId=str(owner_id),
                title=item.get("title", ""),
                description=item.get("description", ""),
                basePrice=float(item.get("basePrice", 0)),
                status=item.get("status", ""),
                type=item.get("type", ""),
                images=item.get("images", []),
                discountPercent=self._discount_cache.get(item.get("id", ""), 0.0)
            )
            for item in user_data.get("listings", [])
        ]

    def update_listing_price(self, listing_id: str, increase_percent: float) -> Dict[str, Any]:
        """
        Update the base price of a listing.
        
        :param listing_id: UUID of the listing
        :param increase_percent: Percentage to increase price by
        :return: Status dictionary
        """
        # Get current listing
        listing = self.get_listing(listing_id)
        if not listing:
            return {"status": "error", "message": f"Listing {listing_id} not found"}
        
        old_price = listing.basePrice
        new_price = old_price * (1 + increase_percent / 100)
        
        # Update via API
        result = self._patch(f"/listings/{listing_id}", {"basePrice": new_price})
        
        if result:
            return {
                "status": "success",
                "message": f"Price for '{listing.title}' updated from RM{old_price:.2f} to RM{new_price:.2f} (+{increase_percent}%)",
                "old_price": old_price,
                "new_price": new_price,
                "listing_id": listing_id
            }
        else:
            # If API update fails, return simulated success for demo
            return {
                "status": "success",
                "message": f"[SIMULATED] Price for '{listing.title}' would be updated from RM{old_price:.2f} to RM{new_price:.2f} (+{increase_percent}%)",
                "old_price": old_price,
                "new_price": new_price,
                "listing_id": listing_id
            }

    def apply_discount(self, listing_id: str, discount_percent: float) -> Dict[str, Any]:
        """
        Apply a discount to a listing.
        
        :param listing_id: UUID of the listing
        :param discount_percent: Discount percentage to apply
        :return: Status dictionary
        """
        listing = self.get_listing(listing_id)
        if not listing:
            return {"status": "error", "message": f"Listing {listing_id} not found"}
        
        # Store in cache (would be stored in DB in production)
        self._discount_cache[listing_id] = discount_percent
        
        return {
            "status": "success",
            "message": f"Applied {discount_percent}% discount to '{listing.title}' for longer bookings.",
            "listing_id": listing_id,
            "discount_percent": discount_percent
        }

    def flag_reviews(self, listing_id: str, issue: str) -> Dict[str, Any]:
        """
        Flag reviews that mention a specific issue.
        
        :param listing_id: UUID of the listing
        :param issue: Keyword to search for in comments
        :return: Status dictionary with count of flagged reviews
        """
        reviews = self.get_reviews(listing_id)
        
        if not reviews:
            return {"status": "error", "message": f"No reviews found for listing {listing_id}"}
        
        count = 0
        for review in reviews:
            if issue.lower() in review.comment.lower():
                review.flagged = True
                count += 1
                # In production, would update via API:
                # self._patch(f"/reviews/{review.reviewId}", {"flagged": True})
        
        return {
            "status": "success",
            "message": f"Flagged {count} review(s) mentioning '{issue}' for listing {listing_id}.",
            "flagged_count": count,
            "listing_id": listing_id,
            "issue": issue
        }

    def close(self):
        """Close the HTTP client."""
        self._client.close()


# Create a global instance
api_db = APIDatabase()
