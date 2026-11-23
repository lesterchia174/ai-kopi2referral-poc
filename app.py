import streamlit as st
import pandas as pd
from datetime import datetime
from openai import OpenAI

# --- PAGE CONFIG ---
st.set_page_config(
    page_title="AI Kopi2Referral-Job hunt Route",
    page_icon="☕",
    layout="wide"
)

# --- CLOUD LLM PROVIDERS & MODES (AI SINGAPORE + GROQ) ---
CLOUD_LLM_MODES = {
    "🇸🇬 AI Singapore (Qwen-SEA-LION-v4.5-27B-IT)": {
        "provider": "AI Singapore",
        "base_url": "https://api.sea-lion.ai/v1",
        "model_id": "aisingapore/Qwen-SEA-LION-v4.5-27B-IT",
        "secret_name": "SEALION_API_KEY",
        "desc": "Locally tuned by AI Singapore. Best for authentic SG workplace tone, local hubs, and natural kopi-chat phrasing.",
        "temp": 0.7
    },
    "⚡ Groq Fast Qwen (qwen/qwen3.8-27b)": {
        "provider": "Groq",
        "base_url": "https://api.groq.com/openai/v1",
        "model_id": "qwen/qwen3.8-27b",
        "secret_name": "GROQ_API_KEY",
        "desc": "Ultra-fast inference (~450 tokens/sec) with reasoning & instruct capabilities. Best for instant LinkedIn comments & DMs.",
        "temp": 0.7
    },
    "🧠 Groq Deep Strategy (llama-3.3-70b-versatile)": {
        "provider": "Groq",
        "base_url": "https://api.groq.com/openai/v1",
        "model_id": "llama-3.3-70b-versatile",
        "secret_name": "GROQ_API_KEY",
        "desc": "70B parameter cloud model on Groq. Best for multi-step 2nd-degree referral strategies & consultant pitches.",
        "temp": 0.5
    }
}

# --- SINGAPORE INDUSTRY CONTEXTS ---
SG_SECTORS = {
    "IT & Tech (One-North / Changi Biz Park)": "Cloud, cybersecurity, AI governance, FinOps, software engineering",
    "Manufacturing (Semicon / Process / Precision)": "Wafer fab yield, equipment uptime, Woodlands/Tampines parks, Tuas, SSIA",
    "Digital Transformation (CBD / GovTech / SI)": "ERP/SAP rollouts, workflow automation, legacy modernization, SGTech",
    "Healthcare & MedTech (Novena / Outram / Tuas)": "Clinical ops, Synapxe/SingHealth/NHG workflows, regulatory & patient safety",
    "Supermarket & Retail (Logistics / Omnichannel)": "Cold-chain supply, heartland merchandising, category ops, SRA"
}

# --- SESSION STATE FOR ROUTE TRACKER ---
if "kopi_routes" not in st.session_state:
    st.session_state.kopi_routes = pd.DataFrame([
        {
            "Date": datetime.now().strftime("%Y-%m-%d"),
            "Insider Name": "Wei Jie (Sample)",
            "Company": "SG Target Tech",
            "Sector": "IT & Tech (One-North / Changi Biz Park)",
            "Current Route Stop": "Stop 2: Zero-Ask Connection DM",
            "Cloud Engine": "aisingapore/Qwen-SEA-LION-v4.5-27B-IT",
            "Next Kopi Action": "Follow up with industry article on Thursday"
        }
    ])

# --- SIDEBAR: CLOUD LLM SELECTOR & API KEYS ---
with st.sidebar:
    st.title("☕ AI Kopi2Referral")
    st.caption("Cloud PoC | AI Singapore & Groq")

    st.subheader("☁️ 1. Select Cloud LLM Mode")
    selected_mode_label = st.selectbox("Cloud Engine", list(CLOUD_LLM_MODES.keys()))
    active_llm = CLOUD_LLM_MODES[selected_mode_label]
    st.caption(f"_{active_llm['desc']}_")

    # Load API key from Streamlit Secrets or manual input based on selected provider
    secret_key_name = active_llm["secret_name"]
    api_key = st.secrets.get(secret_key_name, "") if secret_key_name in st.secrets else ""
    if not api_key:
        api_key = st.text_input(
            f"Enter {active_llm['provider']} API Key",
            type="password",
            help=f"Get free key from {'playground.sea-lion.ai' if active_llm['provider'] == 'AI Singapore' else 'console.groq.com'}"
        )

    st.divider()
    st.subheader("🇸🇬 2. Your Route Coordinates")
    selected_sector = st.selectbox("Singapore Sector", list(SG_SECTORS.keys()))
    my_role = st.text_input("Your Role / Skillset", placeholder="e.g., Process Engineer / Product Owner")
    my_hook = st.text_input("Shared SG Hook", placeholder="e.g., NTU grad, Jurong hub, 5 yrs yield ops")

