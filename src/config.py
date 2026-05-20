"""
Customer Support Workflow — Configuration (PROVIDED, do not modify).
"""

# Valid intent categories for classification
INTENT_CATEGORIES = [
    "refund",
    "shipping",
    "product_inquiry",
    "complaint",
    "general",
]

# Priority levels (low to highest)
PRIORITY_LEVELS = ["low", "medium", "high", "urgent"]

# Valid sentiment values
SENTIMENTS = ["positive", "neutral", "negative", "angry"]

# Keywords/signals that suggest escalation is needed
ESCALATION_SIGNALS = [
    "lawyer", "legal", "sue", "attorney",
    "BBB", "consumer protection",
    "social media", "going public",
    "unacceptable", "outrageous", "disgusted",
    "third time", "multiple times", "again and again",
]

# ──────────────────────────────────────────────────────────────
# Sample customer messages for local testing
# Use these to test your workflow during development.
# Your final solution will be graded on a DIFFERENT set of messages.
# ──────────────────────────────────────────────────────────────
SAMPLE_MESSAGES = [
    {
        "id": 1,
        "message": (
            "Hi, I ordered a bluetooth speaker 2 weeks ago and it still "
            "hasn't arrived. My order number is #48291. Can you check "
            "where it is?"
        ),
        "expected_intent": "shipping",
        "should_escalate": False,
    },
    {
        "id": 2,
        "message": (
            "I want a full refund for order #33012. The headphones I "
            "received are completely broken — one ear doesn't produce "
            "any sound at all."
        ),
        "expected_intent": "refund",
        "should_escalate": False,
    },
    {
        "id": 3,
        "message": (
            "This is absolutely UNACCEPTABLE. I have been waiting for "
            "THREE WEEKS for my order and nobody has responded to my "
            "last 4 emails. I am considering contacting my lawyer if "
            "this isn't resolved TODAY."
        ),
        "expected_intent": "complaint",
        "should_escalate": True,
    },
    {
        "id": 4,
        "message": (
            "Does the UltraView 4K monitor come with an HDMI cable "
            "included? Also, what's the refresh rate? Thinking about "
            "buying one."
        ),
        "expected_intent": "product_inquiry",
        "should_escalate": False,
    },
    {
        "id": 5,
        "message": (
            "Hey, I just wanted to say thanks! My order arrived a day "
            "early and the packaging was perfect. Great job!"
        ),
        "expected_intent": "general",
        "should_escalate": False,
    },
    {
        "id": 6,
        "message": (
            "I need to return the laptop I bought last week. It's within "
            "the return window. How do I get a refund? Order #77820."
        ),
        "expected_intent": "refund",
        "should_escalate": False,
    },
    {
        "id": 7,
        "message": (
            "Your company is a scam. I've been charged twice for the "
            "same order and nobody picks up the phone. I'm going to "
            "post about this on social media and report you to the BBB."
        ),
        "expected_intent": "complaint",
        "should_escalate": True,
    },
    {
        "id": 8,
        "message": (
            "Can I change the shipping address on order #55103? I'm "
            "moving next week and need it delivered to my new place."
        ),
        "expected_intent": "shipping",
        "should_escalate": False,
    },
    {
        "id": 9,
        "message": (
            "What's the difference between the Pro and Standard versions "
            "of your wireless earbuds? I saw both on the website but the "
            "comparison chart is confusing."
        ),
        "expected_intent": "product_inquiry",
        "should_escalate": False,
    },
    {
        "id": 10,
        "message": "How do I update my account email address?",
        "expected_intent": "general",
        "should_escalate": False,
    },
    {
        "id": 11,
        "message": (
            "I received someone else's order! This is the second time "
            "this has happened. The package has a completely different "
            "name on it. I want my correct items AND a refund for the "
            "hassle."
        ),
        "expected_intent": "complaint",
        "should_escalate": True,
    },
    {
        "id": 12,
        "message": (
            "My tracking number says delivered but I never got the "
            "package. It's a $200 order. Can someone help?"
        ),
        "expected_intent": "shipping",
        "should_escalate": False,
    },
]
