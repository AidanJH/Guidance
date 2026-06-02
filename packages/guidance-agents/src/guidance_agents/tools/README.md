# Tools (packages/guidance-agents/src/tools)
Contains JSON schemas and thin Python wrappers for the LLM to call. 

**Rules:**
1. Functions in this folder should ONLY format inputs and handle LLM-specific data formatting.
2. The actual business logic (e.g. database transactions) must be imported from services/.
3. Tools here must include clean docstrings and type hints, as these form the definition sent to the LLM.
