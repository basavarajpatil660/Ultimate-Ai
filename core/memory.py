import json
import os
from datetime import datetime

MEMORY_FILE = "memory.json"

DEFAULT_MEMORY = {
  "last_run": "2024-01-01T00:00:00",
  "run_count_today": 0,
  "provider_stats": {
    "mistral": {"success": 0, "fail": 0},
    "cerebras": {"success": 0, "fail": 0},
    "groq": {"success": 0, "fail": 0}
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

def load_memory():
    default = {
        "last_run": "",
        "run_count_today": 0,
        "provider_stats": {},
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
    try:
        with open("memory.json", "r") as f:
            data = json.load(f)
            # Fill any missing keys with defaults
            for key, value in default.items():
                if key not in data:
                    data[key] = value
            return data
    except Exception:
        return default

def save_memory(data):
    try:
        with open(MEMORY_FILE, 'w') as f:
            json.dump(data, f, indent=2)
    except Exception as e:
        print(f"Failed to save memory: {e}")

def update_budget(provider, amount, budget_type="requests"):
    data = load_memory()
    key = f"{provider}_{budget_type}_used"
    if "budget" not in data:
        data["budget"] = {}
    data["budget"][key] = data["budget"].get(key, 0) + amount
    save_memory(data)

def should_skip_provider(provider):
    data = load_memory()
    if provider in data.get("failed_keys", []):
        return True
    return False

def reset_daily_budget(memory):
    from datetime import datetime
    today = datetime.now().strftime("%Y-%m-%d")
    last_run = memory.get("last_run", "")
    if today not in str(last_run):
        memory["budget"] = {
            "cerebras_tokens_used": 0,
            "groq_requests_used": 0,
            "mistral_tokens_used": 0,
            "tavily_requests_used": 0
        }
        memory["run_count_today"] = 0
        memory["tasks_today"] = []
        print(f"Daily budget reset for {today}")
    memory["last_run"] = datetime.now().isoformat()
    return memory
