"""
Smoke tests — PROVIDED to candidates.

These verify your graph compiles and your functions return the correct types.
Run with: pytest tests/test_smoke.py -v

Note: Tests that call the LLM require a valid OPENROUTER_API_KEY in .env.
"""
import sys
import os
import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))


class TestPart1GraphArchitecture:
    """Part 1: Graph builds and compiles."""

    def test_build_graph_returns_compiled_graph(self):
        """build_graph() returns a compiled graph with an invoke method."""
        from workflow import build_graph

        graph = build_graph()
        assert graph is not None
        assert callable(getattr(graph, "invoke", None)), (
            "build_graph() must return a compiled graph with an invoke method"
        )

    def test_graph_has_nodes(self):
        """Graph has at least 2 nodes."""
        from workflow import build_graph

        graph = build_graph()
        nodes = graph.get_graph().nodes
        assert len(nodes) >= 2, (
            f"Graph should have at least 2 nodes, found {len(nodes)}"
        )

    def test_graph_has_edges(self):
        """Graph has at least 1 edge."""
        from workflow import build_graph

        graph = build_graph()
        edges = graph.get_graph().edges
        assert len(edges) >= 1, "Graph must have at least 1 edge"


class TestPart2Classification:
    """Part 2: Intent classification and escalation."""

    def test_classify_intent_returns_string(self):
        """classify_intent() returns a string."""
        from workflow import classify_intent

        result = classify_intent("I want a refund for my broken headphones")
        assert isinstance(result, str)

    def test_classify_intent_returns_valid_category(self):
        """classify_intent() returns one of INTENT_CATEGORIES."""
        from workflow import classify_intent
        from config import INTENT_CATEGORIES

        result = classify_intent("I want a refund for my broken headphones")
        assert result in INTENT_CATEGORIES, (
            f"classify_intent must return one of {INTENT_CATEGORIES}, "
            f"got '{result}'"
        )

    def test_should_escalate_returns_bool(self):
        """should_escalate() returns a boolean."""
        from workflow import should_escalate

        state = {
            "customer_message": "This is fine, just a quick question.",
            "intent": "general",
            "sentiment": "neutral",
            "priority": "low",
        }
        result = should_escalate(state)
        assert isinstance(result, bool)


class TestPart3EndToEnd:
    """Part 3: Full workflow execution."""

    def test_process_message_returns_dict(self):
        """process_message() returns a dict."""
        from workflow import process_message

        result = process_message("Where is my order #12345?")
        assert isinstance(result, dict)

    def test_process_message_has_required_keys(self):
        """process_message() returns all required SupportState keys."""
        from workflow import process_message

        result = process_message("Where is my order #12345?")
        required_keys = {
            "customer_message", "intent", "sentiment",
            "priority", "response", "escalate", "reasoning",
        }
        assert required_keys.issubset(result.keys()), (
            f"Missing keys: {required_keys - result.keys()}"
        )

    def test_process_message_response_nonempty(self):
        """Response is a substantive customer-facing message."""
        from workflow import process_message

        result = process_message("Where is my order #12345?")
        assert isinstance(result["response"], str)
        assert len(result["response"]) > 20, (
            "Response should be a substantive customer-facing message"
        )

    def test_process_message_valid_intent(self):
        """Intent is one of the valid categories."""
        from workflow import process_message
        from config import INTENT_CATEGORIES

        result = process_message("I want a refund")
        assert result["intent"] in INTENT_CATEGORIES

    def test_process_message_escalate_is_bool(self):
        """Escalate field is a boolean."""
        from workflow import process_message

        result = process_message("I want a refund")
        assert isinstance(result["escalate"], bool)
