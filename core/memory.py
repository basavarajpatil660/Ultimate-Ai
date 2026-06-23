import os
import json
import requests
from datetime import datetime, timezone

# ─────────────────────────────────────────────
#  Cloudflare KV Memory  (replaces memory.json)
#  KV keys used:
#    agent_state      → provider stats, run counts, budget
#    conversation     → last 20 messages with timestamps
#    user_profile     → Nick's personal context (static)
# ─────────────────────────────────────────────

WORKER_URL = os.environ.get("CLOUDFLARE_WORKER_URL", "").rstrip("/")
API_KEY    = os.environ.get("DASHBOARD_API_KEY", "")

HEADERS = {
    "Content-Type": "application/json",
    "X-API-Key": API_KEY
}

# How long (seconds) conversation context stays active
CONTEXT_WINDOW_SECONDS = 300  # 5 minutes

# Nick's permanent user profile — safe to store in KV (private)
USER_PROFILE = {
    "name": "Nick (Basavaraj M Patil)",
    "location": "Hubballi, Karnataka, India",
    "style": "casual, calls people 'brother', sends voice messages, direct",
    "language": "English (Hinglish accent)",
    "projects": [
        "Ultimate AI Agent (Cloudflare + GitHub Actions)",
        "Barnor — Shopify dropshipping (barnor.in)",
        "NickPlays — gaming YouTube channel"
    ],
    "expertise": "self-taught developer, mobile-only workflow, vibe coding with AI",
    "preferences": "complete files not diffs, free APIs only, no credit cards",
    "tools": "Antigravity (Gemini vibe coder), Cloudflare Workers, GitHub Actions",
    "note": "Works entirely on mobile. Gets frustrated when errors repeat. Pushes back on hallucinations."
}

# ─── Low-level KV helpers ───────────────────

def _kv_get(key: str) -> dict | list | None:
    """Read a value from KV via the Worker /api/kv endpoint."""
    try:
        resp = requests.get(
            f"{WORKER_URL}/api/kv",
            headers=HEADERS,
            params={"key": key},
            timeout=10
        )
        if resp.status_code == 200:
            data = resp.json()
            return data.get("value")
        return None
    except Exception:
        return None

def _kv_set(key: str, value: dict | list) -> bool:
    """Write a value to KV via the Worker /api/kv endpoint."""
    try:
        resp = requests.post(
            f"{WORKER_URL}/api/kv",
            headers=HEADERS,
            json={"key": key, "value": value},
            timeout=10
        )
        return resp.status_code == 200
    except Exception:
        return False

# ─── Agent State (replaces memory.json fields) ──

def load_state() -> dict:
    """Load agent state from KV. Falls back to clean default."""
    state = _kv_get("agent_state")
    if state:
        return state
    return {
        "last_run": None,
        "run_count_today": 0,
        "provider_stats": {
            "mistral":   {"success": 0, "fail": 0},
            "cerebras":  {"success": 0, "fail": 0},
            "groq":      {"success": 0, "fail": 0},
            "openrouter":{"success": 0, "fail": 0},
            "google":    {"success": 0, "fail": 0}
        },
        "failed_keys": [],
        "budget": {
            "cerebras_tokens_used": 0,
            "groq_requests_used": 0,
            "mistral_tokens_used": 0,
            "tavily_requests_used": 0
        },
        "last_content_idea": "",
        "last_image_prompt": ""
    }

def save_state(state: dict) -> bool:
    """Save agent state to KV."""
    state["last_run"] = datetime.now(timezone.utc).isoformat()
    return _kv_set("agent_state", state)

def record_task(state: dict, prompt: str, task_type: str, provider: str) -> dict:
    """Add a task entry to state (kept for stats, not conversation)."""
    if "tasks_today" not in state:
        state["tasks_today"] = []
    state["tasks_today"].append({
        "prompt": prompt[:200],  # truncate for storage
        "type": task_type,
        "provider": provider,
        "time": datetime.now(timezone.utc).isoformat()
    })
    # Keep only last 20 tasks
    state["tasks_today"] = state["tasks_today"][-20:]
    return state

# ─── Conversation Memory (5-min context window) ──

