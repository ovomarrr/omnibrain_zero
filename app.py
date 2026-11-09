import streamlit as st
from omnibrain.db import init_db, create_conversation, list_conversations, get_messages, save_message, rename_conversation, delete_conversation
from omnibrain.providers import configured_providers, ask, provider_label
from omnibrain.council import run_council
from omnibrain.memory import add_memory, list_memories, delete_memory, search_memories
from omnibrain.documents import ingest_document, list_documents, delete_document, search_documents
from omnibrain.research import web_search
from omnibrain.agents import DEFAULT_AGENTS, run_agent
from omnibrain.export import conversation_markdown

st.set_page_config(page_title="OmniBrain Zero+", page_icon="🧠", layout="wide", initial_sidebar_state="expanded")
init_db()

st.markdown("""
<style>
.stApp {background: radial-gradient(ellipse at 0% 0%, #172554 0%, #080d1c 43%, #050812 100%);}
.block-container {max-width: 1450px; padding-top: 1.4rem;}
div[data-testid="stSidebar"] {background: #080e1e;}
.ob-panel {background:rgba(17,28,55,.8);border:1px solid #293b70;border-radius:16px;padding:16px;margin:8px 0;}
.ob-small {color:#9fb0d3;font-size:.88rem}
div.stButton>button {border-radius:10px}
</style>
""", unsafe_allow_html=True)

if "active_id" not in st.session_state:
    rows = list_conversations()
    st.session_state.active_id = rows[0]["id"] if rows else create_conversation()
if "provider_keys" not in st.session_state:
    st.session_state.provider_keys = {}
if "custom_agents" not in st.session_state:
    st.session_state.custom_agents = DEFAULT_AGENTS.copy()

with st.sidebar:
    st.markdown("# 🧠 OmniBrain")
    st.caption("ZERO+  ·  AI command center")
    page = st.radio("Workspace", ["Chat", "AI Council", "Research", "Document Brain", "Memory Vault", "Agent Studio", "Settings", "About"])
    st.divider()
    providers = configured_providers()
    st.caption("CONNECTED MODELS")
    if providers:
        for p in providers:
            st.write(f"🟢 {provider_label(p)}")
    else:
        st.warning("No provider configured")
    st.divider()
    st.caption("Privacy-first · Free-tier compatible")

def choose_provider():
    options = configured_providers()
    if not options:
        st.warning("Connect at least one provider in Settings.")
        return None
    return st.selectbox("AI provider", options, format_func=provider_label, key="provider_choice")

def show_sources(results):
    for item in results:
        st.markdown(f"- [{item['title']}]({item['url']})")
        if item.get("snippet"):
            st.caption(item["snippet"])

if page == "Chat":
    st.title("OmniBrain")
    st.markdown("**Your unified AI workspace.** Ask, research, plan, create, and remember.")
    conversations = list_conversations()
    labels = {f'{r["title"][:55]}  ·  #{r["id"]}': r["id"] for r in conversations}
    left, right = st.columns([5, 1])
    with left:
        selected = st.selectbox("Conversation history", list(labels), index=list(labels.values()).index(st.session_state.active_id) if st.session_state.active_id in labels.values() else 0)
        st.session_state.active_id = labels[selected]
    with right:
        if st.button("＋ New chat", use_container_width=True):
            st.session_state.active_id = create_conversation()
            st.rerun()
    cid = st.session_state.active_id
    msgs = get_messages(cid)
    for m in msgs:
        with st.chat_message(m["role"]):
            st.markdown(m["content"])
    with st.expander("⚙️ Chat controls", expanded=False):
        p = choose_provider()
        use_memory = st.checkbox("Include relevant saved memories", True)
        use_docs = st.checkbox("Include relevant uploaded documents", True)
        system = st.text_area("Custom instructions (optional)", placeholder="Example: Be concise, show assumptions, and explain uncertainty.")
    prompt = st.chat_input("Message OmniBrain...")
    if prompt:
        save_message(cid, "user", prompt)
        with st.chat_message("user"):
            st.markdown(prompt)
        context_parts = []
        if use_memory:
            mems = search_memories(prompt, limit=5)
            if mems:
                context_parts.append("RELEVANT USER MEMORIES:\n" + "\n".join("- " + x["content"] for x in mems))
        if use_docs:
            docs = search_documents(prompt, limit=5)
            if docs:
                context_parts.append("RELEVANT UPLOADED DOCUMENT EXCERPTS:\n" + "\n".join(x["content"] for x in docs))
        history = [{"role": x["role"], "content": x["content"]} for x in msgs[-12:]]
        full_prompt = (system.strip() + "\n\n" if system.strip() else "") + ("\n\n".join(context_parts) + "\n\n" if context_parts else "") + prompt
        with st.chat_message("assistant"):
            try:
                with st.spinner("OmniBrain is thinking..."):
                    answer = ask(p, full_prompt, history)
                st.markdown(answer)
                save_message(cid, "assistant", answer)
                if len(msgs) == 0:
                    rename_conversation(cid, prompt[:65])
            except Exception as e:
                st.error(str(e))
                st.info("Your question was saved. Check Settings and provider quota, then retry.")
    if msgs:
        st.download_button("⬇️ Export conversation as Markdown", conversation_markdown(msgs), file_name=f"omnibrain-chat-{cid}.md", mime="text/markdown")

