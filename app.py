import streamlit as st
from openai import OpenAI
from tavily import TavilyClient

# --- PAGE CONFIG ---
st.set_page_config(
    page_title="AI Kopi2Referral | Chatbot",
    page_icon="☕",
    layout="centered"
)

# --- APP HEADER ---
st.title("☕ AI Kopi2Referral Chatbot")
st.caption("Your simple, conversational route planner for landing jobs in Singapore through networking.")

# --- SIDEBAR FOR SECRETS ---
with st.sidebar:
    st.subheader("⚙️ Configuration")
    groq_key = st.secrets.get("GROQ_API_KEY", "") or st.text_input("Groq API Key", type="password")
    tavily_key = st.secrets.get("TAVILY_API_KEY", "") or st.text_input("Tavily Search API Key", type="password")
    
    st.divider()
    st.markdown("**How to use:**\n1. Type your target company & sector.\n2. Ask the bot for a connection script.\n3. Copy and use on LinkedIn!")

# --- INIT CLIENTS ---
client = OpenAI(
    api_key=groq_key,
    base_url="https://api.groq.com/openai/v1"
) if groq_key else None

tavily = TavilyClient(api_key=tavily_key) if tavily_key else None

# --- INITIALIZE CHAT HISTORY ---
if "messages" not in st.session_state:
    st.session_state.messages = [
        {
            "role": "assistant",
            "content": "👋 Hi there! I'm your Kopi2Referral AI strategist. Which Singapore industry or company are you targeting for your job hunt today?"
        }
    ]

# --- DISPLAY CHAT MESSAGES ---
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# --- CHAT INPUT & LOGIC ---
if prompt := st.chat_input("Type your target company, role, or question..."):
    # Append user message
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # Generate assistant response
    with st.chat_message("assistant"):
        if not client:
            response_text = "⚠️ Please enter your Groq API key in the sidebar to start chatting."
            st.markdown(response_text)
            st.session_state.messages.append({"role": "assistant", "content": response_text})
        else:
            with st.spinner("Thinking through the Kopi route..."):
                try:
                    # Optional live web search if user mentions a company
                    search_context = ""
                    if tavily and any(keyword in prompt.lower() for keyword in ["micron", "dbs", "shopee", "grab", "ncs", "fairprice", "st engineering"]):
                        search_res = tavily.search(query=f"{prompt} Singapore hiring news 2026", max_results=2)
                        search_context = "\n[Live Search Context]: " + str(search_res.get("results", []))

                    messages_payload = [
                        {
                            "role": "system",
                            "content": (
                                "You are the 'AI Kopi2Referral' chatbot. Your goal is to help job seekers "
                                "in Singapore bypass public job boards by building real relationships, "
                                "inviting people for casual kopi chats, and securing internal employee referrals. "
                                "Keep your tone conversational, warm, concise, and localized to Singapore workplace culture."
                            )
                        }
                    ] + [{"role": m["role"], "content": m["content"]} for m in st.session_state.messages]

                    if search_context:
                        messages_payload[-1]["content"] += search_context

                    completion = client.chat.completions.create(
                        model="qwen/qwen3.8-27b",
                        messages=messages_payload,
                        temperature=0.7
                    )
                    response_text = completion.choices[0].message.content
                except Exception as e:
                    response_text = f"Error communicating with LLM: {str(e)}"

                st.markdown(response_text)
                st.session_state.messages.append({"role": "assistant", "content": response_text})
