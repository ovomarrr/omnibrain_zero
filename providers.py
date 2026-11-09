import requests
import streamlit as st

def configured_providers():
    result = []
    if st.session_state.get("gemini_key"):
        result.append("gemini")
    if st.session_state.get("openrouter_key"):
        result.append("openrouter")
    return result

def provider_label(provider):
    return {"gemini": "Google Gemini", "openrouter": "OpenRouter"}.get(provider, provider)

def ask(provider, prompt, history=None):
    history = history or []
    if provider == "gemini":
        key = st.session_state.get("gemini_key", "")
        model = st.session_state.get("gemini_model", "gemini-2.5-flash")
        contents = []
        for item in history[-12:]:
            role = "model" if item["role"] == "assistant" else "user"
            contents.append({"role": role, "parts": [{"text": item["content"]}]})
        contents.append({"role": "user", "parts": [{"text": prompt}]})
        url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent"
        r = requests.post(url, params={"key": key}, json={"contents": contents,
            "generationConfig": {"temperature": 0.65, "maxOutputTokens": 4096}}, timeout=90)
        if r.status_code != 200:
            raise RuntimeError(f"Gemini error {r.status_code}: {r.text[:600]}")
        data = r.json()
        try:
            return data["candidates"][0]["content"]["parts"][0]["text"]
        except (KeyError, IndexError):
            raise RuntimeError("Gemini returned no text. Check model availability or safety filters.")
    if provider == "openrouter":
        key = st.session_state.get("openrouter_key", "")
        model = st.session_state.get("openrouter_model", "openrouter/free")
        messages = [{"role": x["role"], "content": x["content"]} for x in history[-12:]]
        messages.append({"role": "user", "content": prompt})
        r = requests.post("https://openrouter.ai/api/v1/chat/completions",
            headers={"Authorization": f"Bearer {key}", "Content-Type": "application/json",
                     "X-Title": "OmniBrain Zero Plus"},
            json={"model": model, "messages": messages, "temperature": 0.65}, timeout=120)
        if r.status_code != 200:
            raise RuntimeError(f"OpenRouter error {r.status_code}: {r.text[:600]}")
        return r.json()["choices"][0]["message"]["content"]
    raise ValueError("Unknown provider.")