elif page == "AI Council":
    st.title("⚡ AI Council")
    st.write("Independent responses, optional cross-critique, and a final synthesis.")
    options = configured_providers()
    if len(options) < 1:
        st.warning("Configure at least one provider in Settings.")
    else:
        chosen = st.multiselect("Council members", options, default=options, format_func=provider_label)
        question = st.text_area("Council question", height=140, placeholder="Give the council a problem to solve...")
        critique = st.checkbox("Run a critique and revision round", value=True)
        if st.button("Convene council", type="primary", disabled=not question.strip() or not chosen):
            with st.spinner("Consulting council members..."):
                results, synthesis = run_council(chosen, question, critique=critique)
            for provider, result in results:
                with st.expander(f"🧠 {provider_label(provider)}", expanded=True):
                    st.markdown(result)
            st.markdown("## 🏆 Chief Intelligence")
            st.markdown(synthesis)

elif page == "Research":
    st.title("🌐 Research Desk")
    st.write("Search public web results and ask an AI to analyze them. Search availability and results depend on the free source.")
    query = st.text_input("What should OmniBrain research?")
    if st.button("Search the web", type="primary", disabled=not query.strip()):
        with st.spinner("Searching public sources..."):
            results = web_search(query, max_results=8)
        if results:
            show_sources(results)
            st.session_state.research_results = results
        else:
            st.warning("No results returned. The public search source may be unavailable or rate-limited.")
    results = st.session_state.get("research_results", [])
    if results:
        st.divider()
        p = choose_provider()
        if st.button("Analyze these sources", disabled=not p):
            source_text = "\n\n".join(f"TITLE: {x['title']}\nURL: {x['url']}\nSNIPPET: {x.get('snippet','')}" for x in results)
            with st.spinner("Analyzing sources..."):
                try:
                    analysis = ask(p, "Analyze these search results. Separate supported facts from claims that need verification. Cite URLs inline. Explain gaps and uncertainty.\n\n" + source_text)
                    st.markdown(analysis)
                except Exception as e:
                    st.error(str(e))

elif page == "Document Brain":
    st.title("📚 Document Brain")
    st.write("Upload text, Markdown, PDF, or DOCX files. Text is extracted and stored in the app database for keyword retrieval.")
    upload = st.file_uploader("Add a document", type=["txt", "md", "pdf", "docx"])
    if upload and st.button("Index document"):
        try:
            name, count = ingest_document(upload.name, upload.getvalue())
            st.success(f"Indexed {name}: {count} text chunks.")
        except Exception as e:
            st.error(f"Could not index document: {e}")
    docs = list_documents()
    if docs:
        st.subheader("Indexed documents")
        for d in docs:
            c1, c2 = st.columns([6, 1])
            c1.write(f"📄 **{d['filename']}** · {d['chunks']} chunks")
            if c2.button("Delete", key=f"docdel{d['id']}"):
                delete_document(d["id"])
                st.rerun()
        question = st.text_input("Ask a question about your documents")
        p = choose_provider()
        if st.button("Ask documents", disabled=not question.strip() or not p):
            matches = search_documents(question, limit=8)
            if matches:
                context = "\n\n".join(x["content"] for x in matches)
                with st.spinner("Reading relevant excerpts..."):
                    try:
                        st.markdown(ask(p, "Answer using the document excerpts below. If the answer is not present, say so. Mention document names when available.\n\n" + context + "\n\nQUESTION: " + question))
                    except Exception as e:
                        st.error(str(e))
            else:
                st.info("No matching excerpts found.")

