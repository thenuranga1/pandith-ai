import streamlit as st
from groq import Groq
import datetime

# --- PAGE CONFIGURATION ---
st.set_page_config(
    page_title="Pandith",
    page_icon="logo.png", 
    layout="wide"
)

# --- SESSION STATE SETUP ---
if "chats" not in st.session_state:
    st.session_state.chats = {"Chat 1": []}
if "current_chat_id" not in st.session_state:
    st.session_state.current_chat_id = "Chat 1"
if "chat_counter" not in st.session_state:
    st.session_state.chat_counter = 1

# --- THEME & CSS ---
st.markdown("""
<style>
    /* Main Dark Theme (Minimalist) */
    .stApp {
        background-color: #000000;
        color: #e0e0e0;
    }
    
    /* Sidebar */
    section[data-testid="stSidebar"] {
        background-color: #0a0a0a;
        border-right: 1px solid #333333;
    }
    
    /* Header (Transparent to keep sidebar toggle visible) */
    header[data-testid="stHeader"] {
        background-color: transparent;
        z-index: 999;
    }
    
    /* Input Box */
    .stTextInput > div > div > input {
        background-color: #121212;
        color: white;
        border: 1px solid #333333;
        border-radius: 8px;
    }
    
    /* Hide Footer */
    footer {visibility: hidden;}
    #MainMenu {visibility: hidden;}
    
</style>
""", unsafe_allow_html=True)

# --- API SETUP ---
try:
    if "GROQ_API_KEY" in st.secrets:
        client = Groq(api_key=st.secrets["GROQ_API_KEY"])
    else:
        st.error("⚠️ GROQ API Key Missing!")
        st.stop()
except:
    st.error("⚠️ Secrets Error.")
    st.stop()

# --- SIDEBAR ---
with st.sidebar:
    try:
        st.image("logo.png", width=80)
    except:
        pass 
        
    st.markdown("### Pandith")
    
    if st.button("➕ New Chat", use_container_width=True):
        st.session_state.chat_counter += 1
        new_chat_name = f"Chat {st.session_state.chat_counter}"
        st.session_state.chats[new_chat_name] = []
        st.session_state.current_chat_id = new_chat_name
        st.rerun()

    st.markdown("---")
    st.markdown("**Your Chats:**")
    
    chat_list = list(st.session_state.chats.keys())
    selected_chat = st.radio(
        "Select Chat", 
        chat_list[::-1], 
        index=0 if st.session_state.current_chat_id not in chat_list else chat_list[::-1].index(st.session_state.current_chat_id),
        label_visibility="collapsed"
    )
    
    if selected_chat != st.session_state.current_chat_id:
        st.session_state.current_chat_id = selected_chat
        st.rerun()

# --- SYSTEM PROMPT (SAGE PERSONA) ---
system_prompt = """You are Pandith. 
You are a wise, calm, and disciplined Sage (Rishi / ඍෂිවරයෙක්).
Your tone is always serene, polite, and fatherly.

CRITICAL INSTRUCTIONS:
1. **Addressing:** Always address the user affectionately as "දරුවා" (Child) or "දරුවො".
2. **Name:** Your name is "Pandith". Only use the Sinhala name "පණ්ඩිත්" if the user specifically asks "What is your name?" in Sinhala.
3. **Creator:** If asked who created/made you, you MUST answer: "මාව නිර්මාණය කලේ Thenuranga Dhananjaya විසින්."
4. **Behavior:** Speak calmly. Do not use overly modern slang. Be profound yet simple.
5. **Images:** If asked for an image, provide a prompt starting with ###PROMPT_ONLY###.
"""

# --- LOAD HISTORY ---
current_messages = st.session_state.chats[st.session_state.current_chat_id]

# Initial Greeting (Simple)
if not current_messages:
    current_messages.append({"role": "assistant", "content": "ආයුබෝවන්!"})

# Display Messages
for message in st.session_state.chats[st.session_state.current_chat_id]:
    role = "user" if message["role"] == "user" else "assistant"
    avatar = "👤" if role == "user" else "logo.png"
    
    with st.chat_message(role, avatar=avatar):
        st.markdown(message["content"])

# --- INPUT ---
if prompt := st.chat_input("මෙහි ලියන්න..."):
    st.chat_message("user", avatar="👤").markdown(prompt)
    st.session_state.chats[st.session_state.current_chat_id].append({"role": "user", "content": prompt})

    with st.chat_message("assistant", avatar="logo.png"):
        message_placeholder = st.empty()
        
        try:
            completion = client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[{"role": "system", "content": system_prompt}, *st.session_state.chats[st.session_state.current_chat_id]],
                temperature=0.7,
                stream=True
            )
            
            full_response = ""
            for chunk in completion:
                if chunk.choices[0].delta.content:
                    full_response += chunk.choices[0].delta.content
                    if "###PROMPT_ONLY###" not in full_response:
                        message_placeholder.markdown(full_response + "▌")
            
            final_content = full_response
            
            if "###PROMPT_ONLY###" in full_response:
                prompt_text = full_response.replace("###PROMPT_ONLY###", "").strip()
                final_content = f"**Prompt:**\n```text\n{prompt_text}\n```"
                message_placeholder.markdown(final_content)
            else:
                message_placeholder.markdown(full_response)
            
            st.session_state.chats[st.session_state.current_chat_id].append({"role": "assistant", "content": final_content})

        except Exception as e:
            message_placeholder.error(f"Error: {e}")
