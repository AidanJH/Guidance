# Services (packages/guidance-agents/src/services)
Contains the core business logic of the Guidance platform, such as database access, third-party integrations (non-LLM), and domain rules.

**Rules:**
1. Code in this folder must NOT depend on LLMs or Agents.
2. It should be fully testable via standard unit tests.
