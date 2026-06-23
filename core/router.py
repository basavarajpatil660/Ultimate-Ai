import os
import requests

VALID_LABELS = [
    "FACTUAL", "REALTIME", "CREATIVE", "CODE", "REASONING",
    "IMAGE_GEN", "IMAGE_READ", "SUMMARIZE", "TRANSLATE",
    "VOICE_OUT", "RESEARCH", "CONTENT"
]

SYSTEM_PROMPT = """You are a task classifier.
Return ONLY ONE of these exact labels, nothing else:
FACTUAL, REALTIME, CREATIVE, CODE, REASONING, IMAGE_GEN, IMAGE_READ, SUMMARIZE, TRANSLATE, VOICE_OUT, RESEARCH, CONTENT"""


def detect_language(prompt):
    hindi_hinglish_keywords = [
        'kya', 'hai', 'kaise', 'karo', 'banao', 'mujhe',
        'nahi', 'aur', 'hain', 'mein', 'liye', 'bhai'
    ]
    words = prompt.lower().split()
    match_count = sum(1 for w in words if w in hindi_hinglish_keywords)
    if match_count >= 2:
        return "hindi/hinglish"
    return "english"


def _heuristic_classify(prompt_lower):
    """Fast keyword-based fallback — no API needed."""
    if any(w in prompt_lower for w in ['image', 'generate image', 'create image', 'draw', 'picture of']):
        return "IMAGE_GEN"
    if any(w in prompt_lower for w in ['latest', 'news', 'today', 'current', 'trending', 'right now']):
        return "REALTIME"
    if any(w in prompt_lower for w in ['search', 'research', 'find out', 'look up']):
        return "RESEARCH"
    if any(w in prompt_lower for w in ['code', 'function', 'debug', 'error', 'script', 'program']):
        return "CODE"
    if any(w in prompt_lower for w in ['translate', 'in spanish', 'in hindi', 'in french']):
        return "TRANSLATE"
    if any(w in prompt_lower for w in ['summarize', 'summary', 'tldr', 'brief']):
        return "SUMMARIZE"
    if any(w in prompt_lower for w in ['write', 'story', 'poem', 'caption', 'post', 'creative']):
        return "CREATIVE"
    if any(w in prompt_lower for w in ['voice', 'speak', 'say this', 'audio']):
        return "VOICE_OUT"
    return "FACTUAL"


def _try_classify_api(api_key, endpoint, model, prompt_text):
    """Try one LLM provider for classification. Returns label or None."""
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    data = {
        "model": model,
        "messages": [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": f"Classify this prompt: {prompt_text[:500]}"}
        ],
        "temperature": 0.0,
        "max_tokens": 10
    }
    try:
        resp = requests.post(endpoint, headers=headers, json=data, timeout=8)
        if resp.status_code == 200:
            label = resp.json()['choices'][0]['message']['content'].strip().upper()
            for v in VALID_LABELS:
                if v in label:
                    return v
    except Exception as e:
        print(f"Router [{model}] failed: {e}")
    return None


def classify_task(prompt, has_image=False):
    prompt_lower = prompt.lower()

    # Image handling — no API needed
    if has_image:
        if not prompt.strip():
            return "IMAGE_READ"
        if any(w in prompt_lower for w in ['generate', 'create', 'make', 'draw']):
            return "IMAGE_GEN"
        return "IMAGE_READ"

    if not prompt.strip():
        return "CONTENT"

    # Mode shortcuts from prompt prefix — instant, no API
    if prompt_lower.startswith('/image'):
        return "IMAGE_GEN"
    if prompt_lower.startswith('/voice'):
        return "VOICE_OUT"
    if prompt_lower.startswith('/research'):
        return "RESEARCH"
    if prompt_lower.startswith('/content'):
        return "CONTENT"

    # Try providers in order — short 8s timeout each
    providers = [
        {
            "key": os.environ.get("CEREBRAS_API_KEY"),
            "endpoint": "https://api.cerebras.ai/v1/chat/completions",
            "model": "llama-3.3-70b"
        },
        {
            "key": os.environ.get("GROQ_API_KEY"),
            "endpoint": "https://api.groq.com/openai/v1/chat/completions",
            "model": "llama-3.3-70b-versatile"
        },
        {
            "key": os.environ.get("MISTRAL_API_KEY"),
            "endpoint": "https://api.mistral.ai/v1/chat/completions",
            "model": "mistral-large-latest"
        },
    ]

    for p in providers:
        if not p["key"]:
            continue
        label = _try_classify_api(p["key"], p["endpoint"], p["model"], prompt)
        if label:
            return label

    # All APIs failed — use fast heuristic
    print("Router: all APIs failed, using heuristic")
    return _heuristic_classify(prompt_lower)