elif page == "Memory Vault":
    st.title("🗃️ Memory Vault")
    st.write("Add, review, search, and delete information you explicitly want OmniBrain to retain.")
    value = st.text_area("New memory", placeholder="A project, preference, or useful fact...")
    if st.button("Save memory", type="primary", disabled=not value.strip()):
        add_memory(value)
        st.success("Saved.")
        st.rerun()
    search = st.text_input("Search saved memories")
    memories = search_memories(search, limit=100) if search else list_memories()
    for m in memories:
        a, b = st.columns([6, 1])
        a.markdown(f'<div class="ob-panel">{m["content"]}<div class="ob-small">{m["created_at"][:16]}</div></div>', unsafe_allow_html=True)
        if b.button("Delete", key=f"mem{m['id']}"):
            delete_memory(m["id"])
            st.rerun()

elif page == "Agent Studio":
    st.title("🤖 Agent Studio")
    st.write("Choose a specialist or create your own role-specific assistant.")
    if "agent_name" not in st.session_state:
        st.session_state.agent_name = ""
    name = st.text_input("New agent name", placeholder="e.g. Startup Strategist")
    instructions = st.text_area("Agent instructions", placeholder="Define its role, workflow, constraints, and output style.")
    if st.button("Add custom agent", disabled=not name.strip() or not instructions.strip()):
        st.session_state.custom_agents[name.strip()] = instructions.strip()
        st.success("Agent added for this session.")
    agents = st.session_state.custom_agents
    if agents:
        agent_name = st.selectbox("Select an agent", list(agents))
        task = st.text_area("Task for this agent", height=120)
        p = choose_provider()
        if st.button("Run agent", type="primary", disabled=not task.strip() or not p):
            with st.spinner(f"{agent_name} is working..."):
                try:
                    st.markdown(run_agent(p, agent_name, agents[agent_name], task))
                except Exception as e:
                    st.error(str(e))
        with st.expander("View agent instructions"):
            st.code(agents[agent_name])

elif page == "Settings":
    st.title("⚙️ Provider Settings")
    st.warning("Use only provider models currently marked free. Free tiers have quotas and can change. This app never requires paid API access.")
    st.subheader("Google Gemini")
    gkey = st.text_input("Gemini API key", type="password", value=st.session_state.get("gemini_key", ""))
    gmodel = st.text_input("Gemini model ID", value=st.session_state.get("gemini_model", "gemini-2.5-flash"))
    st.markdown("[Get a key from Google AI Studio](https://aistudio.google.com/apikey)")
    st.subheader("OpenRouter (optional)")
    okey = st.text_input("OpenRouter API key", type="password", value=st.session_state.get("openrouter_key", ""))
    omodel = st.text_input("OpenRouter model ID", value=st.session_state.get("openrouter_model", "openrouter/free"), help="Only use a model explicitly shown as free in the current catalog.")
    st.markdown("[Browse OpenRouter models](https://openrouter.ai/models)")
    if st.button("Save provider settings", type="primary"):
        st.session_state.gemini_key = gkey.strip()
        st.session_state.gemini_model = gmodel.strip() or "gemini-2.5-flash"
        st.session_state.openrouter_key = okey.strip()
        st.session_state.openrouter_model = omodel.strip() or "openrouter/free"
        st.success("Saved in this browser session. For persistent deployment configuration, use your host's encrypted secrets manager.")
    st.caption("Keys are not saved to GitHub or the SQLite database. They may need to be re-entered after a session expires.")

elif page == "About":
    st.title("About OmniBrain Zero+")
    st.markdown("""
    **A free-first, cloud-hostable AI workspace.**

    Features: universal chat, AI Council, critique/revision, research desk, document Q&A, curated memory, specialist agents, and Markdown export.

    **Zero-fee design:** no paid services are required by the source code. Actual model inference requires a provider that offers a free quota. Hosting, search and free tiers may have restrictions or change.

    **Privacy:** uploaded documents, conversations, and memories are stored in the app's database. On ephemeral free hosting, that database may be reset. Do not upload sensitive information.
    """)
    st.code("Python + Streamlit + SQLite + provider APIs", language="text")
