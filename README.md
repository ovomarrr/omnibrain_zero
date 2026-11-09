# 🧠 OmniBrain Zero+

A free-first, cloud-hostable AI command center. No local AI server is required.

## Features

- **Universal Chat:** Gemini and OpenRouter provider adapters.
- **AI Council:** concurrent independent answers, optional critique pass, and synthesis.
- **Research Desk:** public DuckDuckGo search results with AI source analysis.
- **Document Brain:** upload TXT, Markdown, PDF, and DOCX; extract text, chunk it, and retrieve relevant passages.
- **Memory Vault:** manually curated, searchable memory.
- **Agent Studio:** built-in specialist roles and custom agents.
- **Conversation history:** SQLite persistence and Markdown export.
- **Dark dashboard:** browser-based Streamlit UI.

## Zero-cost promise and limitations

The source code has no mandatory paid services or subscriptions. Use only model endpoints explicitly marked free by the provider. Free quotas, rate limits, model availability, hosting policies, and storage limits can change. This does **not** promise unlimited AI inference or 24/7 uptime.

## Deploy on Streamlit Community Cloud

1. Create a GitHub repository named `omnibrain-zero-plus`.
2. Upload the complete contents of this folder (including `.streamlit/config.toml`).
3. Sign in to [Streamlit Community Cloud](https://share.streamlit.io/).
4. Create an app from your repository and set the main file to `app.py`.
5. Deploy.
6. In the app, open **Settings** and add a free-tier Gemini API key from [Google AI Studio](https://aistudio.google.com/apikey).
7. Optional: add an OpenRouter key and choose a model that is explicitly free in its current catalog at [OpenRouter Models](https://openrouter.ai/models).

## Run locally (optional)

This is not required for cloud deployment.

```bash
pip install -r requirements.txt
streamlit run app.py
```

## Privacy and data persistence

- Never commit API keys.
- Keys entered in Settings are held in Streamlit session state; they are not stored in the repository or SQLite.
- Conversations, memories, and uploaded document text are stored in `omnibrain.db`.
- Free cloud hosts may reset local files during restarts/rebuilds. This starter therefore does not guarantee permanent cloud memory. Back up data or add a persistent database with a verified free tier.
- Do not upload sensitive documents to a public/shared deployment.
- This starter has no user authentication. Keep the deployed URL private or add authentication before sharing it.

## Research caveat

The Research Desk uses the `ddgs` package against a public search service. It may be rate-limited, blocked, or change behavior. Search snippets are not proof; verify important claims against the linked source pages.

## License

MIT.
