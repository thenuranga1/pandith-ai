import streamlit as st
from groq import Groq
import streamlit.components.v1 as components

# --- PAGE CONFIGURATION ---
st.set_page_config(
    page_title="Pandith",
    page_icon="logo.png", 
    layout="wide"
)

# --- SESSION STATE ---
if "chats" not in st.session_state:
    st.session_state.chats = {"Chat 1": []}
if "current_chat_id" not in st.session_state:
    st.session_state.current_chat_id = "Chat 1"
if "chat_counter" not in st.session_state:
    st.session_state.chat_counter = 1

# --- CUSTOM CSS ---
st.markdown("""
<style>
    /* 1. Main Background */
    .stApp {
        background-color: #0E1117;
        color: #FAFAFA;
    }
    
    /* 2. Sidebar Background */
    section[data-testid="stSidebar"] {
        background-color: #262730;
        border-right: 1px solid #333;
    }
    
    /* 3. SIDEBAR CHAT PANELS (ChatGPT Style) */
    div[role="radiogroup"] > label > div:first-child {
        display: none;
    }
    div[role="radiogroup"] > label {
        background-color: transparent !important; /* Transparent initially */
        border: 1px solid transparent !important;
        padding: 10px 15px !important;
        border-radius: 12px !important; /* ROUNDED CORNERS LIKE CHATGPT */
        margin-bottom: 5px !important;
        color: #ddd !important;
        width: 100%;
        display: flex;
        transition: all 0.2s ease;
    }
    /* Hover Effect */
    div[role="radiogroup"] > label:hover {
        background-color: #333 !important;
        color: white !important;
    }
    /* Selected Panel */
    div[role="radiogroup"] > label[data-checked="true"] {
        background-color: #1a1a1a !important; /* Darker highlight */
        border: 1px solid #444 !important;
        color: white !important;
        font-weight: 600;
    }

    /* 4. CHAT INPUT BLENDING */
    div[data-testid="stChatInput"] {
        background-color: transparent !important;
    }
    
    footer {display: none !important;}
    header[data-testid="stHeader"] {background-color: transparent !important;}
    #MainMenu {visibility: hidden;}

</style>
""", unsafe_allow_html=True)

# --- AUTO SCROLL ---
components.html("""
<script>
    const scrollDown = () => {
        window.scrollTo(0, document.body.scrollHeight);
    }
    window.onload = scrollDown;
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
    
    # --- LOGO AREA WITH EXPERIMENTAL TAG ---
    st.markdown("""
        <div style="margin-top: -10px; margin-bottom: 20px;">
            <h1 style="margin: 0; font-size: 2.2rem; font-weight: 700; color: white;">Pandith</h1>
            <span style="
                background-color: #FFC107; 
                color: #000000; 
                padding: 2px 8px; 
                border-radius: 6px; 
                font-size: 0.7rem; 
                font-weight: bold; 
                display: inline-block;
                margin-top: 5px;
                letter-spacing: 0.5px;
            ">EXPERIMENTAL</span>
        </div>
    """, unsafe_allow_html=True)
    
    # New Chat Button
    if st.button("+ New Chat", use_container_width=True):
        st.session_state.chat_counter += 1
        new_chat_name = f"Chat {st.session_state.chat_counter}"
        st.session_state.chats[new_chat_name] = []
        st.session_state.current_chat_id = new_chat_name
        st.rerun()

    st.markdown("---")
    st.caption("Recent Chats")
    
    # Chat List
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
