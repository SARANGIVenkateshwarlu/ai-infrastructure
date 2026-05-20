"""
Customer Support Workflow — State Schema (PROVIDED, do not modify).

This TypedDict defines the shape of data flowing through your LangGraph workflow.
Each node in your graph reads from and writes to this state.
"""
from typing import TypedDict


class SupportState(TypedDict):
    """State object passed through every node in the support workflow.

    Fields:
        customer_message: The raw customer message to process.
        intent: Classified intent category (set by your classifier node).
            Must be one of: 'refund', 'shipping', 'product_inquiry',
            'complaint', 'general'.
        sentiment: Detected sentiment. One of: 'positive', 'neutral',
            'negative', 'angry'.
        priority: Determined priority level. One of: 'low', 'medium',
            'high', 'urgent'.
        response: The generated customer-facing response text.
        escalate: Whether this ticket should be escalated to a human agent.
        reasoning: Brief explanation of why this routing/escalation decision
            was made (useful for auditing).
    """
    customer_message: str
    intent: str
    sentiment: str
    priority: str
    response: str
    escalate: bool
    reasoning: str
