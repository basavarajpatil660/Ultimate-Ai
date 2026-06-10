import os
import requests
from core.fallback import call_with_fallback, ProviderError

def text_to_speech(text):
    provider_chain = [
        {
            'provider_name': 'elevenlabs',
            'api_key': os.environ.get("ELEVENLABS_API_KEY"),
            'model': 'eleven_multilingual_v2',
            'max_retries': 2,
            'backoff_seconds': [2, 4]
        },
        {
            'provider_name': 'google_tts',
            'api_key': os.environ.get("GOOGLE_AI_KEY"),
            'model': 'tts',
            'max_retries': 2,
            'backoff_seconds': [2, 4]
        }
    ]
    
    def tts_call_func(provider):
        name = provider['provider_name']
        api_key = provider['api_key']
        
        if name == 'elevenlabs':
            voice_id = "21m00Tcm4TlvDq8ikWAM" # Rachel
            url = f"https://api.elevenlabs.io/v1/text-to-speech/{voice_id}"
            headers = {
                "xi-api-key": api_key,
                "Content-Type": "application/json"
            }
            data = {
                "text": text,
                "model_id": "eleven_multilingual_v2"
            }
            resp = requests.post(url, headers=headers, json=data, timeout=30)
            if resp.status_code == 200:
                return resp.content
            else:
                raise ProviderError(resp.status_code, resp.text)
                
        elif name == 'google_tts':
            raise ProviderError(500, "Google TTS not fully supported without specific library access in this context")
            
    result = call_with_fallback(provider_chain, tts_call_func)
    if result and result.get("result"):
        audio_bytes = result["result"]
        output_path = "/tmp/output.mp3"
        try:
            with open(output_path, "wb") as f:
                f.write(audio_bytes)
            return {"path": output_path, "provider": result["provider"]}
        except Exception:
            with open("output.mp3", "wb") as f:
                f.write(audio_bytes)
            return {"path": "output.mp3", "provider": result["provider"]}
        
    print("voice unavailable, sent text")
    return None
