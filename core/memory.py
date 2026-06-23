import os
import json
import requests
from datetime import datetime, timezone

# ─────────────────────────────────────────────
#  Cloudflare KV Memory  (replaces memory.json)
#  KV keys: agent_state | conversation | user_profile
# ─────────────────────────────────────────────

CONTEXT_WINDOW_SECONDS = 300  # 5 minutes

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

# In-memory fallback when KV is unavailable
_LOCAL_STATE = {}
_LOCAL_CONVERSATION = []

# ─── Low-level KV helpers ───────────────────

def _get_headers():
    """Build headers fresh each call — reads env at call time, not import time."""
    return {
        "Content-Type": "application/json",
        "X-Dashboard-Key": os.environ.get("DASHBOARD_API_KEY", "")  # matches Worker auth
    }

def _get_worker_url():
    return os.environ.get("CLOUDFLARE_WORKER_URL", "").rstrip("/").replace("/generate", "")

def _kv_get(key: str):
    """Read from KV. Returns parsed value or None. Never raises."""
    global _LOCAL_STATE, _LOCAL_CONVERSATION
    try:
        worker_url = _get_worker_url()
        if not worker_url:
            return _LOCAL_STATE if key == "agent_state" else (_LOCAL_CONVERSATION if key == "conversation" else None)
        resp = requests.get(
            f"{worker_url}/api/kv",
            headers=_get_headers(),
            params={"key": key},
            timeout=8
        )
        if resp.status_code == 200:
            data = resp.json()
            return data.get("value")
        print(f"KV get [{key}] status {resp.status_code} — using local fallback")
        return None
    except Exception as e:
        print(f"KV get [{key}] failed: {e} — using local fallback")
        return None

def _kv_set(key: str, value) -> bool:
    """Write to KV. Returns True on success. Never raises."""
    global _LOCAL_STATE, _LOCAL_CONVERSATION
    # Always update local cache
    if key == "agent_state":
        _LOCAL_STATE = value
    elif key == "conversation":
        _LOCAL_CONVERSATION = value
    try:
        worker_url = _get_worker_url()
        if not worker_url:
            return True  # local-only mode
        resp = requests.post(
            f"{worker_url}/api/kv",
            headers=_get_headers(),
            json={"key": key, "value": value},
            timeout=8
        )
        if resp.status_code == 200:
            return True
        print(f"KV set [{key}] status {resp.status_code} — saved locally only")
        return False
    except Exception as e:
        print(f"KV set [{key}] failed: {e} — saved locally only")
        return False

# ─── Agent State ─────────────────────────────

def load_state() -> dict:
    state = _kv_get("agent_state")
    if state and isinstance(state, dict):
        return state
    return {
        "last_run": None,
        "run_count_today": 0,
        "provider_stats": {
            "mistral":    {"success": 0, "fail": 0},
            "cerebras":   {"success": 0, "fail": 0},
            "groq":       {"success": 0, "fail": 0},
            "openrouter": {"success": 0, "fail": 0},
            "google":     {"success": 0, "fail": 0}
        },
        "failed_keys": [],
        "tasks_today": [],
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
    state["last_run"] = datetime.now(timezone.utc).isoformat()
    return _kv_set("agent_state", state)

# ─── Conversation Memory ──────────────────────

def save_message(role: str, content: str) -> bool:
    history = _kv_get("conversation") or []
    if not isinstance(history, list):
        history = []
    history.append({
        "role": role,
        "content": str(content)[:1000],
        "timestamp": datetime.now(timezone.utc).isoformat()
    })
    history = history[-20:]
    return _kv_set("conversation", history)

def get_recent_context(window_seconds: int = CONTEXT_WINDOW_SECONDS) -> list:
    history = _kv_get("conversation") or []
    if not isinstance(history, list):
        return []
    now = datetime.now(timezone.utc)
    recent = []
    for msg in history:
        try:
            ts = datetime.fromisoformat(msg["timestamp"])
            if ts.tzinfo is None:
                ts = ts.replace(tzinfo=timezone.utc)
            if (now - ts).total_seconds() <= window_seconds:
                recent.append({"role": msg["role"], "content": msg["content"]})
        except Exception:
            continue
    return recent

def clear_conversation() -> bool:
    return _kv_set("conversation", [])

# ─── User Profile ─────────────────────────────

def get_user_profile() -> dict:
    profile = _kv_get("user_profile")
    if not profile:
        _kv_set("user_profile", USER_PROFILE)
        return USER_PROFILE
    return profile

def build_system_prompt_context() -> str:
    try:
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
    except Exception as e:
        print(f"build_system_prompt_context failed: {e}")
        return ""  # never crash the LLM call

# ─── Backwards-compatible wrappers (main.py uses these) ──────

def load_memory() -> dict:
    return load_state()

def save_memory(state: dict) -> bool:
    return save_state(state)

def reset_daily_budget(state: dict) -> dict:
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
    try:
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
    except Exception as e:
        print(f"update_budget failed: {e}")
