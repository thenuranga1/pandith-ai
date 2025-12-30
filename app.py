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

# --- CUSTOM CSS (PITCH BLACK THEME FIXES) ---
st.markdown("""
<style>
    /* 1. Main Dark Theme (Background) */
    .stApp {
        background-color: #000000;
        color: #e0e0e0;
    }
    
    /* 2. Sidebar Styling */
    section[data-testid="stSidebar"] {
        background-color: #050505; /* Almost black sidebar */
        border-right: 1px solid #1a1a1a;
    }
    
    /* 3. SIDEBAR PANELS (Advanced Radio Button Styling) */
    div[role="radiogroup"] > label > div:first-child {
        display: none; /* Hide default radio circles */
    }
    div[role="radiogroup"] > label {
        background-color: #0f0f0f !important;
        border: 1px solid #222 !important;
        padding: 12px 15px !important;
        border-radius: 8px !important;
        margin-bottom: 8px !important;
        color: #888 !important;
        width: 100%;
        display: flex;
        justify-content: flex-start;
        transition: all 0.2s;
    }
    /* Hover Effect */
    div[role="radiogroup"] > label:hover {
        background-color: #1a1a1a !important;
        color: white !important;
        border-color: #444 !important;
    }
    /* Selected Panel (Active Chat) */
    div[role="radiogroup"] > label[data-checked="true"] {
        background-color: #1a1a1a !important;
        border-color: #ffffff !important;
        color: white !important;
        font-weight: bold;
    }

    /* 4. CHAT INPUT BAR STYLING (THE REAL FIX) */
    
    /* Make the bottom container transparent so it doesn't look grey */
    footer {display: none !important;}
    .stApp > header {background-color: transparent !important;}
    
    /* Target the input box wrapper specifically */
    div[data-testid="stChatInput"] {
        background-color: transparent !important;
    }
    
    /* This is the actual box where you type - FORCE BLACK */
    div[data-testid="stChatInput"] > div {
        background-color: #000000 !important; /* Pitch Black */
        border: 1px solid #333 !important; /* Dark Border */
        color: white !important;
        border-radius: 15px !important;
    }
    
    /* Typing Text Color */
    textarea[data-testid="stChatInputTextArea"] {
        color: white !important;
        caret-color: white !important; /* Blinking cursor color */
    }
    
    /* Remove Blue Glow on Focus */
    div[data-testid="stChatInput"] > div:focus-within {
        border-color: #666 !important;
        box-shadow: none !important;
    }
    
    /* Send Button Icon Color */
    button[data-testid="stChatInputSubmitButton"] {
        color: #666 !important;
    }
    button[data-testid="stChatInputSubmitButton"]:hover {
        color: white !important;
    }
    
    /* 5. Header Visibility (Keep Sidebar Toggle) */
    header[data-testid="stHeader"] {
        background-color: transparent;
        z-index: 999;
    }
    #MainMenu {visibility: hidden;}

</style>
""", unsafe_allow_html=True)

# --- AUTO-SCROLL SCRIPT ---
components.html("""
<script>
    const scrollDown = () => {
        window.scrollTo(0, document.body.scrollHeight);
    }
    window.onload = scrollDown;
    setInterval(scrollDown, 1000); // Check every second to keep it scrolled
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
    
    # 1. FIXED BUTTON: "+ New Chat" (No Emoji, Primary Red Style Removed if you want black)
    # If you want it black/grey to match theme, remove type="primary". 
    # I kept it standard to blend in.
    if st.button("+ New Chat", use_container_width=True):
        st.session_state.chat_counter += 1
        new_chat_name = f"Chat {st.session_state.chat_counter}"
        st.session_state.chats[new_chat_name] = []
        st.session_state.current_chat_id = new_chat_name
        st.rerun()

    st.markdown("---")
    st.caption("Recent Chats")
    
    # 2. FIXED PANELS: The CSS above handles the look
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

# --- SYSTEM PROMPT ---
system_prompt = """You are Pandith. 
You are a wise, calm, and disciplined Sage (Rishi).
Your tone is always serene, polite, and fatherly.

CRITICAL INSTRUCTIONS:
1. Address user as "දරුවා" (Child).
2. Name: "Pandith". Use "පණ්ඩිත්" only if asked in Sinhala.
3. Creator: "Thenuranga Dhananjaya".
4. If asked for an image, provide a prompt starting with ###PROMPT_ONLY###.
"""

# --- LOAD HISTORY ---
current_messages = st.session_state.chats[st.session_state.current_chat_id]
if not current_messages:
    current_messages.append({"role": "assistant", "content": "ආයුබෝවන්!"})

# --- DISPLAY CHAT ---
for message in st.session_state.chats[st.session_state.current_chat_id]:
    role = "user" if message["role"] == "user" else "assistant"
    avatar = "👤" if role == "user" else "logo.png"
    
    with st.chat_message(role, avatar=avatar):
        st.markdown(message["content"])

# --- CHAT INPUT ---
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
