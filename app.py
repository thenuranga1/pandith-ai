import streamlit as st
import google.generativeai as genai

# Page Setup (Professional & Minimalist)
st.set_page_config(page_title="Pandith AI", page_icon="🧠", layout="centered")

# Custom CSS for Minimalist Look
st.markdown("""
<style>
    .stApp {
        background-color: #0e1117;
        color: #ffffff;
    }
    .stTextInput > div > div > input {
        background-color: #262730;
        color: #ffffff;
    }
</style>
""", unsafe_allow_html=True)

# Title
st.title("Pandith AI 🧠")
st.caption("Developed by a Sri Lankan Developer 🇱🇰 | Powered by Gemini")

# API Key Handling (Secure)
try:
    if "GEMINI_API_KEY" in st.secrets:
        genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
    else:
        st.error("API Key එක දාලා නෑ! කරුණාකර Settings වලට API Key එක ඇතුලත් කරන්න.")
        st.stop()
except Exception as e:
    st.error(f"Error: {e}")

# Model Configuration
model = genai.GenerativeModel(
    model_name="gemini-1.5-flash",
    system_instruction="You are Pandith AI (පණ්ඩිත් AI), a helpful, professional, and minimalist AI assistant developed in Sri Lanka. You primarily answer in Sinhala, but you are fluent in English as well. Your tone is friendly, respectful, and wise. Keep answers concise and clear."
)

# Initialize Chat History
if "messages" not in st.session_state:
    st.session_state.messages = []
    # Welcome Message
    welcome_msg = "ආයුබෝවන්! මම Pandith AI. මම ඔයාට කොහොමද උදව් කරන්නෙ?"
    st.session_state.messages.append({"role": "model", "parts": [welcome_msg]})

# Display Chat History
for message in st.session_state.messages:
    role = "user" if message["role"] == "user" else "assistant"
    with st.chat_message(role):
        st.markdown(message["parts"][0])

# Chat Input & Processing
if prompt := st.chat_input("මෙතන ඔබේ ප්‍රශ්නය අසන්න..."):
    # Show User Message
    st.chat_message("user").markdown(prompt)
    st.session_state.messages.append({"role": "user", "parts": [prompt]})

    # Generate Response
    with st.chat_message("assistant"):
        message_placeholder = st.empty()
        message_placeholder.markdown("සිතමින් පවතී... 🧠")
        
        try:
            # Create chat session with history
            history = [
                {"role": m["role"], "parts": m["parts"]} 
                for m in st.session_state.messages 
                if m["role"] != "system"
            ]
            chat = model.start_chat(history=history[:-1])
            response = chat.send_message(prompt)
            
            # Display Response
            message_placeholder.markdown(response.text)
            st.session_state.messages.append({"role": "model", "parts": [response.text]})
            
        except Exception as e:
            message_placeholder.error("සමාවෙන්න, පොඩි ගැටළුවක් ආවා. කරුණාකර නැවත උත්සාහ කරන්න.")
