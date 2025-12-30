import streamlit as st
from groq import Groq

# --- PAGE CONFIGURATION ---
st.set_page_config(
    page_title="Pandith AI",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- GLASSMORPHISM CSS (THE NEXT LEVEL UI) ---
st.markdown("""
<style>
    /* 1. Animated Background */
    @keyframes gradient-animation {
        0% { background-position: 0% 50%; }
        50% { background-position: 100% 50%; }
        100% { background-position: 0% 50%; }
    }
    
    .stApp {
        background: linear-gradient(-45deg, #0f0c29, #302b63, #24243e, #141e30);
        background-size: 400% 400%;
        animation: gradient-animation 15s ease infinite;
        color: white;
    }

    /* 2. Sidebar Glass Effect */
    section[data-testid="stSidebar"] {
        background-color: rgba(0, 0, 0, 0.3) !important; /* Semi-transparent */
        backdrop-filter: blur(15px); /* Blur effect */
        border-right: 1px solid rgba(255, 255, 255, 0.1);
    }
    
    /* 3. Chat Input - Floating Glass Bar */
    .stTextInput {
        position: fixed;
        bottom: 40px;
        left: 50%;
        transform: translateX(-50%);
        width: 70%;
        z-index: 999;
    }
    
    .stTextInput > div > div > input {
        background-color: rgba(255, 255, 255, 0.1);
        color: white;
        border: 1px solid rgba(255, 255, 255, 0.2);
        border-radius: 30px;
        backdrop-filter: blur(10px);
        padding: 15px 20px;
        font-size: 16px;
        box-shadow: 0 8px 32px 0 rgba(31, 38, 135, 0.37);
    }
    
    .stTextInput > div > div > input:focus {
        border-color: #00d2ff;
        box-shadow: 0 0 15px rgba(0, 210, 255, 0.5);
    }

    /* 4. Hide Default Streamlit Elements */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    
    /* 5. Custom Code Block Style */
    code {
        color: #00d2ff;
        background-color: rgba(0,0,0,0.5);
        border-radius: 5px;
        padding: 2px 5px;
    }
    
    /* 6. Buttons */
    div.stButton > button {
        background: linear-gradient(90deg, #00d2ff 0%, #3a7bd5 100%);
        color: white;
        border: none;
        border-radius: 20px;
        padding: 10px 20px;
        font-weight: bold;
        transition: all 0.3s ease;
    }
    div.stButton > button:hover {
        transform: scale(1.05);
        box-shadow: 0 0 20px rgba(0, 210, 255, 0.6);
    }
    
    /* Adjust main container to not hide behind fixed input */
    .main .block-container {
        padding-bottom: 120px; 
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
    st.markdown("<p style='color: rgba(255,255,255,0.7);'>Next Gen Sri Lankan AI</p>", unsafe_allow_html=True)
    st.markdown("---")
    st.success("✅ Engine: **Llama 3.3 (Groq)**")
    st.info("🎨 UI: **Glassmorphism v2.0**")
    
    st.markdown("---")
    if st.button("Clear Chat 🗑️"):
        st.session_state.messages = []
        st.rerun()

# --- CHAT LOGIC ---

# System Instruction
system_prompt = """You are Pandith AI (පණ්ඩිත් AI), a futuristic and advanced AI assistant.
Answer primarily in Sinhala.
CRITICAL: If the user asks for an image, do NOT generate one. Instead, generate a highly detailed English prompt starting with '###PROMPT_ONLY###'."""

if "messages" not in st.session_state:
    st.session_state.messages = []
    st.session_state.messages.append({"role": "assistant", "content": "ආයුබෝවන්! මම Pandith AI. අලුත් මුහුණුවරකින් මම ඔබව සාදරයෙන් පිළිගන්නවා. 😎"})

# Display History
for message in st.session_state.messages:
    role = "user" if message["role"] == "user" else "assistant"
    avatar = "👤" if role == "user" else "🧠"
    
    with st.chat_message(role, avatar=avatar):
        st.markdown(message["content"])

# Input
if prompt := st.chat_input("මෙහි ලියන්න..."):
    # User Message
    st.chat_message("user", avatar="👤").markdown(prompt)
    st.session_state.messages.append({"role": "user", "content": prompt})

    # AI Response
    with st.chat_message("assistant", avatar="🧠"):
        message_placeholder = st.empty()
        message_placeholder.markdown("Searching Neural Net... ⚡")
        
        try:
            completion = client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[
                    {"role": "system", "content": system_prompt},
                    *st.session_state.messages
                ],
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
                final_output = f"🌌 **Image Prompt Generated:**\n\n```text\n{prompt_text}\n```\n_Copy this to Midjourney or Firefly_"
                message_placeholder.markdown(final_output)
                st.session_state.messages.append({"role": "assistant", "content": final_output})
            else:
                message_placeholder.markdown(full_response)
                st.session_state.messages.append({"role": "assistant", "content": full_response})

        except Exception as e:
            message_placeholder.error(f"System Malfunction: {e}")
