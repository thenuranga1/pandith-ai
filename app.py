import streamlit as st
from groq import Groq

# --- PAGE CONFIGURATION ---
st.set_page_config(
    page_title="Pandith AI",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- ULTIMATE GLASSMORPHISM CSS ---
st.markdown("""
<style>
    /* 1. Moving Gradient Background (Darker & Smoother) */
    @keyframes gradient-animation {
        0% { background-position: 0% 50%; }
        50% { background-position: 100% 50%; }
        100% { background-position: 0% 50%; }
    }
    
    .stApp {
        background: linear-gradient(-45deg, #000000, #1e1e1e, #232526, #414345);
        background-size: 400% 400%;
        animation: gradient-animation 15s ease infinite;
        color: #e0e0e0;
    }

    /* 2. SIDEBAR GLASS EFFECT (The Fix) */
    section[data-testid="stSidebar"] {
        background-color: rgba(255, 255, 255, 0.05); /* Very transparent white */
        backdrop-filter: blur(20px); /* Heavy Blur */
        border-right: 1px solid rgba(255, 255, 255, 0.1);
        box-shadow: 10px 0 30px rgba(0, 0, 0, 0.5);
    }
    
    /* Ensure text in sidebar is visible */
    section[data-testid="stSidebar"] h1, 
    section[data-testid="stSidebar"] h2, 
    section[data-testid="stSidebar"] h3, 
    section[data-testid="stSidebar"] p, 
    section[data-testid="stSidebar"] span {
        color: #ffffff !important;
        text-shadow: 0 0 10px rgba(0,0,0,0.5);
    }

    /* 3. Header & Menu Button (Make it transparent but VISIBLE) */
    header[data-testid="stHeader"] {
        background: transparent;
        z-index: 999;
    }
    /* Menu Button Color */
    button[kind="header"] {
        color: white !important;
        background-color: rgba(255,255,255,0.1);
        border-radius: 10px;
    }

    /* 4. Chat Input - Floating Neon Glass */
    .stTextInput {
        position: fixed;
        bottom: 30px;
        left: 50%;
        transform: translateX(-50%);
        width: 60%;
        z-index: 1000;
    }
    
    .stTextInput > div > div > input {
        background-color: rgba(0, 0, 0, 0.3);
        color: white;
        border: 1px solid rgba(255, 255, 255, 0.2);
        border-radius: 30px;
        backdrop-filter: blur(10px);
        padding: 12px 20px;
    }
    
    .stTextInput > div > div > input:focus {
        border-color: #00d2ff;
        box-shadow: 0 0 15px rgba(0, 210, 255, 0.4);
    }

    /* 5. Messages - Bubbles */
    .stChatMessage {
        background-color: rgba(255, 255, 255, 0.05);
        border: 1px solid rgba(255, 255, 255, 0.05);
        border-radius: 15px;
        padding: 10px;
        margin-bottom: 10px;
        backdrop-filter: blur(5px);
    }

    /* Hide Footer */
    footer {visibility: hidden;}
    
    /* Main container padding so input doesn't cover text */
    .main .block-container {
        padding-bottom: 100px;
    }

</style>
""", unsafe_allow_html=True)

# --- API SETUP ---
try:
    if "GROQ_API_KEY" in st.secrets:
        client = Groq(api_key=st.secrets["GROQ_API_KEY"])
    else:
        st.error("⚠️ GROQ API Key එක දාලා නෑ!")
        st.stop()
except:
    st.error("⚠️ Secrets හරියට සෙට් වෙලා නෑ.")
    st.stop()

# --- SIDEBAR ---
with st.sidebar:
    st.title("Pandith AI 🧠")
    st.markdown("---")
    st.info("✅ Engine: **Llama 3.3**")
    st.success("✨ UI: **Glassmorphism**")
    
    st.markdown("---")
    # Custom Glass Button
    if st.button("Clear Chat 🗑️", type="primary"):
        st.session_state.messages = []
        st.rerun()

# --- CHAT LOGIC ---
system_prompt = """You are Pandith AI (පණ්ඩිත් AI).
Answer primarily in Sinhala.
CRITICAL: If the user asks for an image, generate a prompt starting with '###PROMPT_ONLY###'."""

if "messages" not in st.session_state:
    st.session_state.messages = []
    st.session_state.messages.append({"role": "assistant", "content": "ආයුබෝවන්! මම Pandith AI. මම දැන් අලුත් Glass UI එකකින්."})

# Display History
for message in st.session_state.messages:
    role = "user" if message["role"] == "user" else "assistant"
    avatar = "👤" if role == "user" else "🧠"
    
    with st.chat_message(role, avatar=avatar):
        st.markdown(message["content"])

# Input
if prompt := st.chat_input("මෙහි ලියන්න..."):
    st.chat_message("user", avatar="👤").markdown(prompt)
    st.session_state.messages.append({"role": "user", "content": prompt})

    with st.chat_message("assistant", avatar="🧠"):
        message_placeholder = st.empty()
        message_placeholder.markdown("Processing... ⚡")
        
        try:
            completion = client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[{"role": "system", "content": system_prompt}, *st.session_state.messages],
                temperature=0.7,
                max_tokens=1024,
                stream=True
            )
            
            full_response = ""
            for chunk in completion:
                if chunk.choices[0].delta.content:
                    full_response += chunk.choices[0].delta.content
                    if "###PROMPT_ONLY###" not in full_response:
                        message_placeholder.markdown(full_response + "▌")

            if "###PROMPT_ONLY###" in full_response:
                prompt_text = full_response.replace("###PROMPT_ONLY###", "").strip()
                final_output = f"🎨 **Image Prompt:**\n```text\n{prompt_text}\n```"
                message_placeholder.markdown(final_output)
                st.session_state.messages.append({"role": "assistant", "content": final_output})
            else:
                message_placeholder.markdown(full_response)
                st.session_state.messages.append({"role": "assistant", "content": full_response})

        except Exception as e:
            message_placeholder.error(f"Error: {e}")
