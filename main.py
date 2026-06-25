import os
import sys
import requests
import traceback
import re
from datetime import datetime

from core.memory import load_memory, save_memory, reset_daily_budget, update_budget
from core.router import classify_task, detect_language
from core.formatter import format_output
from core.delivery import send_text, send_image, send_audio, send_alert, send_email

from agents.llm_agent import call_llm
from agents.image_agent import generate_image
from agents.vision_agent import analyze_image
from agents.search_agent import research_and_synthesize
from agents.content_agent import generate_content
from agents.voice_agent import text_to_speech
from agents.image_agent import generate_image, edit_image


def notify_worker_image(prompt, file_id, template_name=None):
    """
    Callback to worker after image is sent to Telegram.
    Saves file_id + prompt to D1 via /api/image_callback endpoint.
    """
    worker_url = os.environ.get("CLOUDFLARE_WORKER_URL", "")
    api_key = os.environ.get("DASHBOARD_API_KEY", "")
    if not worker_url or not api_key:
        print("Worker URL or API key missing — skipping image callback")
        return
    try:
        # Strip trailing slash
        base = worker_url.rstrip("/")
        # Remove /generate if present
        base = base.replace("/generate", "")
        resp = requests.post(
            f"{base}/api/image_callback",
            json={"prompt": prompt, "file_id": file_id, "template_name": template_name},
            headers={"X-Dashboard-Key": api_key},
            timeout=10
        )
        print(f"Image callback: {resp.status_code}")
    except Exception as e:
        print(f"Image callback failed: {e}")


