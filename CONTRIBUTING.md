# 🤝 Contributing to Nick's Ultimate AI Agent

First off — thanks for taking the time to contribute! Every bit helps, whether it's fixing a typo or adding a whole new agent. 🙌

---

## 📋 Table of Contents

- [Code of Conduct](#code-of-conduct)
- [How Can I Contribute?](#how-can-i-contribute)
- [Getting Started](#getting-started)
- [Commit Message Standards](#commit-message-standards)
- [Pull Request Process](#pull-request-process)
- [What Not To Include](#what-not-to-include)

---

## 🧭 Code of Conduct

Be respectful. Be constructive. No harassment, no spam, no toxic behavior. Simple.

---

## 💡 How Can I Contribute?

### 🐛 Reporting Bugs
- Go to [Issues](https://github.com/basavarajpatil660/ultimate-ai-agent/issues)
- Click **New Issue**
- Describe: what happened, what you expected, steps to reproduce
- Include logs if available (remove any sensitive data first)

### 💡 Suggesting Features
- Go to [Discussions](https://github.com/basavarajpatil660/ultimate-ai-agent/discussions)
- Open a new discussion under **Ideas**
- Describe the feature and why it fits this project

### 🔧 Writing Code
Good areas to contribute:
- New agent types (video generation, code execution, reminders)
- Additional LLM provider integrations
- Dashboard improvements
- Bug fixes
- Documentation improvements
- Better error handling and fallback logic

---

## 🚀 Getting Started

```bash
# 1. Fork the repo on GitHub

# 2. Clone your fork
git clone https://github.com/YOUR_USERNAME/ultimate-ai-agent.git
cd ultimate-ai-agent

# 3. Create a new branch
git checkout -b feature/your-feature-name

# 4. Make your changes

# 5. Test your changes manually

# 6. Commit using conventional commits (see below)
git commit -m "feat: add video generation agent"

# 7. Push to your fork
git push origin feature/your-feature-name

# 8. Open a Pull Request on GitHub
```

---

## ✍️ Commit Message Standards

We use **Conventional Commits** format:

```
<type>: <short description>
```

| Type | When To Use |
|---|---|
| `feat:` | Adding a new feature |
| `fix:` | Fixing a bug |
| `docs:` | Documentation changes only |
| `refactor:` | Code change that's not a fix or feature |
| `chore:` | Maintenance tasks, dependency updates |
| `test:` | Adding or updating tests |

**Examples:**
```
feat: add WhatsApp interface support
fix: resolve image agent black image fallback
docs: update setup guide for Cloudflare KV binding
refactor: simplify LLM provider chain logic
chore: update requirements.txt dependencies
```

---

## 🔁 Pull Request Process

1. Make sure your branch is up to date with `main`
2. Write a clear PR title using conventional commit format
3. Fill in the PR description — what changed and why
4. Link to any related issue (e.g. `Closes #12`)
5. Wait for review — feedback will be given constructively

**PR will be merged when:**
- Code is clean and readable
- No hardcoded secrets or personal data
- Existing functionality is not broken
- Description clearly explains the change

---

## 🚫 What Not To Include

> [!WARNING]
> PRs containing any of the following will be immediately closed:

- Real API keys, tokens, or secrets of any kind
- Personal data (chat IDs, email addresses, names)
- Hardcoded URLs pointing to personal Cloudflare workers
- Debug files or local test scripts
- Unrelated changes bundled into one PR

---

## 🙏 Thank You

Every contribution matters — from a typo fix to a full new feature. If you build something cool on top of this, share it in Discussions! Would love to see what people create. 🚀
