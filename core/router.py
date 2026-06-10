import os
import requests

def detect_language(prompt):
    # Basic heuristic for Hindi/Hinglish detection
    hindi_hinglish_keywords = ['kya', 'hai', 'kaise', 'karo', 'banao', 'mujhe', 'nahi', 'aur', 'hain', 'mein', 'liye', 'bhai']
    words = prompt.lower().split()
    match_count = sum(1 for w in words if w in hindi_hinglish_keywords)
    if match_count >= 2:
        return "hindi/hinglish"
    return "english"

def classify_task(prompt, has_image=False):
    prompt_lower = prompt.lower()
    
    if has_image:
        if not prompt.strip():
            return "IMAGE_READ"
        if any(word in prompt_lower for word in ['generate', 'create', 'make', 'draw']):
            return "IMAGE_GEN"
        return "IMAGE_READ"
        
    if not prompt.strip():
        return "CONTENT"

    # Use Mistral to classify
    api_key = os.environ.get("MISTRAL_API_KEY", None)
    if not api_key:
        # Fallback heuristic
        if 'news' in prompt_lower or 'briefing' in prompt_lower:
            return "CONTENT"
        return "FACTUAL"

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    
    truncated_prompt = prompt[:4000]
    
    system_prompt = """You are a task classifier.
Return ONLY ONE of these exact labels, nothing else:
FACTUAL, REALTIME, CREATIVE, CODE, REASONING, IMAGE_GEN, IMAGE_READ, SUMMARIZE, TRANSLATE, VOICE_OUT, RESEARCH, CONTENT"""
    
    data = {
        "model": "mistral-large-latest",
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": f"Classify this prompt: {truncated_prompt}"}
        ],
        "temperature": 0.0,
        "max_tokens": 10
    }
    
    try:
        response = requests.post("https://api.mistral.ai/v1/chat/completions", headers=headers, json=data, timeout=30)
        if response.status_code == 200:
            label = response.json()['choices'][0]['message']['content'].strip()
            valid_labels = ["FACTUAL", "REALTIME", "CREATIVE", "CODE", "REASONING", "IMAGE_GEN", "IMAGE_READ", "SUMMARIZE", "TRANSLATE", "VOICE_OUT", "RESEARCH", "CONTENT"]
            for v in valid_labels:
                if v in label.upper():
                    return v
    except Exception:
        pass
        
    return "FACTUAL"
