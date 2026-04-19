import hashlib
import os
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import yaml
from jinja2 import Environment, FileSystemLoader, StrictUndefined

# ---------------------------------------------------------------------------
# Paths & Jinja environment
# ---------------------------------------------------------------------------
_PROMPTS_DIR = Path(__file__).parent
_MANIFEST_PATH = _PROMPTS_DIR / "prompts.yaml"

_jinja_env = Environment(
    loader=FileSystemLoader(str(_PROMPTS_DIR)),
    undefined=StrictUndefined,
    keep_trailing_newline=True,
)

# ---------------------------------------------------------------------------
# Langfuse client (lazy init, graceful degradation)
# ---------------------------------------------------------------------------
_langfuse_client = None
_langfuse_init_attempted = False


def _get_langfuse():
    """Lazily initialise the Langfuse client. Returns None if unavailable."""
    global _langfuse_client, _langfuse_init_attempted
    if _langfuse_init_attempted:
        return _langfuse_client
    _langfuse_init_attempted = True
    try:
        from langfuse import Langfuse

        _langfuse_client = Langfuse(
            secret_key=os.getenv("LANGFUSE_SECRET_KEY", ""),
            public_key=os.getenv(
                "LANGFUSE_PUBLIC_KEY",
                "pk-lf-877c8482-8da4-4f52-8418-5562fa99e356",
            ),
            host=os.getenv("LANGFUSE_HOST", "http://192.168.50.50:3000"),
        )
    except Exception as e:
        print(f"[prompts] Langfuse unavailable: {e}")
    return _langfuse_client


# ---------------------------------------------------------------------------
# Manifest helpers
# ---------------------------------------------------------------------------
def _load_manifest() -> dict:
    if _MANIFEST_PATH.exists():
        with open(_MANIFEST_PATH, "r") as f:
            return yaml.safe_load(f) or {}
    return {"prompts": {}}


def _save_manifest(manifest: dict) -> None:
    with open(_MANIFEST_PATH, "w") as f:
        yaml.dump(manifest, f, default_flow_style=False, sort_keys=False)


def _hash_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


# ---------------------------------------------------------------------------
# PromptResult
# ---------------------------------------------------------------------------
@dataclass
class PromptResult:
    """Returned by get_prompt(). Use .text for the rendered string."""

    text: str
    name: str
    version: int

    def __str__(self) -> str:
        return self.text


# ---------------------------------------------------------------------------
# Core: get_prompt
# ---------------------------------------------------------------------------
def get_prompt(template_name: str, **kwargs: Any) -> PromptResult:
    """Render a prompt template and sync its version to Langfuse.

    On every call:
      1. Hashes the .jinja file and compares to prompts.yaml manifest.
      2. If changed → bumps version, updates manifest, pushes new version to Langfuse.
      3. Renders locally with Jinja2.
      4. Returns a PromptResult with .text, .name, .version.

    Args:
        template_name: Name of the .jinja file without extension.
        **kwargs: Variables to substitute into the template.

    Returns:
        PromptResult with rendered text and version metadata.

    Raises:
        jinja2.UndefinedError: If a required template variable is missing.
        jinja2.TemplateNotFound: If the template file does not exist.
        KeyError: If template_name is not registered in prompts.yaml.
    """
    manifest = _load_manifest()
    prompts = manifest.setdefault("prompts", {})

    if template_name not in prompts:
        raise KeyError(
            f"Prompt '{template_name}' not found in prompts.yaml. "
            f"Available: {list(prompts.keys())}"
        )

    entry = prompts[template_name]
    template_path = _PROMPTS_DIR / entry["file"]
    current_hash = _hash_file(template_path)

    # --- Auto-version on content change ---
    if current_hash != entry.get("content_hash"):
        entry["version"] = entry.get("version", 0) + 1
        entry["content_hash"] = current_hash
        _save_manifest(manifest)

        # Push new version to Langfuse
        lf = _get_langfuse()
        if lf is not None:
            try:
                lf.create_prompt(
                    name=template_name,
                    type="text",
                    prompt=template_path.read_text(encoding="utf-8"),
                    labels=entry.get("labels", []),
                )
                print(
                    f"[prompts] Synced '{template_name}' v{entry['version']} to Langfuse"
                )
            except Exception as e:
                print(f"[prompts] Langfuse sync failed: {e}")

    # --- Render locally ---
    template = _jinja_env.get_template(entry["file"])
    rendered = template.render(**kwargs)

    return PromptResult(
        text=rendered,
        name=template_name,
        version=entry["version"],
    )
