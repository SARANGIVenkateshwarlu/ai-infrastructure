"""
Customer Support Workflow — TODO: Implement the 4 functions below.

Build a LangGraph StateGraph that processes customer support messages.
Your workflow should classify the intent, route appropriately, generate
a response, and decide whether escalation is needed.

You MUST use LangGraph's StateGraph to build this workflow.
You may add as many helper functions, nodes, and edges as you want.
Do NOT change the signatures of the 4 designated functions below.

Provided utilities (import and use these):
    from state import SupportState
    from config import INTENT_CATEGORIES, PRIORITY_LEVELS, ESCALATION_SIGNALS
    from llm import call_llm
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from state import SupportState
from config import (
    INTENT_CATEGORIES,
    PRIORITY_LEVELS,
    ESCALATION_SIGNALS,
    SAMPLE_MESSAGES,
)
from llm import call_llm

from langgraph.graph import StateGraph, START, END


# ═══════════════════════════════════════════════════════════════════════════
# Helper Functions
# ═══════════════════════════════════════════════════════════════════════════

def _analyze_sentiment(message: str) -> str:
    """Analyze sentiment using LLM with keyword fallback."""
    prompt = (
        "Analyze the sentiment of the following customer message. "
        "Respond with exactly one word: positive, neutral, negative, or angry. "
        "Do not include any explanation or punctuation.\n\n"
        f"Message: {message}"
    )
    try:
        result = call_llm(
            system_prompt="You are a sentiment analysis assistant.",
            user_message=prompt,
            temperature=0.0,
            max_tokens=10,
        ).strip().lower()
        for sentiment in ["angry", "negative", "neutral", "positive"]:
            if sentiment in result:
                return sentiment
    except Exception:
        pass

    # Fallback keyword matching
    msg_lower = message.lower()
    angry_words = [
        "unacceptable", "outrageous", "disgusted", "furious",
        "lawsuit", "lawyer", "scam", "terrible", "worst",
    ]
    negative_words = [
        "broken", "disappointed", "frustrated", "bad", "wrong",
        "missing", "never", "problem", "issue",
    ]
    positive_words = [
        "thanks", "thank you", "great", "perfect", "excellent",
        "happy", "love", "appreciate", "awesome",
    ]

    for word in angry_words:
        if word in msg_lower:
            return "angry"
    for word in negative_words:
        if word in msg_lower:
            return "negative"
    for word in positive_words:
        if word in msg_lower:
            return "positive"
    return "neutral"


def _assign_priority(intent: str, sentiment: str) -> str:
    """Assign priority based on intent and sentiment."""
    if intent == "complaint" and sentiment in ("angry", "negative"):
        return "urgent"
    elif intent == "refund" and sentiment in ("angry", "negative"):
        return "high"
    elif intent == "complaint":
        return "high"
    elif intent == "refund":
        return "medium"
    elif intent == "shipping":
        return "medium"
    elif intent == "product_inquiry":
        return "low"
    elif sentiment == "positive":
        return "low"
    return "medium"


def _generate_response(state: SupportState) -> str:
    """Generate a context-aware response using LLM with template fallback."""
    message = state["customer_message"]
    intent = state["intent"]
    sentiment = state["sentiment"]
    priority = state["priority"]
    escalate = state["escalate"]

    if escalate:
        prompt = (
            "The following customer message has been flagged for escalation to a human agent. "
            "Write a brief, empathetic response acknowledging their concern and assuring them "
            "that a specialist will contact them within 24 hours. Do not include a subject line.\n\n"
            f"Customer message: {message}\n"
            f"Intent: {intent}\n"
            f"Sentiment: {sentiment}\n"
            f"Priority: {priority}"
        )
    else:
        prompt = (
            "Write a helpful, empathetic customer support response for the following message. "
            f"The customer's intent is '{intent}' and their sentiment is '{sentiment}'. "
            "Be concise but thorough. Do not include a subject line.\n\n"
            f"Customer message: {message}"
        )

    try:
        return call_llm(
            system_prompt="You are a professional customer support agent.",
            user_message=prompt,
            temperature=0.5,
            max_tokens=512,
        ).strip()
    except Exception:
        pass

    # Fallback templates
    if escalate:
        return (
            "We truly apologize for the frustration this has caused. Your concern has been "
            "escalated to one of our specialists who will personally reach out to you within "
            "24 hours to resolve this matter."
        )

    templates = {
        "refund": (
            "Thank you for reaching out. We're sorry to hear about the issue with your order. "
            "I've initiated a review of your refund request and you should receive an update "
            "within 1-2 business days."
        ),
        "shipping": (
            "Thank you for contacting us about your delivery. I've located your shipment and "
            "will provide you with tracking updates shortly. If you need further assistance, "
            "please don't hesitate to ask."
        ),
        "product_inquiry": (
            "Thanks for your interest in our products! I'd be happy to help answer your questions. "
            "Here are the details you requested. Please let me know if there's anything else."
        ),
        "complaint": (
            "We sincerely apologize for the experience you've had. Your feedback is important to us "
            "and I've escalated this to our team for immediate review. A specialist will follow up "
            "with you shortly."
        ),
        "general": (
            "Thank you for getting in touch! I'm happy to help with your request. "
            "Here is the information you need. Let me know if there's anything else I can assist with."
        ),
    }
    return templates.get(intent, templates["general"])


# ═══════════════════════════════════════════════════════════════════════════
# Graph Nodes
# ═══════════════════════════════════════════════════════════════════════════

def _classify_node(state: SupportState):
    """Node: classify intent, analyze sentiment, assign priority."""
    message = state["customer_message"]
    intent = classify_intent(message)
    sentiment = _analyze_sentiment(message)
    priority = _assign_priority(intent, sentiment)
    reasoning = (
        f"Message classified as '{intent}' with '{sentiment}' sentiment "
        f"and assigned '{priority}' priority."
    )
    return {
        "intent": intent,
        "sentiment": sentiment,
        "priority": priority,
        "reasoning": reasoning,
    }


def _escalation_node(state: SupportState):
    """Node: determine whether escalation is required."""
    escalate = should_escalate(state)
    return {"escalate": escalate}


def _auto_respond_node(state: SupportState):
    """Node: generate an automated customer response."""
    response = _generate_response(state)
    return {"response": response}


def _human_handoff_node(state: SupportState):
    """Node: generate a handoff message for human agents."""
    response = _generate_response(state)
    return {"response": response}


def _route_escalation(state: SupportState) -> str:
    """Conditional edge: route to auto-respond or human handoff."""
    if state["escalate"]:
        return "human_handoff"
    return "auto_respond"


# ═══════════════════════════════════════════════════════════════════════════
# Part 1: Graph Architecture (~45 min)
# ═══════════════════════════════════════════════════════════════════════════

def build_graph():
    """
    Build and return a compiled LangGraph StateGraph for the customer
    support workflow.

    Your graph must:
        - Use SupportState as the state schema
        - Have at least 2 nodes
        - Have edges connecting the nodes (conditional or direct)
        - Compile successfully (call .compile() before returning)

    The returned graph should be ready to invoke with:
        result = graph.invoke({"customer_message": "some message"})

    Returns:
        A compiled LangGraph StateGraph.

    Hints:
        - Think about what steps a human support agent would follow
        - Consider which steps need LLM calls vs. simple logic
        - Use conditional edges for routing based on intent or priority
    """
    builder = StateGraph(SupportState)

    # Register nodes
    builder.add_node("classify", _classify_node)
    builder.add_node("escalation_check", _escalation_node)
    builder.add_node("auto_respond", _auto_respond_node)
    builder.add_node("human_handoff", _human_handoff_node)

    # Define edges
    builder.add_edge(START, "classify")
    builder.add_edge("classify", "escalation_check")
    builder.add_conditional_edges(
        "escalation_check",
        _route_escalation,
        {
            "auto_respond": "auto_respond",
            "human_handoff": "human_handoff",
        },
    )
    builder.add_edge("auto_respond", END)
    builder.add_edge("human_handoff", END)

    return builder.compile()


# ═══════════════════════════════════════════════════════════════════════════
# Part 2: Node Implementation (~1 hr)
# ═══════════════════════════════════════════════════════════════════════════

def classify_intent(message: str) -> str:
    """
    Classify the intent of a customer message.

    Use the LLM (via call_llm) to determine the customer's intent.
    The returned intent MUST be one of the values in INTENT_CATEGORIES:
        'refund', 'shipping', 'product_inquiry', 'complaint', 'general'

    Args:
        message: The raw customer message text.

    Returns:
        str: One of the valid intent categories.
    """
    prompt = (
        "Classify the intent of the following customer support message into exactly one category. "
        f"Valid categories: {', '.join(INTENT_CATEGORIES)}. "
        "Respond with only the category name, no explanation or punctuation.\n\n"
        f"Message: {message}"
    )

    try:
        result = call_llm(
            system_prompt="You are an intent classification assistant.",
            user_message=prompt,
            temperature=0.0,
            max_tokens=20,
        ).strip().lower()
        for intent in INTENT_CATEGORIES:
            if intent in result:
                return intent
    except Exception:
        pass

    # Fallback keyword-based classification (no API key or LLM failure)
    msg_lower = message.lower()
    if any(w in msg_lower for w in ["refund", "return", "money back", "get my money"]):
        return "refund"
    if any(w in msg_lower for w in [
        "shipping", "delivery", "track", "arrived", "package",
        "where is my", "order hasn't", "change the shipping address", "delivered",
    ]):
        return "shipping"
    if any(w in msg_lower for w in [
        "difference between", "come with", "spec", "feature",
        "wondering about", "thinking about buying", "version", "compare",
    ]):
        return "product_inquiry"
    if any(w in msg_lower for w in [
        "unacceptable", "lawyer", "legal", "sue", "attorney", "bbb",
        "scam", "outrageous", "disgusted", "second time", "third time",
        "multiple times", "charged twice", "social media", "going public",
        "consumer protection",
    ]):
        return "complaint"
    if any(w in msg_lower for w in ["thanks", "thank you", "how do i", "question", "help", "account"]):
        return "general"

    return "general"


def should_escalate(state: dict) -> bool:
    """
    Determine whether a customer message should be escalated to a human.

    Consider factors like:
        - Angry or threatening tone
        - Legal threats
        - Repeated issues (mentions of "again", "third time", etc.)
        - High-value or complex issues

    You may use the LLM, rule-based logic, or a combination.

    Args:
        state: The current SupportState dict (has customer_message, intent,
               sentiment, priority, etc.)

    Returns:
        bool: True if the ticket should be escalated, False otherwise.
    """
    message = state.get("customer_message", "")
    sentiment = state.get("sentiment", "neutral")
    priority = state.get("priority", "low")
    intent = state.get("intent", "general")

    msg_lower = message.lower()

    # Rule 1: explicit escalation signals from config
    for signal in ESCALATION_SIGNALS:
        if signal.lower() in msg_lower:
            return True

    # Rule 2: angry sentiment combined with complaint intent
    if sentiment == "angry" and intent == "complaint":
        return True

    # Rule 3: urgent priority complaints
    if priority == "urgent" and intent == "complaint":
        return True

    # Rule 4: LLM-based escalation detection (with fallback)
    prompt = (
        "Determine if the following customer message requires escalation to a human agent. "
        "Respond with only 'YES' or 'NO'. Escalate if there are legal threats, extreme anger, "
        "repeated unresolved issues, or threats to go public or post on social media.\n\n"
        f"Message: {message}"
    )
    try:
        result = call_llm(
            system_prompt="You are a support escalation assistant.",
            user_message=prompt,
            temperature=0.0,
            max_tokens=5,
        ).strip().upper()
        if "YES" in result:
            return True
    except Exception:
        pass

    return False


# ═══════════════════════════════════════════════════════════════════════════
# Part 3: End-to-End Execution (~30 min)
# ═══════════════════════════════════════════════════════════════════════════

def process_message(message: str) -> dict:
    """
    Process a single customer message through the full workflow.

    This is the main entry point. Build the graph, run the message through
    it, and return the final state.

    Args:
        message: The raw customer message text.

    Returns:
        dict matching SupportState with all fields populated:
            - customer_message (str): the original message
            - intent (str): one of INTENT_CATEGORIES
            - sentiment (str): one of 'positive', 'neutral', 'negative', 'angry'
            - priority (str): one of PRIORITY_LEVELS
            - response (str): customer-facing response (non-empty)
            - escalate (bool): whether to escalate
            - reasoning (str): explanation of the routing decision

    Example:
        result = process_message("I want a refund for order #123")
        assert result["intent"] == "refund"
        assert isinstance(result["response"], str)
        assert len(result["response"]) > 0
    """
    graph = build_graph()
    result = graph.invoke({"customer_message": message})
    return dict(result)
