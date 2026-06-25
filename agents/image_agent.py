import os
import requests
import time
import urllib.parse

def generate_image(
    prompt,
    CLOUDFLARE_WORKER_URL=None,
    CLOUDFLARE_API_KEY=None,
    PIXAZO_API_KEY=None
):
    prompt = prompt[:500] if prompt else "abstract art"

    IMAGE_WORKER_URL = CLOUDFLARE_WORKER_URL or os.environ.get("CLOUDFLARE_WORKER_URL")
    try:
        url = IMAGE_WORKER_URL + "/generate"
        headers = {"Content-Type": "application/json"}
        if CLOUDFLARE_API_KEY:
            headers["Authorization"] = f"Bearer {CLOUDFLARE_API_KEY}"
        response = requests.post(
            url,
            headers=headers,
            json={"prompt": prompt},
            timeout=60
        )
        print(f"Cloudflare status: {response.status_code}")
        if response.status_code == 200:
            content = response.content
            if len(content) > 1000:
                with open("/tmp/output.png", "wb") as f:
                    f.write(content)
                print("Image generated via Cloudflare FLUX")
                return {"file_path": "/tmp/output.png", "provider": "cloudflare"}
            else:
                print(f"Cloudflare returned too small: {len(content)} bytes")
                print(f"Response text: {response.text[:200]}")
        else:
            print(f"Cloudflare error: {response.status_code} - {response.text[:200]}")
    except Exception as e:
        print(f"Cloudflare exception: {e}")

    # Provider 2: Pollinations AI (100% free, no key needed)
    try:
        encoded = urllib.parse.quote(prompt)
        img_url = f"https://image.pollinations.ai/prompt/{encoded}?width=512&height=512&nologo=true"
        print(f"Trying Pollinations AI...")
        response = requests.get(img_url, timeout=60)
        print(f"Pollinations status: {response.status_code}")
        if response.status_code == 200 and len(response.content) > 1000:
            with open("/tmp/output.png", "wb") as f:
                f.write(response.content)
            print("Image generated via Pollinations AI")
            return {"file_path": "/tmp/output.png", "provider": "pollinations"}
        else:
            print(f"Pollinations too small or failed: {len(response.content)} bytes")
    except Exception as e:
        print(f"Pollinations exception: {e}")

    # Provider 3: Pixazo
    if PIXAZO_API_KEY:
        try:
            response = requests.post(
                "https://api-console.pixazo.ai/v1/generate",
                headers={
                    "Authorization": f"Bearer {PIXAZO_API_KEY}",
                    "Content-Type": "application/json"
                },
                json={"prompt": prompt, "model": "flux-schnell"},
                timeout=60
            )
            if response.status_code == 200:
                data = response.json()
                img_url = data.get("image_url") or data.get("url") or data.get("output")
                if img_url:
                    img_response = requests.get(img_url, timeout=30)
                    if img_response.status_code == 200:
                        with open("/tmp/output.png", "wb") as f:
                            f.write(img_response.content)
                        print("Image generated via Pixazo")
                        return {"file_path": "/tmp/output.png", "provider": "pixazo"}
        except Exception as e:
            print(f"Pixazo image failed: {e}")

    print("All image providers failed")
    return None


def edit_image(
    image_path,
    prompt,
    CLOUDFLARE_WORKER_URL=None,
    CLOUDFLARE_API_KEY=None
):
    import base64
    prompt = prompt[:500] if prompt else "enhance this image"

    IMAGE_WORKER_URL = CLOUDFLARE_WORKER_URL or os.environ.get("CLOUDFLARE_WORKER_URL")

    try:
        with open(image_path, "rb") as f:
            image_data = base64.b64encode(f.read()).decode("utf-8")

        url = IMAGE_WORKER_URL + "/edit"
        headers = {"Content-Type": "application/json"}
        if CLOUDFLARE_API_KEY:
            headers["Authorization"] = f"Bearer {CLOUDFLARE_API_KEY}"

        response = requests.post(
            url,
            headers=headers,
            json={"prompt": prompt, "image": image_data},
            timeout=60
        )
        print(f"Cloudflare edit status: {response.status_code}")
        if response.status_code == 200:
            content = response.content
            if len(content) > 1000:
                with open("/tmp/output_edit.png", "wb") as f:
                    f.write(content)
                print("Image edited via Cloudflare FLUX.2 klein")
                return {"file_path": "/tmp/output_edit.png", "provider": "cloudflare-flux2-klein"}
            else:
                print(f"Edit returned too small: {len(content)} bytes")
        else:
            print(f"Cloudflare edit error: {response.status_code}")
    except Exception as e:
        print(f"Cloudflare edit exception: {e}")

    print("Image edit failed")
    return None
