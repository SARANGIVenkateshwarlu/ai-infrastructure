# Master Document — AI Infrastructure Coding Test
## Customer Support Workflow (LangGraph)

**Date:** 2026-05-20  
**Project:** `ai-infrastructure`  
**Objective:** Build an AI-powered support workflow that classifies, routes, and drafts responses to customer messages using LangGraph.

---

## Table of Contents

1. [Project Overview](#1-project-overview)
2. [Provided Files (Read-Only)](#2-provided-files-read-only)
3. [Implementation Tasks](#3-implementation-tasks)
   - Part 1: Graph Architecture
   - Part 2: Node Implementation
   - Part 3: End-to-End Execution
4. [Graph Design](#4-graph-design)
5. [Helper Functions](#5-helper-functions)
6. [Node Functions](#6-node-functions)
7. [Conditional Routing](#7-conditional-routing)
8. [Fallback Strategy](#8-fallback-strategy)
9. [Test Results](#9-test-results)
10. [Files Modified](#10-files-modified)

---

## 1. Project Overview

The company handles 500+ tickets/day across refunds, shipping, product questions, and complaints. The solution is a **LangGraph StateGraph** that:

- Classifies incoming messages into 5 intent categories
- Detects sentiment and assigns priority
- Determines if human escalation is required
- Generates empathetic, context-aware responses
- Routes escalated tickets to human agents

---

## 2. Provided Files (Read-Only)

| File | Purpose |
|------|---------|
| `src/state.py` | `SupportState` TypedDict — the graph's state schema |
| `src/config.py` | `INTENT_CATEGORIES`, `PRIORITY_LEVELS`, `ESCALATION_SIGNALS`, `SAMPLE_MESSAGES` |
| `src/llm.py` | `call_llm()` helper — calls OpenRouter free models with retry logic |
| `tests/test_smoke.py` | 11 smoke tests verifying graph structure, types, and end-to-end shape |

---

## 3. Implementation Tasks

### Part 1: Graph Architecture (`build_graph`)

**Goal:** Build and return a compiled LangGraph `StateGraph` using `SupportState`.

**Requirements Met:**
- Uses `SupportState` as the state schema
- Contains **4 nodes** (≥2 required)
- Contains **conditional edges** for routing
- Compiles successfully via `.compile()`

**Graph Structure:**
```
START → classify → escalation_check ─┬─[auto_respond]──→ END
                                     └─[human_handoff]─→ END
```

### Part 2: Node Implementation

#### `classify_intent(message: str) -> str`
- Uses LLM with zero-temperature prompt for deterministic classification
- Parses response and validates against `INTENT_CATEGORIES`
- **Fallback:** keyword-based heuristic when LLM is unavailable

#### `should_escalate(state: dict) -> bool`
- Multi-layer logic: rule-based signals + LLM confirmation
- Rules checked in order:
  1. Explicit `ESCALATION_SIGNALS` match (legal threats, "social media", etc.)
  2. `angry` sentiment + `complaint` intent
  3. `urgent` priority + `complaint` intent
  4. LLM yes/no check (with fallback on failure)

### Part 3: End-to-End Execution (`process_message`)
- Builds the graph once, invokes it with `{"customer_message": message}`
- Returns a plain `dict` with all `SupportState` fields populated

---

## 4. Graph Design

### Nodes

| Node Name | Function | Purpose |
|-----------|----------|---------|
| `classify` | `_classify_node` | Classifies intent, detects sentiment, assigns priority, writes reasoning |
| `escalation_check` | `_escalation_node` | Calls `should_escalate()` and sets the `escalate` flag |
| `auto_respond` | `_auto_respond_node` | Generates an automated customer-facing response |
| `human_handoff` | `_human_handoff_node` | Generates a handoff message when escalation is true |

### Edges

| From | To | Type | Condition |
|------|-----|------|-----------|
| `START` | `classify` | direct | — |
| `classify` | `escalation_check` | direct | — |
| `escalation_check` | `auto_respond` | conditional | `escalate == False` |
| `escalation_check` | `human_handoff` | conditional | `escalate == True` |
| `auto_respond` | `END` | direct | — |
| `human_handoff` | `END` | direct | — |

---

## 5. Helper Functions

### `_analyze_sentiment(message: str) -> str`
- **Primary:** LLM call with a strict one-word instruction (`positive`, `neutral`, `negative`, `angry`)
- **Fallback:** Keyword lists for angry → negative → positive → neutral

### `_assign_priority(intent: str, sentiment: str) -> str`
| Intent | Sentiment | Priority |
|--------|-----------|----------|
| complaint | angry / negative | `urgent` |
| refund | angry / negative | `high` |
| complaint | any | `high` |
| refund | any | `medium` |
| shipping | any | `medium` |
| product_inquiry | any | `low` |
| general | positive | `low` |
| default | — | `medium` |

### `_generate_response(state: SupportState) -> str`
- **Primary:** LLM prompt tailored to `escalate` flag and intent/sentiment context
- **Fallback:** Pre-written templates per intent + a generic escalation handoff message
- Guarantees substantive output (>20 chars) even without API access

---

## 6. Node Functions

### `_classify_node(state)`
```python
intent      = classify_intent(message)
sentiment   = _analyze_sentiment(message)
priority    = _assign_priority(intent, sentiment)
reasoning   = f"Message classified as '{intent}' with '{sentiment}' sentiment and assigned '{priority}' priority."
return {"intent": intent, "sentiment": sentiment, "priority": priority, "reasoning": reasoning}
```

### `_escalation_node(state)`
```python
escalate = should_escalate(state)
return {"escalate": escalate}
```

### `_auto_respond_node(state)` & `_human_handoff_node(state)`
Both call `_generate_response(state)`, which internally branches on the `escalate` flag to produce the correct tone.

---

## 7. Conditional Routing

```python
def _route_escalation(state: SupportState) -> str:
    if state["escalate"]:
        return "human_handoff"
    return "auto_respond"
```

Registered in the graph builder as:
```python
builder.add_conditional_edges(
    "escalation_check",
    _route_escalation,
    {
        "auto_respond": "auto_respond",
        "human_handoff": "human_handoff",
    },
)
```

---

## 8. Fallback Strategy

Because the smoke tests run without a guaranteed API key, every LLM-dependent function has a deterministic fallback:

| Function | Fallback Behavior |
|----------|-------------------|
| `classify_intent` | Keyword matching on `refund`, `shipping`, `product_inquiry`, `complaint`, `general` terms |
| `_analyze_sentiment` | Keyword lists for angry/negative/positive/neutral |
| `_generate_response` | Intent-specific template strings + escalation handoff template |
| `should_escalate` | Rule-based signals + sentiment/intent/priority heuristics |

This ensures the workflow is **robust** and **testable** in any environment.

---

## 9. Test Results

```bash
pytest tests/test_smoke.py -v
```

| Test | Status |
|------|--------|
| `test_build_graph_returns_compiled_graph` | ✅ PASSED |
| `test_graph_has_nodes` | ✅ PASSED |
| `test_graph_has_edges` | ✅ PASSED |
| `test_classify_intent_returns_string` | ✅ PASSED |
| `test_classify_intent_returns_valid_category` | ✅ PASSED |
| `test_should_escalate_returns_bool` | ✅ PASSED |
| `test_process_message_returns_dict` | ✅ PASSED |
| `test_process_message_has_required_keys` | ✅ PASSED |
| `test_process_message_response_nonempty` | ✅ PASSED |
| `test_process_message_valid_intent` | ✅ PASSED |
| `test_process_message_escalate_is_bool` | ✅ PASSED |

**Result:** `11 passed, 2 warnings in 0.60s`

---

## 10. Files Modified

| File | Action | Notes |
|------|--------|-------|
| `src/workflow.py` | **Implemented** | Added helpers, nodes, and 4 required functions without changing original order or signatures |
| `master.md` | **Created** | This document |

---

## Appendix: Sample Execution (Conceptual)

**Input:** `"I want a full refund for order #33012. The headphones are broken."`

**Flow:**
1. `classify` → intent=`refund`, sentiment=`negative`, priority=`high`
2. `escalation_check` → escalate=`False` (no legal threats, not angry enough)
3. `auto_respond` → empathetic refund acknowledgment response
4. `END`

**Output:**
```json
{
  "customer_message": "I want a full refund for order #33012...",
  "intent": "refund",
  "sentiment": "negative",
  "priority": "high",
  "response": "Thank you for reaching out...",
  "escalate": false,
  "reasoning": "Message classified as 'refund' with 'negative' sentiment and assigned 'high' priority."
}
```

---

*End of Master Document*
