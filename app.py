import streamlit as st
from openai import OpenAI
from tavily import TavilyClient

# ─────────────────────────────────────────────────────────────
# PAGE CONFIG
# ─────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="AI Kopi2Referral | Chatbot",
    page_icon="☕",
    layout="centered",
)

st.title("☕ AI Kopi2Referral Chatbot")
st.caption(
    "Your simple, conversational route planner for landing jobs in "
    "Singapore through networking."
)

# ─────────────────────────────────────────────────────────────
# HELPER: safely read a secret, fall back to a text input
# ─────────────────────────────────────────────────────────────
def get_secret_or_input(secret_name: str, label: str) -> str:
    try:
        return st.secrets[secret_name]
    except (KeyError, FileNotFoundError):
        return st.text_input(label, type="password")


# ─────────────────────────────────────────────────────────────
# SIDEBAR — CONFIGURATION
# ─────────────────────────────────────────────────────────────
with st.sidebar:
    st.subheader("⚙️ Configuration")

    groq_key = get_secret_or_input("GROQ_API_KEY", "Groq API Key")
    tavily_key = get_secret_or_input("TAVILY_API_KEY", "Tavily Search API Key")

    st.divider()

    use_search = st.toggle(
        "🌐 Enable web search (Tavily)",
        value=True,
        help="Ground answers in live web results for companies, roles and events.",
    )

    st.divider()

    if st.button("🗑️ Clear chat", use_container_width=True):
        st.session_state.messages = []
        st.rerun()

    st.divider()
    st.markdown(
        "**How to use:**\n"
        "1. Type your target role / industry in the chat.\n"
        "2. The bot suggests a networking plan for Singapore.\n"
        "3. Ask follow-ups — it remembers the conversation."
    )

# ─────────────────────────────────────────────────────────────
# VALIDATE KEYS BEFORE BUILDING CLIENTS
# ─────────────────────────────────────────────────────────────
if not groq_key:
    st.warning("⚠️ Please provide a Groq API key in the sidebar.")
    st.stop()

if use_search and not tavily_key:
    st.warning("⚠️ Web search is on but no Tavily API key was provided.")
    st.stop()

# ─────────────────────────────────────────────────────────────
# CLIENTS
#   Groq is OpenAI-compatible → point the base_url at Groq.
# ─────────────────────────────────────────────────────────────
client = OpenAI(
    base_url="https://api.groq.com/openai/v1",
    api_key=groq_key,
)

tavily = TavilyClient(api_key=tavily_key) if use_search else None

MODEL = "openai/gpt-oss-120b"

SYSTEM_PROMPT = (
    "You are 'Kopi2Referral', a warm, practical career-networking coach for "
    "people looking for jobs in Singapore. You help the user build a realistic "
    "networking route: who to meet, where to meet them (events, communities, "
    "coffee chats), what to say, and how to follow up. Keep answers concise, "
    "conversational and Singapore-specific (mention local communities, "
    "co-working spaces, MRT-friendly venues where relevant). Use any supplied "
    "web-search context to ground recommendations, and cite source URLs inline "
    "when you use them."
)

# ─────────────────────────────────────────────────────────────
# CHAT STATE
# ─────────────────────────────────────────────────────────────
if "messages" not in st.session_state:
    st.session_state.messages = []

# ─────────────────────────────────────────────────────────────
# RENDER EXISTING HISTORY
# ─────────────────────────────────────────────────────────────
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# ─────────────────────────────────────────────────────────────
# OPTIONAL: TAVILY SEARCH → CONTEXT STRING
# ─────────────────────────────────────────────────────────────
def build_search_context(query: str) -> str:
    if not tavily:
        return ""
    try:
        results = tavily.search(query=query, max_results=4).get("results", [])
    except Exception as e:  # network / auth / quota errors
        st.toast(f"Search failed: {e}", icon="⚠️")
        return ""

    if not results:
        return ""

    lines = ["### Web search context"]
    for i, r in enumerate(results, 1):
        title = r.get("title", "Untitled")
        url = r.get("url", "")
        snippet = (r.get("content") or "").strip().replace("\n", " ")
        if len(snippet) > 400:
            snippet = snippet[:400] + "…"
        lines.append(f"{i}. **{title}** — {url}\n   {snippet}")
    return "\n".join(lines)

# ─────────────────────────────────────────────────────────────
# CHAT INPUT
# ─────────────────────────────────────────────────────────────
if prompt := st.chat_input("e.g. I'm a fresh grad targeting fintech product roles…"):

    # 1. Show + store the user message
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # 2. Build the payload for the LLM
    payload = [{"role": "system", "content": SYSTEM_PROMPT}]

    # Only the LAST user turn needs fresh search context.
    if use_search:
        with st.spinner("Searching the web…"):
            context = build_search_context(prompt)
        if context:
            payload.append(
                {"role": "system", "content": f"Useful live context:\n{context}"}
            )

    payload.extend(st.session_state.messages)

    # 3. Stream the assistant reply
    with st.chat_message("assistant"):
        try:
            stream = client.chat.completions.create(
                model=MODEL,
                messages=payload,
                temperature=0.6,
                stream=True,
            )
            answer = st.write_stream(
                chunk.choices[0].delta.content or ""
                for chunk in stream
                if chunk.choices and chunk.choices[0].delta.content
            )
        except Exception as e:
            answer = f"⚠️ **Error calling Groq:** `{e}`"
            st.error(answer)

    # 4. Persist assistant reply
    st.session_state.messages.append({"role": "assistant", "content": answer})
