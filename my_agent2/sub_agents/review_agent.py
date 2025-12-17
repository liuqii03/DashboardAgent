from google.adk.agents import LlmAgent

"""
Review tools for the analytics dashboard.

These functions interact with the in-memory database to fetch review
summaries for any listing and to flag reviews that mention a specific
issue. They support agents in understanding customer feedback and
highlighting areas for improvement.
"""

from typing import Dict, Any

from ..database.database import db


def fetch_review_data(listing_id: str) -> Dict[str, Any]:
    """
    Retrieve review data for a listing and compute overall sentiment and
    common themes.

    The sentiment is classified as positive, neutral, or negative based on
    the average rating. The most common theme is determined by
    scanning review comments for keywords such as 'clean', 'dirty',
    'comfortable', etc.

    :param listing_id: Identifier of the listing whose reviews to analyze.
    :return: A dictionary containing overall sentiment, common theme,
             and a message summarizing the findings.
    """
    reviews = db.get_reviews(listing_id)
    if not reviews:
        return {
            "listing_id": listing_id,
            "overall_sentiment": "No reviews",
            "common_theme": None,
            "message": f"There are no reviews for listing '{listing_id}'.",
        }
    # Compute average rating
    avg_rating = sum(r.rating for r in reviews) / len(reviews)
    # Determine sentiment
    if avg_rating >= 4.0:
        overall_sentiment = "Positive"
    elif avg_rating >= 2.0:
        overall_sentiment = "Neutral"
    else:
        overall_sentiment = "Negative"
    # Identify common theme based on keywords in comments
    keywords = {
        "clean": ["clean", "tidy", "spotless"],
        "dirty": ["dirty", "filthy", "messy"],
        "comfortable": ["comfortable", "cozy", "comfortable"],
        "quality": ["quality", "good", "excellent"],
        "missing": ["missing", "lost", "no"]
    }
    theme_counts: Dict[str, int] = {key: 0 for key in keywords}
    for review in reviews:
        comment = review.comment.lower()
        for theme, words in keywords.items():
            if any(word in comment for word in words):
                theme_counts[theme] += 1
    # Determine the most frequent theme if any
    common_theme = None
    if any(theme_counts.values()):
        common_theme = max(theme_counts, key=theme_counts.get)
    message_parts = [
        f"Overall sentiment is {overall_sentiment} based on an average rating of {avg_rating:.1f}.",
    ]
    if common_theme:
        message_parts.append(
            f"The most common theme in the comments is '{common_theme}'."
        )
    message = " ".join(message_parts)
    return {
        "listing_id": listing_id,
        "overall_sentiment": overall_sentiment,
        "common_theme": common_theme,
        "message": message,
    }


def flag_reviews(listing_id: str, issue: str = "clean") -> Dict[str, Any]:
    """
    Flag reviews of a listing that mention a specific issue.

    Delegates to the database to flag any reviews whose comments contain
    the given issue string (case-insensitive). Returns the result
    indicating how many reviews were flagged.

    :param listing_id: Identifier of the listing whose reviews to flag.
    :param issue: Keyword to search for in review comments.
    :return: A dictionary with status and message from the database.
    """
    return db.flag_reviews(listing_id, issue)

# Create the ReviewAnalysisAgent LLM agent
review_agent = LlmAgent(
    model="gemini-2.5-flash",
    name="ReviewAnalysisAgent",
    description="Customer review analysis specialist.",
    instruction=(
        "You are an expert at analysing customer reviews for rental listings. Your role is to summarise the overall sentiment, "
        "identify common themes, and suggest improvements or highlight positive feedback based on those reviews.\n\n"
        "When responding to a query:\n"
        "1. Ensure that the user has specified a listing ID or title. If the listing is not clear, politely ask the user to provide or confirm the listing ID.\n"
        "   When you ask for the listing ID, wait for the user to reply and then remember the ID they provide. Use that listing ID in the subsequent steps.\n"
        "   If you are handling a multi‑aspect analysis and the listing ID was provided earlier, do not ask for the ID again – simply use the existing ID for your analysis.\n"
        "2. Use the `fetch_review_data` tool with the provided listing ID to retrieve the average rating, overall sentiment (Positive/Neutral/Negative) and any common theme found in the comments. Summarise these findings clearly, mentioning the average rating and any notable theme.\n"
        "3. If the overall sentiment is positive, highlight the strengths and encourage the owner to maintain the good work.\n"
        "4. If the sentiment is neutral or negative, emphasise the common theme and suggest specific improvements to address that issue (for example, improving cleanliness if cleanliness is a common theme).\n"
        "5. After presenting your analysis, ask the user if they would like to flag the reviews mentioning the common theme. Only call the `flag_reviews` tool once the user explicitly confirms they want to flag reviews, passing the listing ID and the issue (the common theme) to the tool.\n\n"
        "If the user’s query is about pricing, demand or occupancy instead of reviews, call the ADK function `transfer_to_agent` with 'DemandPricingAgent'. "
        "If it is about booking durations, occupancy trends or discount strategies, transfer to 'BookingTrendAgent'.\n"
        "If the user asks to analyse **all aspects** or mentions multiple domains (pricing, bookings and reviews), you are the final specialist in the chain. \n"
        "Provide your analysis and do not transfer control to another agent. Once you finish, the multi‑aspect analysis is complete.\n"
        "When the user’s intent is unclear or ambiguous, ask a clarifying question before taking any action. Always be supportive and clear in your responses, "
        "and never call an action tool without the user's explicit confirmation."
    ),
    tools=[fetch_review_data, flag_reviews],
)
