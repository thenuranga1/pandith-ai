import streamlit as st
from groq import Groq
import datetime

# --- PAGE CONFIGURATION ---
st.set_page_config(
    page_title="Pandith (පණ්ඩිත්)",
    page_icon="logo.png", 
    layout="wide"
)

# --- SESSION STATE SETUP (Multi-Chat Logic) ---
if "chats" not in st.session_state:
    # මුල්ම Chat එක
    st.session_state.chats = {"Chat 1": []}
if "current_chat_id" not in st.session_state:
    st.session_state.current_chat_id = "Chat 1"
if "chat_counter" not in st.session_state:
    st.session_state.chat_counter = 1

# --- THEME & CSS ---
# Sidebar එක වැහුවම ආයෙ ගන්න පුලුවන් වෙන්න Header එක හැදුවා.
st.markdown("""
<style>
    /* Main Dark Theme */
    .stApp {
        background-color: #000000;
        color: #ffffff;
    }
    
    /* Sidebar Background */
    section[data-testid="stSidebar"] {
        background-color: #0a0a0a;
        border-right: 1px solid #333333;
    }
    
    /* Fix: Show Sidebar Toggle Button */
    header[data-testid="stHeader"] {
        background-color: transparent;
        z-index: 999;
    }
    /* Hide decorative line but keep the button */
    .stApp > header {
        background-color: transparent;
    }
    
    /* Input Box */
    .stTextInput > div > div > input {
        background-color: #121212;
        color: white;
        border: 1px solid #333333;
        border-radius: 8px;
    }
    
    /* Remove Streamlit Footer only */
    footer {visibility: hidden;}
    #MainMenu {visibility: hidden;} /* Hide 3 dots menu if you want */
    
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

# --- SIDEBAR: CHAT MANAGEMENT ---
with st.sidebar:
    # Logo & Name
    try:
        st.image("logo.png", width=80)
    except:
        pass # Logo එක නැත්නම් අවුලක් නෑ
        
    st.markdown("### Pandith (පණ්ඩිත්)")
    
    # New Chat Button
    if st.button("➕ New Chat", use_container_width=True):
        st.session_state.chat_counter += 1
        new_chat_name = f"Chat {st.session_state.chat_counter}"
        st.session_state.chats[new_chat_name] = []
        st.session_state.current_chat_id = new_chat_name
        st.rerun()

    st.markdown("---")
    st.markdown("**Your Chats:**")
    
    # Chat List (Radio Button to switch)
    chat_list = list(st.session_state.chats.keys())
    # Reverse list to show newest on top
    selected_chat = st.radio(
        "Select Chat", 
        chat_list[::-1], 
        index=0 if st.session_state.current_chat_id not in chat_list else chat_list[::-1].index(st.session_state.current_chat_id),
        label_visibility="collapsed"
    )
    
    # Update Current Chat ID
    if selected_chat != st.session_state.current_chat_id:
        st.session_state.current_chat_id = selected_chat
        st.rerun()

# --- SYSTEM PROMPT (BRAIN) ---
# මෙතන තමයි නිර්මාතෘගේ නම සහ Pandith ගේ නම කොටලා තියෙන්නෙ.
system_prompt = """You are Pandith (පණ්ඩිත්). You are a helpful, direct, and minimalist AI assistant. 
Answer primarily in Sinhala.

CRITICAL RULES:
1. Your name is ONLY "Pandith (පණ්ඩිත්)". Do not use "Pandith AI".
2. If the user asks who created/made/developed you, you MUST answer: "මාව නිර්මාණය කලේ Thenuranga Dhananjaya විසින්." (Created by Thenuranga Dhananjaya).
3. If asked for an image, provide a prompt starting with ###PROMPT_ONLY###.
"""

# --- LOAD CURRENT CHAT HISTORY ---
current_messages = st.session_state.chats[st.session_state.current_chat_id]

# Initial Greeting if empty
if not current_messages:
    current_messages.append({"role": "assistant", "content": "ආයුබෝවන්! මම පණ්ඩිත් (Pandith)."})

# Display History
for message in st.session_state.chats[st.session_state.current_chat_id]:
    role = "user" if message["role"] == "user" else "assistant"
    avatar = "👤" if role == "user" else "logo.png"
    
    with st.chat_message(role, avatar=avatar):
        st.markdown(message["content"])

# --- CHAT INPUT & LOGIC ---
if prompt := st.chat_input("මෙහි ලියන්න..."):
    # 1. Add User Message to UI & History
    st.chat_message("user", avatar="👤").markdown(prompt)
    st.session_state.chats[st.session_state.current_chat_id].append({"role": "user", "content": prompt})

    # 2. Generate AI Response
    with st.chat_message("assistant", avatar="logo.png"):
        message_placeholder = st.empty()
        
        try:
            # Send context to Groq
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
            
            # 3. Handle Output
            final_content = full_response
            
            if "###PROMPT_ONLY###" in full_response:
                prompt_text = full_response.replace("###PROMPT_ONLY###", "").strip()
                final_content = f"**Image Prompt:**\n```text\n{prompt_text}\n```"
                message_placeholder.markdown(final_content)
            else:
                message_placeholder.markdown(full_response)
            
            # 4. Save AI Message to History
            st.session_state.chats[st.session_state.current_chat_id].append({"role": "assistant", "content": final_content})

        except Exception as e:
            message_placeholder.error(f"Error: {e}")
