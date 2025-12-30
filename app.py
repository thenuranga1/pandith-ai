import streamlit as st
from groq import Groq
import streamlit.components.v1 as components

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

# --- CUSTOM CSS (THEME & UI FIXES) ---
st.markdown("""
<style>
    /* 1. Main Dark Theme */
    .stApp {
        background-color: #000000;
        color: #e0e0e0;
    }
    
    /* 2. Sidebar Styling */
    section[data-testid="stSidebar"] {
        background-color: #050505;
        border-right: 1px solid #222;
    }
    
    /* 3. SIDEBAR CHAT PANELS (Radio Button Hack) */
    /* Hide the default radio circles */
    div[role="radiogroup"] > label > div:first-child {
        display: none;
    }
    /* Style the labels as Panels/Cards */
    div[role="radiogroup"] > label {
        background-color: #111;
        border: 1px solid #333;
        padding: 12px 15px;
        border-radius: 8px;
        margin-bottom: 8px;
        cursor: pointer;
        transition: all 0.2s ease;
        color: #aaa;
        display: flex;
        width: 100%;
    }
    /* Hover Effect */
    div[role="radiogroup"] > label:hover {
        background-color: #1a1a1a;
        border-color: #555;
        color: white;
    }
    /* Selected Panel Effect */
    div[role="radiogroup"] > label[data-checked="true"] {
        background-color: #222;
        border-color: #fff;
        color: white;
        font-weight: bold;
        box-shadow: 0 0 10px rgba(255,255,255,0.05);
    }

    /* 4. CHAT INPUT BAR STYLING (Dark Theme Fix) */
    /* The container */
    .stChatInput {
        background-color: transparent !important;
    }
    /* The actual input box */
    .stChatInput textarea {
        background-color: #111 !important;
        color: white !important;
        border: 1px solid #333 !important;
        border-radius: 10px !important;
    }
    /* Focus state */
    .stChatInput textarea:focus {
        border-color: #666 !important;
        box-shadow: none !important;
    }
    
    /* 5. Header & Footer Visibility */
    header[data-testid="stHeader"] {
        background-color: transparent;
        z-index: 999;
    }
    footer {visibility: hidden;}
    #MainMenu {visibility: hidden;}

</style>
""", unsafe_allow_html=True)

# --- JAVASCRIPT FOR AUTO-SCROLL (Jump to Bottom) ---
# This script runs on every reload to ensure we are at the bottom
components.html("""
<script>
    window.onload = function() {
        window.scrollTo(0, document.body.scrollHeight);
    }
    // Also try to scroll after a small delay to catch dynamic content
    setTimeout(function() {
        window.scrollTo(0, document.body.scrollHeight);
    }, 500);
</script>
""", height=0, width=0)

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
        st.image("logo.png", width=70)
    except:
        pass 
        
    st.markdown("### Pandith")
    st.markdown("<div style='height: 10px;'></div>", unsafe_allow_html=True) # Spacer
    
    # Updated Button Text: + New Chat
    if st.button("+ New Chat", use_container_width=True, type="primary"):
        st.session_state.chat_counter += 1
        new_chat_name = f"Chat {st.session_state.chat_counter}"
        st.session_state.chats[new_chat_name] = []
        st.session_state.current_chat_id = new_chat_name
        st.rerun()

    st.markdown("---")
    st.caption("Your Chats")
    
    # Custom Styled Radio Button List
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

# Initial Greeting
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
