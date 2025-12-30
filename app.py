import streamlit as st
from groq import Groq

# --- PAGE CONFIGURATION ---
st.set_page_config(
    page_title="Pandith AI",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- CUSTOM CSS ---
st.markdown("""
<style>
    .stApp { background-color: #0E1117; color: white; }
    section[data-testid="stSidebar"] { background-color: #161B22; }
    .stTextInput > div > div > input { background-color: #262730; color: white; border-radius: 20px; }
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
</style>
""", unsafe_allow_html=True)

# --- API SETUP ---
try:
    if "GROQ_API_KEY" in st.secrets:
        client = Groq(api_key=st.secrets["GROQ_API_KEY"])
    else:
        st.error("⚠️ API Key එක දාලා නෑ! Settings වලට GROQ_API_KEY එක දාන්න.")
        st.stop()
except Exception as e:
    st.error(f"⚠️ Connection Error: {e}")

# --- SIDEBAR ---
with st.sidebar:
    st.title("Pandith AI 🧠")
    st.caption("Developed by a Sri Lankan Developer 🇱🇰")
    st.markdown("---")
    
    if st.button("Clear Chat / New Chat 🗑️"):
        st.session_state.messages = []
        st.rerun()
    
    st.markdown("---")
    st.markdown("Powered by **Llama 3.3 (Groq)**")

# --- CHAT LOGIC ---
if "messages" not in st.session_state:
    st.session_state.messages = []
    st.session_state.messages.append({
        "role": "assistant", 
        "content": "ආයුබෝවන්! මම Pandith AI. මම අලුත්ම Llama 3.3 තාක්ෂණයෙන් බලගැන්වී ඇත. ඔබට කොහොමද උදව් කරන්නෙ?"
    })

for message in st.session_state.messages:
    role = "user" if message["role"] == "user" else "assistant"
    avatar = "👤" if role == "user" else "🧠"
    with st.chat_message(role, avatar=avatar):
        st.markdown(message["content"])

if prompt := st.chat_input("ඔබේ ප්‍රශ්නය මෙතන අසන්න..."):
    st.chat_message("user", avatar="👤").markdown(prompt)
    st.session_state.messages.append({"role": "user", "content": prompt})

    with st.chat_message("assistant", avatar="🧠"):
        message_placeholder = st.empty()
        message_placeholder.markdown("සිතමින් පවතී... ⚡")
        
        try:
            # Generate Answer using NEW MODEL
            completion = client.chat.completions.create(
                model="llama-3.3-70b-versatile",  # <--- මම මෙන්න මේක වෙනස් කලා අලුත් එකට
                messages=[
                    {"role": "system", "content": "You are Pandith AI (පණ්ඩිත් AI), a helpful AI assistant. You answer primarily in Sinhala. If the question is in English, answer in English. Be concise and helpful."},
                    *st.session_state.messages
                ],
                temperature=0.7,
                max_tokens=1024,
                top_p=1,
                stream=True,
                stop=None,
            )
            
            full_response = ""
            for chunk in completion:
                if chunk.choices[0].delta.content:
                    full_response += chunk.choices[0].delta.content
                    message_placeholder.markdown(full_response + "▌")
            
            message_placeholder.markdown(full_response)
            st.session_state.messages.append({"role": "assistant", "content": full_response})
            
        except Exception as e:
            message_placeholder.error(f"⚠️ Error: {e}")
