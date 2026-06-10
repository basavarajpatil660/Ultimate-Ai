# Ultimate AI Agent

A completely serverless, multi-agent AI system running entirely on GitHub Actions. It supports dynamic task routing, text generation, image generation, web search, voice synthesis, and automatic fallback chains.

## Section 1: Setup Steps

**Step 1:** Fork or create this repository on your GitHub account.
**Step 2:** Go to your repository → **Settings** → **Secrets and Variables** → **Actions**.
**Step 3:** Click **New Repository Secret**.
**Step 4:** Add each secret listed below exactly as named.

## Section 2: Complete Secret List

- `TELEGRAM_BOT_TOKEN` — Get from [@BotFather](https://t.me/BotFather) on Telegram
- `TELEGRAM_CHAT_ID` — Your personal Telegram chat ID
- `GMAIL_ADDRESS` — Your Gmail address
- `GMAIL_APP_PASSWORD` — Generate from [Google Account Security](https://myaccount.google.com/security) (App Passwords)
- `MISTRAL_API_KEY` — Get from [Mistral Admin](https://console.mistral.ai/)
- `CEREBRAS_API_KEY` — Get from [Cerebras Cloud](https://cloud.cerebras.ai/)
- `GROQ_API_KEY` — Get from [Groq Console](https://console.groq.com/)
- `OPENROUTER_API_KEY` — Get from [OpenRouter](https://openrouter.ai/)
- `GOOGLE_AI_KEY` — Get from [Google AI Studio](https://aistudio.google.com/)
- `CLOUDFLARE_WORKER_URL` — Your existing Cloudflare worker `/generate` endpoint URL
- `TOGETHER_API_KEY` — Get from [Together AI](https://api.together.ai/)
- `COHERE_API_KEY` — Get from [Cohere Dashboard](https://dashboard.cohere.com/)
- `JINA_API_KEY` — Get from [Jina AI](https://jina.ai/)
- `TAVILY_API_KEY` — Get from [Tavily](https://app.tavily.com/)
- `ASSEMBLYAI_API_KEY` — Get from [AssemblyAI](https://www.assemblyai.com/)
- `ELEVENLABS_API_KEY` — Get from [ElevenLabs](https://elevenlabs.io/)
- `PIXAZO_API_KEY` — Get from [Pixazo Console](https://api-console.pixazo.ai/)

## Section 3: How to trigger manually

1. Go to the **Actions** tab in your repository.
2. Select **Ultimate AI Agent** from the left menu.
3. Click **Run workflow**.
4. Enter your prompt and select the mode.
5. Click **Run workflow**.

## Section 4: How scheduled runs work

The agent runs automatically on a scheduled cron. By default, it runs at these IST times:
6:00 AM, 8:00 AM, 10:00 AM, 11:00 AM, 1:00 PM, 3:00 PM, 5:00 PM, 7:00 PM, 9:00 PM, 11:00 PM, 1:00 AM.

If a scheduled run occurs without a prompt, the agent defaults to generating a content idea, an AI news briefing, and sending an email requesting manual input for next time.
