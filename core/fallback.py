import time
import requests
import logging
from core.memory import load_memory, save_memory

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ProviderError(Exception):
    def __init__(self, status_code, message=""):
        self.status_code = status_code
        self.message = message

def call_with_fallback(provider_chain, call_func):
    
    memory = load_memory()
    failed_keys = memory.get("failed_keys", [])
    
    for provider in provider_chain:
        provider_name = provider.get('provider_name')
        api_key = provider.get('api_key')
        max_retries = provider.get('max_retries', 1)
        backoff = provider.get('backoff_seconds', [])
        
        if not api_key:
            continue
            
        if provider_name in failed_keys:
            continue
            
        for attempt in range(max_retries):
            try:
                result = call_func(provider)
                logger.info(f"Success with {provider_name}")
                return {"provider": provider_name, "result": result}
            except ProviderError as e:
                if e.status_code == 429:
                    break # immediately try next provider
                elif e.status_code in [500, 502, 503]:
                    wait_time = backoff[attempt] if attempt < len(backoff) else 5
                    time.sleep(wait_time)
                elif e.status_code == 401:
                    if provider_name not in failed_keys:
                        failed_keys.append(provider_name)
                        memory["failed_keys"] = failed_keys
                        save_memory(memory)
                    break
                else:
                    break # other errors skip
            except requests.exceptions.Timeout:
                if attempt == 0 and max_retries > 1:
                    time.sleep(1) # small delay before retry
                else:
                    break
            except Exception as e:
                logger.error(f"Exception on {provider_name}: {str(e)}")
                break
                
    return None
