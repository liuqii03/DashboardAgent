"""
Simple in-memory database for the analytics dashboard.

This module defines a basic `Database` class and a global `db` instance
that stores information about users, listings, bookings, and reviews.
It exposes methods to retrieve and update this data. In a real-world
application, these methods would query an actual database or API.

The data structures here are provided for demonstration purposes and
should be replaced with real data integrations as needed.
"""

from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any

@dataclass
class User:
    userId: str
    username: str
    email: str
    passwordHash: str
    currentRole: str  # e.g., 'owner' or 'renter'
    walletAddress: str
    reputationScore: float


@dataclass
class Listing:
    listingId: str
    ownerId: str
    title: str
    description: str
    basePrice: float
    location: str
    status: str  # e.g., 'available' or 'booked'
    images: List[str]
    category: str  # 'vehicle', 'item', or 'accommodation'
    policyTemplateIds: List[str] = field(default_factory=list)
    insuranceTemplateId: Optional[str] = None
    discountPercent: float = 0.0  # Current discount applied


@dataclass
class Booking:
    bookingId: str
    listingId: str
    renterId: str
    startDate: datetime
    endDate: datetime
    totalPrice: float
    status: str  # e.g., 'confirmed', 'cancelled'
    paymentTxHash: str
    appliedPoliciesJson: str
    appliedInsuranceJson: str


@dataclass
class Review:
    reviewId: str
    bookingId: str
    reviewerId: str
    reviewedId: str
    rating: int
    comment: str
    timestamp: datetime
    flagged: bool = False