def main():
    try:
        memory = load_memory()
        memory = reset_daily_budget(memory)

        prompt = os.environ.get("INPUT_PROMPT", "").strip()
        mode = os.environ.get("INPUT_MODE", "auto")

        telegram_token = os.environ.get("TELEGRAM_BOT_TOKEN")
        chat_id = os.environ.get("TELEGRAM_CHAT_ID")
        gmail = os.environ.get("GMAIL_ADDRESS")
        gmail_pw = os.environ.get("GMAIL_APP_PASSWORD")

        CLOUDFLARE_WORKER_URL = os.environ.get("CLOUDFLARE_WORKER_URL", None)
        CLOUDFLARE_API_KEY = os.environ.get("CLOUDFLARE_API_KEY", None)
        PIXAZO_API_KEY = os.environ.get("PIXAZO_API_KEY", None)
        ELEVENLABS_API_KEY = os.environ.get("ELEVENLABS_API_KEY", None)

        if not prompt and mode == "auto":
            idea_res = call_llm("Generate one unique content idea for my YouTube channel. Return only the idea.")
            news_res = call_llm("Generate one short AI news briefing bullet point.")

            if idea_res:
                send_text(telegram_token, chat_id, f"🎮 *Content Idea:*\n{idea_res.get('result', '')}\n_Provider: {idea_res.get('provider', '')}_")
            if news_res:
                send_text(telegram_token, chat_id, f"📰 *AI News:*\n{news_res.get('result', '')}\n_Provider: {news_res.get('provider', '')}_")

            time_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S UTC")
            send_email(gmail, gmail_pw, gmail, "🤖 Agent needs your input", f"Your AI agent ran at {time_str} but received no prompt.")

            memory["run_count_today"] += 1
            save_memory(memory)
            sys.exit(0)

        if prompt:
            has_image = False
            if mode == "image_edit" and "[IMAGE_URL:" in prompt:
                task_type = "IMAGE_EDIT"
            elif mode == "image_read" and "[IMAGE_URL:" in prompt:
                task_type = "IMAGE_READ"
            else:
                task_type = classify_task(prompt, has_image)

            lang = detect_language(prompt)
            if lang == "hindi/hinglish":
                prompt += " (Please respond in Hindi/Hinglish)"

            provider_used = "unknown"
            result_data = None

            if task_type in ["FACTUAL", "CREATIVE", "REASONING", "CODE", "SUMMARIZE", "TRANSLATE"]:
                res = call_llm(prompt)
                if res:
                    result_data = res["result"]
                    provider_used = res["provider"]

            elif task_type in ["REALTIME", "RESEARCH"]:
                res = research_and_synthesize(prompt)
                if res:
                    result_data = res["result"]
                    provider_used = res["provider"]

            elif task_type == "IMAGE_GEN":
                res = generate_image(
                    prompt,
                    CLOUDFLARE_WORKER_URL=CLOUDFLARE_WORKER_URL,
                    CLOUDFLARE_API_KEY=CLOUDFLARE_API_KEY,
                    PIXAZO_API_KEY=PIXAZO_API_KEY
                )
                if res:
                    result_data = res
                    provider_used = res["provider"]

            elif task_type == "IMAGE_READ":
                url_match = re.search(r'\[IMAGE_URL:(.+?)\]', prompt)
                if url_match:
                    image_url = url_match.group(1)
                    prompt = re.sub(r'\[IMAGE_URL:.+?\]', '', prompt).strip()
                    try:
                        img_response = requests.get(image_url, timeout=30)
                        if img_response.status_code == 200:
                            image_path = "/tmp/input.png"
                            with open(image_path, 'wb') as f:
                                f.write(img_response.content)
                            if os.path.exists(image_path):
                                res = analyze_image(image_path, prompt)
                                if res:
                                    result_data = res["result"]
                                    provider_used = res["provider"]
                            else:
                                result_data = "Image download failed - file not saved."
                        else:
                            result_data = f"Failed to download image: HTTP {img_response.status_code}"
                    except Exception as e:
                        result_data = f"Image download error: {str(e)}"
                else:
                    result_data = "No image URL found in prompt."

            elif task_type == "IMAGE_EDIT":
                url_match = re.search(r'\[IMAGE_URL:(.+?)\]', prompt)
                if url_match:
                    image_url = url_match.group(1)
                    prompt = re.sub(r'\[IMAGE_URL:.+?\]', '', prompt).strip()
                    try:
                        img_response = requests.get(image_url, timeout=30)
                        if img_response.status_code == 200:
                            image_path = "/tmp/input.png"
                            with open(image_path, 'wb') as f:
                                f.write(img_response.content)
                            if os.path.exists(image_path):
                                res = edit_image(
                                    image_path, prompt,
                                    CLOUDFLARE_WORKER_URL=CLOUDFLARE_WORKER_URL,
                                    CLOUDFLARE_API_KEY=CLOUDFLARE_API_KEY
                                )
                                if res:
                                    result_data = res
                                    provider_used = res["provider"]
                            else:
                                result_data = "Image download failed - file not saved."
                        else:
                            result_data = f"Failed to download image: HTTP {img_response.status_code}"
                    except Exception as e:
                        result_data = f"Image download error: {str(e)}"
                else:
                    result_data = "No image URL found in prompt."

            elif task_type == "CONTENT":
                res = generate_content(prompt)
                if res:
                    result_data = res["result"]
                    provider_used = res["provider"]

            elif task_type == "VOICE_OUT":
                res_text = call_llm(prompt)
                if res_text:
                    text_str = res_text["result"]
                    audio_res = text_to_speech(text_str, ELEVENLABS_API_KEY=ELEVENLABS_API_KEY)
                    if audio_res:
                        result_data = audio_res
                        provider_used = f"llm:{res_text['provider']}, voice:{audio_res['provider']}"
                    else:
                        result_data = text_str
                        task_type = "text"
                        provider_used = res_text["provider"]

            if result_data:
                formatted = format_output(result_data, task_type, provider_used)

                if formatted["type"] == "image" and \
                   formatted.get("file_path") and \
                   os.path.exists(formatted["file_path"]):
                    # ✅ Capture file_id after sending image
                    file_id = send_image(
                        telegram_token, chat_id,
                        formatted["file_path"],
                        formatted.get("caption", "")
                    )
                    # ✅ Send callback to worker — saves to D1 images table
                    if file_id:
                        notify_worker_image(prompt, file_id)

                elif formatted["type"] == "image" and not formatted.get("file_path"):
                    send_text(telegram_token, chat_id, "Image generation failed: file not saved.")

                elif formatted["type"] == "audio" and \
                     formatted.get("file_path") and \
                     os.path.exists(formatted["file_path"]):
                    send_audio(
                        telegram_token, chat_id,
                        formatted["file_path"],
                        formatted.get("caption", "")
                    )
                else:
                    send_text(telegram_token, chat_id, formatted.get("content", "Task completed but no output."))

                if provider_used == "mistral":
                    update_budget("mistral", 500)
                elif provider_used == "cerebras":
                    update_budget("cerebras", 500)
                elif provider_used == "groq":
                    update_budget("groq", 1)
            else:
                send_text(telegram_token, chat_id, "Failed to process task across all providers.")

            memory["run_count_today"] += 1
            if "tasks_today" not in memory:
                memory["tasks_today"] = []
            memory["tasks_today"].append({
                "prompt": prompt,
                "type": task_type,
                "provider": provider_used,
                "time": datetime.now().isoformat()
            })
            save_memory(memory)

    except Exception as e:
        telegram_token = os.environ.get("TELEGRAM_BOT_TOKEN")
        chat_id = os.environ.get("TELEGRAM_CHAT_ID")
        error_msg = f"Agent Crash:\n{traceback.format_exc()}"
        print("=== AGENT CRASH ===")
        print(error_msg)
        print("===================")
        try:
            send_alert(telegram_token, chat_id, error_msg[:4000])
        except Exception as alert_err:
            print(f"send_alert also failed: {alert_err}")
        sys.exit(1)


if __name__ == "__main__":
    main()
