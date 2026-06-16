# Prompts (packages/guidance-agents/src/prompts)
Central registry for all LLM prompts used across Guidance.

**Rules:**
1. All prompts must be registered in prompts.yaml.
2. Do not embed massive string prompts inside Python code. Keep them in .jinja files.
3. The __init__.py module handles dynamic syncing and version bumping with Langfuse. Use get_prompt("template_name").
