# Comparison of LongChain and LangGraph for AI Agent Development

## Comparison

| Dimension | LongChain | LangGraph|
|---|---|---|
| Agent Loop | create_agent | stateful workflows |
| Workflow | models, tools, prompt, middleware | deterministic steps, LLM-driven agentic steps |
| State Management | durable execution, human-in-the-loop, persistence | durable execution, streaming, human-in-the-loop, persistence, memory |
| Multi-Agent | subagent-spawning | subagents, complex state transitions |
| Complexity | highly configurable | low-level |
| Best Use Case | use cases requiring a highly customizable harness, application where minimal code changes are preferred | advanced needs combining deterministic and agentic workflows, use cases requiring fine-grained control over agent behavior |

## Recommendation

LongChain is recommended for users seeking a highly configurable and customizable agent harness, particularly when minimal code changes are preferred. LangGraph is recommended for advanced users who need low-level control over agent orchestration and wish to combine deterministic and LLM-driven steps in the same graph.

### Reasons

- LongChain's highly configurable nature makes it suitable for use cases where a minimal code change approach is desired.
- LangGraph's low-level design and fine-grained control make it ideal for users who need to mix deterministic and agentic workflows.

### Caveats

- LongChain requires LangGraph components for underlying orchestration, which could be a limitation for users who want to avoid additional dependencies.
- LangGraph does not abstract prompts or architecture, which may require users to have familiarity with components like models and tools.

## Sources

- longchain.md
- longgraph.md
