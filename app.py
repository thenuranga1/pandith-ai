import streamlit as st
import google.generativeai as genai

# --- PAGE CONFIGURATION ---
st.set_page_config(
    page_title="Pandith AI",
    page_icon="🧠",
    layout="wide"
)

# --- CUSTOM CSS ---
st.markdown("""
<style>
    .stApp { background-color: #0E1117; color: white; }
    section[data-testid="stSidebar"] { background-color: #161B22; }
    .stTextInput > div > div > input { background-color: #262730; color: white; }
</style>
""", unsafe_allow_html=True)

# --- API SETUP & DEBUGGING ---
try:
    if "GEMINI_API_KEY" in st.secrets:
        genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
    else:
        st.error("⚠️ API Key එක දාලා නෑ! Streamlit Settings වලට ගිහින් Secrets හදන්න.")
        st.stop()
except Exception as e:
    st.error(f"⚠️ Key Error: {e}")

# --- SIDEBAR ---
with st.sidebar:
    st.title("Pandith AI 🇱🇰")
    st.markdown("Developed by a Sri Lankan Developer")
    if st.button("Clear Chat 🗑️"):
        st.session_state.messages = []
        st.rerun()

# --- CHAT LOGIC ---
model = genai.GenerativeModel("gemini-pro")

if "messages" not in st.session_state:
    st.session_state.messages = [{"role": "model", "parts": ["ආයුබෝවන්! මම Pandith AI. ඔබට කොහොමද උදව් කරන්නෙ?"]}]

for message in st.session_state.messages:
    role = "user" if message["role"] == "user" else "assistant"
    st.chat_message(role).markdown(message["parts"][0])

if prompt := st.chat_input("ඔබේ ප්‍රශ්නය මෙතන අසන්න..."):
    st.chat_message("user").markdown(prompt)
    st.session_state.messages.append({"role": "user", "parts": [prompt]})

    with st.chat_message("assistant"):
        message_placeholder = st.empty()
        try:
            # Generate Response
            history = [{"role": m["role"], "parts": m["parts"]} for m in st.session_state.messages if m["role"] != "system"]
            chat = model.start_chat(history=history[:-1])
            response = chat.send_message(prompt)
            
            message_placeholder.markdown(response.text)
            st.session_state.messages.append({"role": "model", "parts": [response.text]})
            
        except Exception as e:
            # HERE IS THE FIX: Show the REAL error
            st.error(f"⚠️ තාක්ෂණික දෝෂයක්: {e}")
