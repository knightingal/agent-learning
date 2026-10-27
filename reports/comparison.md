# Comparison of LongChain and LangGraph for Program

## Comparison

| Dimension | LangGraph | LangChain|
|---|---|---|
| Agent Loop | deterministic steps, LLM-driven agentic steps | model + harness, prompt, tools, middleware |
| Workflow | long-running, stateful | agent, use case-specific |
| State Management | short-term working memory, long-term memory | short-term working memory, long-term memory |
| Multi-Agent | subagents | subagents |
| Complexity | low-level | high-level |
| Best Use Case | complex tasks, deterministic steps, agentic steps | highly customizable harness, agent composition, use case-specific |

## Recommendation

LangGraph is better suited for low-level orchestration with fine-grained control over agent workflows, while LangChain offers a higher-level abstraction for building customizable agents that leverage LangGraph's capabilities.

### Reasons

- LangGraph's low-level nature allows more precise control over execution flow
- LangChain's high-level approach simplifies agent creation but abstracts away some details

### Caveats

- Evidence gap: The comparison only covers the specified dimensions and does not include performance metrics or scalability comparisons
- Evidence gap: No information provided about specific implementation details or integration complexity

## Sources

- longchain.md
- longgraph.md