def save_message(role: str, content: str) -> bool:
    """
    Save a message to conversation history in KV.
    role: 'user' or 'assistant'
    """
    history = _kv_get("conversation") or []
    history.append({
        "role": role,
        "content": content[:1000],  # cap per message
        "timestamp": datetime.now(timezone.utc).isoformat()
    })
    # Keep last 20 messages max
    history = history[-20:]
    return _kv_set("conversation", history)

def get_recent_context(window_seconds: int = CONTEXT_WINDOW_SECONDS) -> list[dict]:
    """
    Return messages from the last `window_seconds` seconds.
    Returns list of {"role": ..., "content": ...} — ready for LLM injection.
    """
    history = _kv_get("conversation") or []
    now = datetime.now(timezone.utc)
    recent = []
    for msg in history:
        try:
            ts = datetime.fromisoformat(msg["timestamp"])
            # make timezone-aware if naive
            if ts.tzinfo is None:
                ts = ts.replace(tzinfo=timezone.utc)
            age = (now - ts).total_seconds()
            if age <= window_seconds:
                recent.append({
                    "role": msg["role"],
                    "content": msg["content"]
                })
        except Exception:
            continue
    return recent

def clear_conversation() -> bool:
    """Clear all conversation history (e.g. on /start command)."""
    return _kv_set("conversation", [])

# ─── User Profile ────────────────────────────

def get_user_profile() -> dict:
    """
    Get Nick's profile from KV.
    First run: pushes the default USER_PROFILE to KV.
    """
    profile = _kv_get("user_profile")
    if not profile:
        _kv_set("user_profile", USER_PROFILE)
        return USER_PROFILE
    return profile

def build_system_prompt_context() -> str:
    """
    Build a context string to prepend to every LLM system prompt.
    Includes user profile + recent conversation history.
    """
    profile = get_user_profile()
    recent  = get_recent_context()

    lines = [
        "=== USER CONTEXT ===",
        f"You are talking to {profile.get('name', 'Nick')}.",
        f"Style: {profile.get('style', '')}",
        f"Language: {profile.get('language', 'English')}",
        f"Active projects: {', '.join(profile.get('projects', []))}",
        f"Note: {profile.get('note', '')}",
        ""
    ]

    if recent:
        lines.append("=== RECENT CONVERSATION (last 5 min) ===")
        for msg in recent:
            tag = "Nick" if msg["role"] == "user" else "You (AI)"
            lines.append(f"{tag}: {msg['content']}")
        lines.append("")

    lines.append("=== YOUR TASK ===")
    return "\n".join(lines)

# ─── Backwards-compatible wrappers (for main.py) ─────────────
# These match the old function names so main.py needs zero changes.

def load_memory() -> dict:
    """Old name → load_state()"""
    return load_state()

def save_memory(state: dict) -> bool:
    """Old name → save_state()"""
    return save_state(state)

def reset_daily_budget(state: dict) -> dict:
    """
    Resets daily counters if last_run was a different day.
    Keeps provider_stats cumulative, resets tasks_today.
    """
    now = datetime.now(timezone.utc)
    last = state.get("last_run")
    if last:
        try:
            last_dt = datetime.fromisoformat(last)
            if last_dt.tzinfo is None:
                last_dt = last_dt.replace(tzinfo=timezone.utc)
            if last_dt.date() < now.date():
                state["run_count_today"] = 0
                state["tasks_today"] = []
                state["budget"] = {
                    "cerebras_tokens_used": 0,
                    "groq_requests_used": 0,
                    "mistral_tokens_used": 0,
                    "tavily_requests_used": 0
                }
        except Exception:
            pass
    return state

def update_budget(provider: str, amount: int) -> None:
    """Update token/request budget for a provider in KV."""
    state = load_state()
    budget = state.get("budget", {})
    key_map = {
        "mistral":  "mistral_tokens_used",
        "cerebras": "cerebras_tokens_used",
        "groq":     "groq_requests_used",
        "tavily":   "tavily_requests_used"
    }
    k = key_map.get(provider)
    if k:
        budget[k] = budget.get(k, 0) + amount
        state["budget"] = budget
        save_state(state)