class Database:
    """
    A simple in-memory database to store and retrieve listings, bookings,
    reviews, and user data. Provides methods for agents to query and
    update information.
    """

    def __init__(self) -> None:
        # Initialize sample users
        self.users: Dict[str, User] = {
            "user001": User(
                userId="user001",
                username="Alice",
                email="alice@example.com",
                passwordHash="hashed_password",
                currentRole="owner",
                walletAddress="0xA1B2C3D4",
                reputationScore=4.8,
            ),
            "user002": User(
                userId="user002",
                username="Bob",
                email="bob@example.com",
                passwordHash="hashed_password",
                currentRole="renter",
                walletAddress="0xE5F6G7H8",
                reputationScore=4.5,
            ),
        }

        # Initialize sample listings
        self.listings: Dict[str, Listing] = {
            "car001": Listing(
                listingId="car001",
                ownerId="user001",
                title="Toyota Corolla 2019",
                description="Reliable sedan, great on fuel.",
                basePrice=50.0,
                location="Seri Kembangan, Selangor",
                status="available",
                images=[],
                category="vehicle",
                policyTemplateIds=["policy001"],
                insuranceTemplateId="insurance001",
            ),
            "cam001": Listing(
                listingId="cam001",
                ownerId="user001",
                title="Canon EOS R6 Camera",
                description="Full-frame mirrorless camera with 4K video.",
                basePrice=30.0,
                location="Seri Kembangan, Selangor",
                status="available",
                images=[],
                category="item",
                policyTemplateIds=["policy001"],
                insuranceTemplateId="insurance002",
            ),
            "acc001": Listing(
                listingId="acc001",
                ownerId="user002",
                title="Cozy Apartment in KL",
                description="One-bedroom apartment in Bukit Bintang area.",
                basePrice=80.0,
                location="Kuala Lumpur",
                status="available",
                images=[],
                category="accommodation",
                policyTemplateIds=["policy003"],
                insuranceTemplateId="insurance003",
            ),
        }

        # Initialize sample bookings
        now = datetime.now()
        self.bookings: Dict[str, List[Booking]] = {
            "car001": [
                # High demand for car001: bookings span most of the last 30 days
                Booking(
                    bookingId="b001",
                    listingId="car001",
                    renterId="user002",
                    # 15-day booking from 25 days ago to 10 days ago
                    startDate=now - timedelta(days=25),
                    endDate=now - timedelta(days=10),
                    totalPrice=750.0,
                    status="confirmed",
                    paymentTxHash="txh1",
                    appliedPoliciesJson="{}",
                    appliedInsuranceJson="{}",
                ),
                Booking(
                    bookingId="b002",
                    listingId="car001",
                    renterId="user002",
                    # 6-day booking from 9 days ago to 3 days ago
                    startDate=now - timedelta(days=9),
                    endDate=now - timedelta(days=3),
                    totalPrice=300.0,
                    status="confirmed",
                    paymentTxHash="txh2",
                    appliedPoliciesJson="{}",
                    appliedInsuranceJson="{}",
                ),
                Booking(
                    bookingId="b003",
                    listingId="car001",
                    renterId="user002",
                    # 2-day booking from 2 days ago to today
                    startDate=now - timedelta(days=2),
                    endDate=now,
                    totalPrice=100.0,
                    status="confirmed",
                    paymentTxHash="txh3",
                    appliedPoliciesJson="{}",
                    appliedInsuranceJson="{}",
                ),
            ],
            "cam001": [
                Booking(
                    bookingId="b004",
                    listingId="cam001",
                    renterId="user002",
                    startDate=now - timedelta(days=12),
                    endDate=now - timedelta(days=11),
                    totalPrice=30.0,
                    status="confirmed",
                    paymentTxHash="txh4",
                    appliedPoliciesJson="{}",
                    appliedInsuranceJson="{}",
                ),
            ],
            "acc001": [
                Booking(
                    bookingId="b005",
                    listingId="acc001",
                    renterId="user001",
                    startDate=now - timedelta(days=20),
                    endDate=now - timedelta(days=15),
                    totalPrice=400.0,
                    status="confirmed",
                    paymentTxHash="txh5",
                    appliedPoliciesJson="{}",
                    appliedInsuranceJson="{}",
                ),
                Booking(
                    bookingId="b006",
                    listingId="acc001",
                    renterId="user001",
                    startDate=now - timedelta(days=10),
                    endDate=now - timedelta(days=5),
                    totalPrice=400.0,
                    status="confirmed",
                    paymentTxHash="txh6",
                    appliedPoliciesJson="{}",
                    appliedInsuranceJson="{}",
                ),
            ],
        }

        # Initialize sample reviews
        self.reviews: Dict[str, List[Review]] = {
            "car001": [
                Review(
                    reviewId="r001",
                    bookingId="b001",
                    reviewerId="user002",
                    reviewedId="user001",
                    rating=5,
                    comment="Great car, very clean and comfortable!",
                    timestamp=now - timedelta(days=7),
                ),
                Review(
                    reviewId="r002",
                    bookingId="b002",
                    reviewerId="user002",
                    reviewedId="user001",
                    rating=4,
                    comment="Smooth ride, but could improve on cleanliness.",
                    timestamp=now - timedelta(days=3),
                ),
                Review(
                    reviewId="r003",
                    bookingId="b003",
                    reviewerId="user002",
                    reviewedId="user001",
                    rating=5,
                    comment="Excellent service and very fuel-efficient.",
                    timestamp=now - timedelta(days=1),
                ),
            ],
            "cam001": [
                Review(
                    reviewId="r004",
                    bookingId="b004",
                    reviewerId="user002",
                    reviewedId="user001",
                    rating=4,
                    comment="Camera quality is superb, but strap was missing.",
                    timestamp=now - timedelta(days=10),
                ),
            ],
            "acc001": [
                Review(
                    reviewId="r005",
                    bookingId="b005",
                    reviewerId="user001",
                    reviewedId="user002",
                    rating=3,
                    comment="Apartment was cozy but not as clean as expected.",
                    timestamp=now - timedelta(days=18),
                ),
                Review(
                    reviewId="r006",
                    bookingId="b006",
                    reviewerId="user001",
                    reviewedId="user002",
                    rating=5,
                    comment="Wonderful stay, great location and amenities.",
                    timestamp=now - timedelta(days=7),
                ),
            ],
        }

    # --- Retrieval methods ---
    def get_user(self, user_id: str) -> Optional[User]:
        return self.users.get(user_id)

    def get_listing(self, listing_id: str) -> Optional[Listing]:
        return self.listings.get(listing_id)

    def get_bookings(self, listing_id: str) -> List[Booking]:
        return self.bookings.get(listing_id, [])

    def get_reviews(self, listing_id: str) -> List[Review]:
        return self.reviews.get(listing_id, [])

    # --- Update methods ---
    def update_listing_price(self, listing_id: str, increase_percent: float) -> Dict[str, Any]:
        listing = self.listings.get(listing_id)
        if not listing:
            return {"status": "error", "message": f"Listing '{listing_id}' not found."}
        # Increase the base price by the given percentage
        original_price = listing.basePrice
        listing.basePrice = listing.basePrice * (1 + increase_percent / 100)
        return {
            "status": "success",
            "message": (
                f"Price for listing '{listing_id}' increased from {original_price:.2f} to {listing.basePrice:.2f} "
                f"({increase_percent:.0f}% increase)."
            ),
        }

    def apply_discount(self, listing_id: str, discount_percent: float) -> Dict[str, Any]:
        listing = self.listings.get(listing_id)
        if not listing:
            return {"status": "error", "message": f"Listing '{listing_id}' not found."}
        # Set discount percent on listing
        listing.discountPercent = discount_percent
        return {
            "status": "success",
            "message": (
                f"A discount of {discount_percent:.0f}% has been applied to listing '{listing_id}'."
            ),
        }

    def flag_reviews(self, listing_id: str, issue: str) -> Dict[str, Any]:
        reviews = self.reviews.get(listing_id)
        if not reviews:
            return {"status": "error", "message": f"No reviews found for listing '{listing_id}'."}
        count = 0
        for review in reviews:
            if issue.lower() in review.comment.lower():
                review.flagged = True
                count += 1
        return {
            "status": "success",
            "message": f"Flagged {count} review(s) mentioning '{issue}' for listing '{listing_id}'.",
        }


# Create a global database instance that can be imported by tools
db = Database()
