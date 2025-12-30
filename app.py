import streamlit as st
from groq import Groq

# --- PAGE CONFIGURATION ---
st.set_page_config(
    page_title="Pandith AI",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- CUSTOM CSS (Pro & Minimalist) ---
st.markdown("""
<style>
    .stApp { background-color: #0E1117; color: white; }
    section[data-testid="stSidebar"] { background-color: #161B22; }
    .stTextInput > div > div > input { background-color: #262730; color: white; border-radius: 20px; }
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    /* Code block style for prompts */
    code { color: #ff4b4b; font-weight: bold; }
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
    st.caption("Developed by a Sri Lankan Developer 🇱🇰")
    st.markdown("---")
    st.markdown("✅ **Engine:** Llama 3.3 (Groq)")
    st.markdown("✅ **Focus:** Text & Prompts")
    
    if st.button("Clear Chat / New Chat 🗑️"):
        st.session_state.messages = []
        st.rerun()

# --- CHAT LOGIC ---

# System Instruction: Generate prompts if asked for images
system_prompt = """You are Pandith AI (පණ්ඩිත් AI), an advanced AI assistant.
Answer primarily in Sinhala.
CRITICAL INSTRUCTION: If the user asks for an image, picture, or drawing, DO NOT say you cannot generate images. Instead, generate a highly detailed, creative English prompt for that image.
Start your response with "###PROMPT_ONLY###" followed by the English prompt."""

if "messages" not in st.session_state:
    st.session_state.messages = []
    st.session_state.messages.append({"role": "assistant", "content": "ආයුබෝවන්! මම Pandith AI. මට ඔබ හා සිංහලෙන් කතා කළ හැකියි. ඔබට යම් පින්තූරයක් අවශ්‍ය නම්, ඒ සඳහා අවශ්‍ය විස්තරය (Prompt) මට සාදා දිය හැකිය."})

# Display History
for message in st.session_state.messages:
    role = "user" if message["role"] == "user" else "assistant"
    avatar = "👤" if role == "user" else "🧠"
    with st.chat_message(role, avatar=avatar):
        st.markdown(message["content"])

# Input
if prompt := st.chat_input("ඔබේ ප්‍රශ්නය මෙතන අසන්න..."):
    st.chat_message("user", avatar="👤").markdown(prompt)
    st.session_state.messages.append({"role": "user", "content": prompt})

    with st.chat_message("assistant", avatar="🧠"):
        message_placeholder = st.empty()
        message_placeholder.markdown("සිතමින් පවතී... ⚡")
        
        try:
            # Get response from Groq
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

            # Check if it's an image prompt request
            if "###PROMPT_ONLY###" in full_response:
                prompt_text = full_response.replace("###PROMPT_ONLY###", "").strip()
                
                # Format the output nicely for copying
                final_output = f"ඔබ ඉල්ලූ පින්තූරය සඳහා විස්තරය (Prompt) මෙන්න. මෙය Copy කරගෙන වෙනත් මෙවලමක් භාවිතයෙන් පින්තූරය සාදාගන්න:\n\n```text\n{prompt_text}\n```"
                
                message_placeholder.markdown(final_output)
                st.session_state.messages.append({"role": "assistant", "content": final_output})
            else:
                # Normal text response
                message_placeholder.markdown(full_response)
                st.session_state.messages.append({"role": "assistant", "content": full_response})

        except Exception as e:
            message_placeholder.error(f"System Error: {e}")
