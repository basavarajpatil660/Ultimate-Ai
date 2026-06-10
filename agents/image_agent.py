import os
import requests
import base64
from core.fallback import call_with_fallback, ProviderError

def generate_image(prompt):
    provider_chain = [
        {
            'provider_name': 'cloudflare',
            'api_key': os.environ.get("CLOUDFLARE_WORKER_URL"),
            'model': 'worker',
            'max_retries': 2,
            'backoff_seconds': [2, 4]
        },
        {
            'provider_name': 'together',
            'api_key': os.environ.get("TOGETHER_API_KEY"),
            'model': 'black-forest-labs/FLUX.1-schnell-Free',
            'max_retries': 2,
            'backoff_seconds': [2, 4]
        },
        {
            'provider_name': 'pixazo',
            'api_key': os.environ.get("PIXAZO_API_KEY"),
            'model': 'flux-schnell',
            'max_retries': 2,
            'backoff_seconds': [2, 4]
        }
    ]
    
    def img_call_func(provider):
        name = provider['provider_name']
        api_key = provider['api_key'] 
        model = provider['model']
        
        if name == 'cloudflare':
            url = f"{api_key}/generate" if not str(api_key).endswith('/generate') else api_key
            try:
                resp = requests.post(url, json={"prompt": prompt, "enhance": True}, timeout=30)
                if resp.status_code == 200:
                    return resp.content 
                else:
                    raise ProviderError(resp.status_code, resp.text)
            except requests.exceptions.RequestException as e:
                raise ProviderError(500, str(e))
                
        elif name == 'together':
            url = "https://api.together.xyz/v1/images/generations"
            headers = {
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json"
            }
            data = {
                "model": model,
                "prompt": prompt,
                "steps": 4,
                "n": 1
            }
            resp = requests.post(url, headers=headers, json=data, timeout=30)
            if resp.status_code == 200:
                b64_img = resp.json()['data'][0]['b64_json']
                return base64.b64decode(b64_img)
            else:
                raise ProviderError(resp.status_code, resp.text)
                
        elif name == 'pixazo':
            url = "https://api-console.pixazo.ai/v1/generate"
            headers = {
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json"
            }
            data = {
                "model": model,
                "prompt": prompt
            }
            resp = requests.post(url, headers=headers, json=data, timeout=30)
            if resp.status_code == 200:
                if 'application/json' in resp.headers.get('Content-Type', ''):
                    try:
                        b64_img = resp.json().get('image_base64', '')
                        if b64_img:
                            return base64.b64decode(b64_img)
                    except Exception:
                        pass
                return resp.content
            else:
                raise ProviderError(resp.status_code, resp.text)

    result = call_with_fallback(provider_chain, img_call_func)
    if result and result.get("result"):
        image_bytes = result["result"]
        output_path = "/tmp/output.png"
        try:
            with open(output_path, "wb") as f:
                f.write(image_bytes)
            return {"path": output_path, "provider": result["provider"]}
        except Exception:
            # fallback if /tmp is not available locally or on specific runner
            with open("output.png", "wb") as f:
                f.write(image_bytes)
            return {"path": "output.png", "provider": result["provider"]}
    return None
