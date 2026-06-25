# 🤖 Nick's Ultimate AI Agent

> A fully serverless, multi-agent AI system built on **Cloudflare Workers + GitHub Actions** — controlled entirely via Telegram. Text, image generation, image editing, voice, web search, and content creation — all running on **free tier APIs. No credit card. No server.**

Built by **Basavaraj M Patil (Nick)** — Hubballi, Karnataka, India 🇮🇳

[![GitHub Actions](https://img.shields.io/badge/GitHub_Actions-Orchestrator-2088FF?logo=github-actions&logoColor=white)](https://github.com/features/actions)
[![Cloudflare Workers](https://img.shields.io/badge/Cloudflare_Workers-Serverless-F38020?logo=cloudflare&logoColor=white)](https://workers.cloudflare.com)
[![Python](https://img.shields.io/badge/Python-3.11-3776AB?logo=python&logoColor=white)](https://python.org)
[![Telegram](https://img.shields.io/badge/Telegram-Bot_Interface-26A5E4?logo=telegram&logoColor=white)](https://core.telegram.org/bots)

---

## ✨ What It Does

Send a message to a Telegram bot → GitHub Actions spins up a Python agent → AI processes the task → result sent back to Telegram. That's it. No server running 24/7. No cost.

**Capabilities:**
- 💬 **Smart Chat** — Multi-provider LLM with 5-layer fallback chain
- 🎨 **Image Generation** — FLUX 1 Schnell via Cloudflare Workers AI
- ✏️ **Image Editing** — Stable Diffusion img2img (attach photo + prompt)
- 👁 **Image Analysis** — Describe or analyze any photo
- 🔊 **Voice Output** — Text-to-speech via ElevenLabs or gTTS
- 🔍 **Web Research** — Live search via Tavily + LLM synthesis
- 📱 **Content Creation** — Gaming/AI captions for Instagram & YouTube
- 📋 **Prompt Templates** — Save reusable image prompt templates with `{X}` placeholders
- 🧠 **Private Memory** — Persistent AI memory across sessions via Cloudflare KV
- ⚡ **Automation Triggers** — Trigger YouTube/AI trend hunters from Telegram

---

## 🏗 Architecture

```
Telegram Message
      │
      ▼
Cloudflare Worker (Webhook)
      │
      ├── Static commands → reply instantly
      ├── Template commands → KV read/write
      └── AI tasks → trigger GitHub Actions
                          │
                          ▼
                   Python Agent (main.py)
                          │
                    ┌─────┴──────┐
                    │            │
               LLM Chain    Image/Voice/Search
                    │            │
               Mistral      Cloudflare FLUX
               Cerebras      Pollinations AI
               Groq           Pixazo
               OpenRouter     ElevenLabs / gTTS
               Gemini         Tavily / Jina
                    │
                    ▼
             Result → Telegram
             Log    → Cloudflare D1
             Memory → Cloudflare KV
```

---

## 🤖 Telegram Commands

### 🎯 AI Task Commands
| Command | Description |
|---|---|
| `/image <prompt>` | Generate an AI image using FLUX |
| `/image_edit <prompt>` + attach photo | Edit an image with AI |
| `/image_read <question>` + attach photo | Analyze or describe an image |
| `/voice <text>` | Convert text to speech |
| `/research <query>` | Web search + AI summary |
| `/content <topic>` | Generate social media caption |
| Just type anything | Auto mode — agent detects the task |

### 📋 Prompt Template Commands
| Command | Description |
|---|---|
| `/save_template <name> <prompt with {X}>` | Save a reusable prompt |
| `/use_template <name> <subject>` | Generate image using template |
| `/list_templates` | Show all saved templates |
| `/delete_template <name>` | Delete a template |

### ⚡ Automation Triggers
| Command | Description |
|---|---|
| `/youtube_trends` | Trigger YouTube Trend Hunter |
| `/ai_trends` | Trigger AI Daily Trend Hunter |

### 📊 Info Commands
| Command | Description |
|---|---|
| `/status` | Live stats for today |
| `/models` | All AI models in use |
| `/providers` | Provider chain + limits |
| `/modes` | What each mode does |
| `/about` | About this agent |
| `/help` | Full command list |

---

## 🧠 AI Provider Chain

### 💬 LLM (Text) — 5-layer fallback
1. **Mistral Large** — 1B tokens/month
2. **Cerebras Llama 3.3 70B** — 1M tokens/day (fastest)
3. **Groq Llama 3.3 70B** — 1K req/day
4. **OpenRouter** — Free tier (DeepSeek, Qwen3)
5. **Google Gemini 2.5 Flash** — 1.5K req/day

### 🎨 Image Generation — 3-layer fallback
1. **Cloudflare Workers AI** — FLUX 1 Schnell (primary)
2. **Pollinations AI** — Free, no key needed (backup)
3. **Pixazo** — Free tier (fallback)

### 🖼 Image Editing
- **Cloudflare Workers AI** — Stable Diffusion v1-5 img2img

### 👁 Vision / Image Analysis
1. **Gemini 2.5 Flash Vision** (primary)
2. **Groq Llama 3.2 Vision** (fallback)

### 🔊 Voice / TTS
1. **ElevenLabs** — Rachel voice, 10K chars/month
2. **gTTS** — Unlimited fallback

### 🔍 Web Search
1. **Tavily** — 1K searches/month
2. **Jina Reader** — Scraper fallback

---

## 🏛 Infrastructure

| Component | Service | Purpose |
|---|---|---|
| Webhook Worker | Cloudflare Workers | Receives Telegram messages, routes commands |
| Image Worker | Cloudflare Workers AI | FLUX image gen + SD img2img editing |
| Orchestrator | GitHub Actions | Runs Python agent per task |
| Database | Cloudflare D1 | Logs commands, images, automation runs |
| Memory | Cloudflare KV | Private AI memory across sessions |
| Templates | Cloudflare KV | User prompt templates |
| Dashboard | Lovable (React) | Visual dashboard for stats + history |

---

## 📁 Project Structure

```
ultimate-ai-agent/
├── main.py                  # Entry point — task router
├── requirements.txt
├── agents/
│   ├── llm_agent.py         # Multi-provider LLM chain
│   ├── image_agent.py       # Image gen + edit
│   ├── vision_agent.py      # Image analysis
│   ├── search_agent.py      # Web research + synthesis
│   ├── content_agent.py     # Social media content
│   └── voice_agent.py       # Text-to-speech
├── core/
│   ├── memory.py            # KV memory system
│   ├── router.py            # Task classifier
│   ├── formatter.py         # Output formatter
│   └── delivery.py          # Telegram send helpers
└── .github/
    └── workflows/
        ├── agent.yml        # Main agent workflow
        ├── daily.yml        # Scheduled auto-runs
        └── ...              # 8 total workflows
```

---

## ⚙️ GitHub Secrets Required

| Secret | Description |
|---|---|
| `TELEGRAM_BOT_TOKEN` | Your Telegram bot token |
| `TELEGRAM_CHAT_ID` | Your Telegram chat ID |
| `CLOUDFLARE_WORKER_URL` | github-backend worker URL |
| `CLOUDFLARE_API_KEY` | image-api worker auth key |
| `DASHBOARD_API_KEY` | Dashboard auth key |
| `MISTRAL_API_KEY` | Mistral API key |
| `CEREBRAS_API_KEY` | Cerebras API key |
| `GROQ_API_KEY` | Groq API key |
| `OPENROUTER_API_KEY` | OpenRouter API key |
| `GOOGLE_AI_KEY` | Google AI Studio key |
| `ELEVENLABS_API_KEY` | ElevenLabs API key |
| `TAVILY_API_KEY` | Tavily search key |
| `JINA_API_KEY` | Jina Reader key |
| `GMAIL_ADDRESS` | Gmail for email alerts |
| `GMAIL_APP_PASSWORD` | Gmail app password |

> All providers used are **free tier** — no credit card required.

---

## 🗄 Cloudflare D1 Database Schema

```sql
-- Command history
CREATE TABLE commands (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  command TEXT,
  mode TEXT,
  prompt TEXT,
  provider TEXT,
  status TEXT,
  created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- Image gallery
CREATE TABLE images (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  prompt TEXT,
  template_name TEXT,
  file_id TEXT,
  image_url TEXT,
  created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- Automation run logs
CREATE TABLE automation_runs (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  automation TEXT,
  status TEXT,
  created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);
```

---

## 🧠 Memory System

The agent uses **Cloudflare KV** for private persistent memory:

| KV Key | Content |
|---|---|
| `agent_state` | Overall agent state and preferences |
| `conversation` | Recent conversation context (5-min window) |
| `user_profile` | User profile — name, projects, style |

Memory is **completely private** — stored in Cloudflare KV, never in the public repo.

---

## 📊 Dashboard

A React dashboard (built with Lovable) connects to the Cloudflare Worker API for:
- 📈 Command history with filters
- 🎨 Image gallery
- ⚡ Automation run logs
- 🏥 Provider health status
- 📋 Template manager

---

## 🔄 Scheduled Runs

GitHub Actions runs the agent automatically at:

`6AM, 8AM, 10AM, 11AM, 1PM, 3PM, 5PM, 7PM, 9PM, 11PM, 1AM IST`

In auto mode (no prompt), it generates a NickPlays content idea + AI news briefing and sends to Telegram.

---

## 🚀 Getting Started

1. **Fork this repo**
2. **Set up Cloudflare:**
   - Create a Worker for the webhook (github-backend)
   - Create a Worker for image generation (image-api)
   - Create a D1 database and run the schema above
   - Create two KV namespaces: one for templates, one for memory
3. **Create a Telegram Bot** via [@BotFather](https://t.me/BotFather)
4. **Add all GitHub Secrets** from the table above
5. **Deploy both Cloudflare Workers** with your code
6. **Set Telegram webhook** to your github-backend worker URL
7. **Send `/help`** to your bot and start using it!

---

## 👨‍💻 Built By

**Basavaraj M Patil (Nick)**
- 📍 Hubballi, Karnataka, India
- 🎓 Computer Science Diploma Student
- 📺 [NickPlays](https://youtube.com) — Gaming YouTube Channel
- 💻 [GitHub](https://github.com/basavarajpatil660)
- 🔗 [LinkedIn](https://linkedin.com/in/itsbasavarajmp)
- 📸 [Instagram](https://instagram.com/basavaraj_nick)

> Built entirely on mobile using Antigravity (Gemini) + Claude. 100% free tier. No PC required for development.

---

## 📜 License

MIT License — use freely, learn from it, build on it.
