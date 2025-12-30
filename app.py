import streamlit as st
import google.generativeai as genai

# --- PAGE CONFIGURATION ---
st.set_page_config(
    page_title="Pandith AI",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- CUSTOM CSS (Pro & Minimalist UI) ---
st.markdown("""
<style>
    /* Main Background */
    .stApp {
        background-color: #0E1117;
        color: white;
    }
    
    /* Sidebar Background */
    section[data-testid="stSidebar"] {
        background-color: #161B22;
    }
    
    /* Chat Input Box */
    .stTextInput > div > div > input {
        background-color: #262730;
        color: white;
        border-radius: 20px;
    }

    /* Hide Streamlit Branding */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
</style>
""", unsafe_allow_html=True)

# --- API SETUP ---
try:
    if "GEMINI_API_KEY" in st.secrets:
        genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
    else:
        st.error("⚠️ API Key එක දාලා නෑ! කරුණාකර Streamlit Settings වලට API Key එක ඇතුලත් කරන්න.")
        st.stop()
except Exception as e:
    st.error(f"⚠️ Connection Error: {e}")

# --- SIDEBAR ---
with st.sidebar:
    st.title("Pandith AI 🧠")
    st.caption("Developed by a Sri Lankan Developer 🇱🇰")
    st.markdown("---")
    st.markdown("Pandith AI is designed to be smart, helpful, and culturally aware.")
    
    if st.button("Clear Chat / New Chat 🗑️"):
        st.session_state.messages = []
        st.rerun()
    
    st.markdown("---")
    st.markdown("Powered by **Gemini 1.5 Flash**")

# --- CHAT LOGIC ---

# Model Setup
model = genai.GenerativeModel(
    model_name="gemini-1.5-flash",
    system_instruction="You are Pandith AI (පණ්ඩිත් AI). You are a professional, highly intelligent, and minimal AI assistant made in Sri Lanka. You answer primarily in Sinhala but are fluent in English. Be concise, direct, and helpful. Do not mention you are from Google. You are Pandith AI."
)

# Initialize History
if "messages" not in st.session_state:
    st.session_state.messages = []
    # Welcome Message
    st.session_state.messages.append({
        "role": "model", 
        "parts": ["ආයුබෝවන්! මම Pandith AI. මම ඔයාට කොහොමද උදව් කරන්නෙ?"]
    })

# Display Chat History
for message in st.session_state.messages:
    role = "user" if message["role"] == "user" else "assistant"
    avatar = "👤" if role == "user" else "🧠"
    
    with st.chat_message(role, avatar=avatar):
        st.markdown(message["parts"][0])

# Chat Input & Response
if prompt := st.chat_input("ඔබේ ප්‍රශ්නය මෙතන අසන්න..."):
    # User Message
    st.chat_message("user", avatar="👤").markdown(prompt)
    st.session_state.messages.append({"role": "user", "parts": [prompt]})

    # AI Response
    with st.chat_message("assistant", avatar="🧠"):
        message_placeholder = st.empty()
        message_placeholder.markdown("සිතමින් පවතී... 💭")
        
        try:
            # Build history for context
            history = [
                {"role": m["role"], "parts": m["parts"]} 
                for m in st.session_state.messages 
                if m["role"] != "system"
            ]
            
            # Generate Answer
            chat = model.start_chat(history=history[:-1])
            response = chat.send_message(prompt)
            
            # Show Answer
            message_placeholder.markdown(response.text)
            st.session_state.messages.append({"role": "model", "parts": [response.text]})
            
        except Exception as e:
            message_placeholder.error(f"⚠️ Error: {e}")