# --- UNIFIED CLOUD CALL FUNCTION (OPENAI-COMPATIBLE) ---
def run_cloud_llm(prompt: str) -> str:
    if not api_key:
        return f"⚠️ Please enter your **{active_llm['provider']} API Key** in the left sidebar."
    try:
        client = OpenAI(
            api_key=api_key,
            base_url=active_llm["base_url"]
        )
        completion = client.chat.completions.create(
            model=active_llm["model_id"],
            messages=[
                {
                    "role": "system",
                    "content": (
                        "You are the 'AI Kopi2Referral-Job hunt Route' strategist for Singapore. "
                        "Help candidates bypass crowded job boards by turning cold industry contacts "
                        "into genuine friends through casual Singapore 'kopi chats' and value-first networking, "
                        "leading to internal employee referrals. Keep tone warm, peer-to-peer, and authentic to Singapore."
                    )
                },
                {"role": "user", "content": prompt}
            ],
            temperature=active_llm["temp"]
        )
        return completion.choices[0].message.content
    except Exception as e:
        return f"Cloud API Error ({active_llm['provider']} - {active_llm['model_id']}): {str(e)}"

# --- MAIN UI ---
st.title("☕ AI Kopi2Referral-Job hunt Route (Cloud PoC)")
st.markdown(
    f"**Provider:** `{active_llm['provider']}` | **Model:** `{active_llm['model_id']}` | **Sector:** `{selected_sector}`"
)

col_left, col_right = st.columns([1.2, 1])

with col_left:
    st.subheader("🗺️ Route Planner: Generate Your Next Move")
    route_step = st.select_slider(
        "Select Your Current Stop on the Kopi2Referral Route:",
        options=[
            "Stop 1: Social Radar Comment",
            "Stop 2: Zero-Ask Connection DM",
            "Stop 3: SG Kopi / Virtual Chat Invite",
            "Stop 4: Post-Kopi Value Drop",
            "Stop 5: Soft Referral / Consultant Pitch"
        ]
    )

    insider_name = st.text_input("Target Insider Name & Role", placeholder="e.g., Rachel Tan, Fab Process Lead")
    insider_company = st.text_input("Target Company", placeholder="e.g., GlobalFoundries / FairPrice / NCS")
    context_input = st.text_area(
        "Paste Recent LinkedIn Post, Company News, or Mutual Contact Info:",
        height=120,
        placeholder="e.g., Posted about automation upgrades in Tampines, or connected via mutual friend..."
    )

    if st.button("🚀 Generate Route Action", type="primary"):
        prompt = f"""
        Generate a step-by-step action and 2 ready-to-send scripts for this exact stage of the Kopi2Referral Route:
        - Route Stage: {route_step}
        - Singapore Sector: {selected_sector} ({SG_SECTORS[selected_sector]})
        - Candidate: {my_role} | Hook: {my_hook}
        - Target Insider: {insider_name} at {insider_company}
        - Context: {context_input}

        Provide:
        1. Strategic Goal for this specific stop (1-2 sentences).
        2. Option A: Ultra-short message (under 280 characters for LinkedIn connection note).
        3. Option B: Warm, natural Singapore peer message (mentioning local context/kopi where appropriate).
        """
        with st.spinner(f"Running {active_llm['model_id']} on {active_llm['provider']} Cloud..."):
            output = run_cloud_llm(prompt)
            st.markdown(output)

with col_right:
    st.subheader("📍 Active Kopi2Referral Tracker")
    with st.form("add_route_form"):
        c1, c2 = st.columns(2)
        f_name = c1.text_input("Insider Name")
        f_comp = c2.text_input("Company")
        f_stop = st.selectbox("Current Stop", [
            "Stop 1: Social Radar Comment",
            "Stop 2: Zero-Ask Connection DM",
            "Stop 3: SG Kopi / Virtual Chat Invite",
            "Stop 4: Post-Kopi Value Drop",
            "Stop 5: Soft Referral Unlocked"
        ])
        f_next = st.text_input("Next Action", placeholder="e.g., Invite for kopi at One-North")
        submitted = st.form_submit_button("➕ Log Contact on Route")

        if submitted and f_name and f_comp:
            new_entry = pd.DataFrame([{
                "Date": datetime.now().strftime("%Y-%m-%d"),
                "Insider Name": f_name,
                "Company": f_comp,
                "Sector": selected_sector,
                "Current Route Stop": f_stop,
                "Cloud Engine": active_llm["model_id"],
                "Next Kopi Action": f_next
            }])
            st.session_state.kopi_routes = pd.concat([st.session_state.kopi_routes, new_entry], ignore_index=True)
            st.success(f"Added {f_name} to your route!")

    edited_routes = st.data_editor(st.session_state.kopi_routes, num_rows="dynamic", use_container_width=True)
    st.session_state.kopi_routes = edited_routes

    st.download_button(
        label="📥 Export PoC Route CSV",
        data=edited_routes.to_csv(index=False).encode("utf-8"),
        file_name=f"kopi2referral_poc_{datetime.now().strftime('%Y%m%d')}.csv",
        mime="text/csv"
    )
