# 🚀 Quick Reference: Pure AI Supreme Router

## TL;DR

The `manage_request` node is a **pure AI-driven router** that intelligently routes all user requests to the appropriate flow using LLM reasoning (no keywords!).

## Three Flows

1. **add_card_flow** - Register new credit cards
2. **recommendation_flow** - Analyze transactions and recommend cards
3. **general_flow** - Handle general conversation

## How It Works

```python
User Message → LLM analyzes with full project context → Routes to best flow
```

## Key Files

| File | Purpose |
|------|---------|
| `app/graph/nodes.py` | Contains `manage_request_node` and system prompt |
| `app/graph/graph.py` | Graph structure with routing logic |
| `app/graph/state.py` | State definition with `flow_decision` |

## Testing

```bash
# Run CLI
python main_cli.py

# Test inputs
You: /add_card HDFC Regalia Gold Card
You: I'm spending 5000 on Amazon
You: What's a good credit score?
```

## Adding a New Flow

1. Update `GraphState` in `app/graph/state.py`:
```python
flow_decision: Literal["add_card_flow", "recommendation_flow", "general_flow", "new_flow"]
```

2. Update `MANAGE_REQUEST_SYSTEM_PROMPT` in `app/graph/nodes.py`:
```python
### Flow 4: NEW_FLOW
**Purpose**: What it does
**Route here when**: Scenarios
**Examples**: Real examples
```

3. Add routing in `app/graph/graph.py`:
```python
builder.add_conditional_edges(
    "manage_request",
    flow_decision_selector,
    {
        "add_card_flow": "card_parser",
        "recommendation_flow": "transaction_parser",
        "general_flow": "memory_retrieval_general",
        "new_flow": "new_node"  # Add this
    }
)
```

## Debugging

```python
# In manage_request_node, check logs:
print(f"🎯 Supreme Router Decision: {flow_decision}")
print(f"📝 User Request: {last_message[:100]}...")
```

## Key Principles

✅ **DO:**
- Let LLM reason about intent
- Update system prompt for new flows
- Trust the AI's decision
- Log routing decisions

❌ **DON'T:**
- Add keyword matching
- Use pattern matching
- Hardcode routing rules
- Override LLM decisions

## Architecture

```
profiler → manage_request → [add_card | recommendation | general] → END
```

## Benefits

- 🧠 Pure AI intelligence
- 🔧 Zero maintenance (no keywords)
- 📈 Improves with better models
- 🎯 Context-aware routing
- 🚀 Easy to extend

## Documentation

- `ARCHITECTURE.md` - Complete architecture
- `FLOW_DIAGRAM.md` - Visual flow diagrams
- `SUPREME_ROUTER_VISUAL.md` - Visual architecture
- `DEVELOPER_GUIDE.md` - Detailed developer guide
- `IMPLEMENTATION_SUMMARY.md` - What was built

---

**Quick, smart, and pure AI** 🧠⚡
