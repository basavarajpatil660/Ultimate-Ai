import os
import requests
import time

def generate_image(prompt, CLOUDFLARE_WORKER_URL=None,
                   HUGGINGFACE_API_KEY=None,
                   PIXAZO_API_KEY=None):

    # Truncate prompt to safe length
    prompt = prompt[:500] if prompt else "abstract art"
    
    # Provider 1: Cloudflare Worker
    if CLOUDFLARE_WORKER_URL:
        try:
            url = CLOUDFLARE_WORKER_URL.rstrip("/") + "/generate"
            response = requests.post(
                url,
                json={"prompt": prompt, "enhance": True},
                timeout=60
            )
            if response.status_code == 200:
                with open("/tmp/output.png", "wb") as f:
                    f.write(response.content)
                print("Image generated via Cloudflare")
                return {
                    "file_path": "/tmp/output.png",
                    "provider": "cloudflare"
                }
        except Exception as e:
            print(f"Cloudflare image failed: {e}")

    # Provider 2: Hugging Face FLUX
    if HUGGINGFACE_API_KEY:
        for attempt in range(3):
            try:
                response = requests.post(
                    "https://api-inference.huggingface.co/models/black-forest-labs/FLUX.1-schnell",
                    headers={
                        "Authorization": f"Bearer {HUGGINGFACE_API_KEY}"
                    },
                    json={"inputs": prompt},
                    timeout=60
                )
                if response.status_code == 200:
                    with open("/tmp/output.png", "wb") as f:
                        f.write(response.content)
                    print("Image generated via HuggingFace")
                    return {
                        "file_path": "/tmp/output.png",
                        "provider": "huggingface"
                    }
                elif response.status_code == 503:
                    # Model loading, wait and retry
                    wait = 10 * (attempt + 1)
                    print(f"HF model loading, waiting {wait}s")
                    time.sleep(wait)
                else:
                    print(f"HF failed: {response.status_code}")
                    break
            except Exception as e:
                print(f"HuggingFace image failed: {e}")
                break

    # Provider 3: Pixazo
    if PIXAZO_API_KEY:
        try:
            response = requests.post(
                "https://api-console.pixazo.ai/v1/generate",
                headers={
                    "Authorization": f"Bearer {PIXAZO_API_KEY}",
                    "Content-Type": "application/json"
                },
                json={
                    "prompt": prompt,
                    "model": "flux-schnell"
                },
                timeout=60
            )
            if response.status_code == 200:
                data = response.json()
                img_url = data.get("image_url") or \
                          data.get("url") or \
                          data.get("output")
                if img_url:
                    img_response = requests.get(
                        img_url, timeout=30)
                    if img_response.status_code == 200:
                        with open("/tmp/output.png", "wb") as f:
                            f.write(img_response.content)
                        print("Image generated via Pixazo")
                        return {
                            "file_path": "/tmp/output.png",
                            "provider": "pixazo"
                        }
        except Exception as e:
            print(f"Pixazo image failed: {e}")

    print("All image providers failed")
    return None
