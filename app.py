import streamlit as st
from groq import Groq

# --- PAGE CONFIGURATION (Favicon Setup) ---
# මෙතන page_icon එකට අපි logo.png දුන්නම Browser Tab එකේ Logo එක වැටෙනවා.
st.set_page_config(
    page_title="Pandith AI",
    page_icon="logo.png", 
    layout="wide"
)

# --- THEME SWITCHER LOGIC ---
# Sidebar එකේ උඩින්ම Switch එක දාමු
with st.sidebar:
    st.image("logo.png", width=80) # Sidebar එකෙත් Logo එක පෙන්නමු
    st.markdown("### Settings")
    theme_mode = st.toggle("⚫ Dark Mode", value=True)

# --- GROK STYLE CSS (DYNAMIC) ---
# Switch එක On/Off වෙන විදිහට පාට මාරු වෙන කෝඩ් එක
if theme_mode:
    # DARK MODE (Grok Style)
    bg_color = "#000000"
    text_color = "#ffffff"
    input_bg = "#121212"
    sidebar_bg = "#0a0a0a"
    border_color = "#333333"
else:
    # LIGHT MODE
    bg_color = "#ffffff"
    text_color = "#000000"
    input_bg = "#f7f7f7"
    sidebar_bg = "#f0f0f0"
    border_color = "#e0e0e0"

st.markdown(f"""
<style>
    /* Main Background */
    .stApp {{
        background-color: {bg_color};
        color: {text_color};
    }}
    
    /* Sidebar Background */
    section[data-testid="stSidebar"] {{
        background-color: {sidebar_bg};
        border-right: 1px solid {border_color};
    }}
    
    /* Text Input Styling (Minimalist) */
    .stTextInput > div > div > input {{
        background-color: {input_bg};
        color: {text_color};
        border: 1px solid {border_color};
        border-radius: 8px; /* Slight curve like Grok */
        padding: 10px 15px;
    }}
    
    /* Focus Color */
    .stTextInput > div > div > input:focus {{
        border-color: {text_color};
        box-shadow: none;
    }}

    /* Headers & Text */
    h1, h2, h3, p, div, span {{
        color: {text_color} !important;
        font-family: 'Segoe UI', sans-serif; /* Clean font */
    }}

    /* Chat Messages Background */
    .stChatMessage {{
        background-color: transparent;
    }}

    /* Remove Streamlit Extras */
    #MainMenu {{visibility: hidden;}}
    footer {{visibility: hidden;}}
    header {{visibility: hidden;}}
    
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

# --- SIDEBAR CONTENT ---
with st.sidebar:
    st.markdown("---")
    st.markdown(f"**Pandith AI** v2.0")
    if st.button("New Chat +", use_container_width=True):
        st.session_state.messages = []
        st.rerun()

# --- CHAT LOGIC ---
system_prompt = """You are Pandith AI. You are helpful, direct, and minimalist. 
Answer primarily in Sinhala.
If asked for an image, provide a prompt starting with ###PROMPT_ONLY###."""

if "messages" not in st.session_state:
    st.session_state.messages = []
    # Initial Greeting
    st.session_state.messages.append({"role": "assistant", "content": "ආයුබෝවන්."})

# Display History
for message in st.session_state.messages:
    role = "user" if message["role"] == "user" else "assistant"
    
    # AVATAR LOGIC:
    # User -> 👤 (Default Icon)
    # Assistant -> logo.png (Your Custom Logo)
    avatar = "👤" if role == "user" else "logo.png"
    
    with st.chat_message(role, avatar=avatar):
        st.markdown(message["content"])

# Input Area
if prompt := st.chat_input("Ask Pandith..."):
    # User Message
    st.chat_message("user", avatar="👤").markdown(prompt)
    st.session_state.messages.append({"role": "user", "content": prompt})

    # AI Response
    with st.chat_message("assistant", avatar="logo.png"):
        message_placeholder = st.empty()
        
        try:
            completion = client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[{"role": "system", "content": system_prompt}, *st.session_state.messages],
                temperature=0.7,
                stream=True
            )
            
            full_response = ""
            for chunk in completion:
                if chunk.choices[0].delta.content:
                    full_response += chunk.choices[0].delta.content
                    if "###PROMPT_ONLY###" not in full_response:
                        message_placeholder.markdown(full_response + "▌")
            
            # Formatting Response
            if "###PROMPT_ONLY###" in full_response:
                prompt_text = full_response.replace("###PROMPT_ONLY###", "").strip()
                final_output = f"**Prompt:**\n```text\n{prompt_text}\n```"
                message_placeholder.markdown(final_output)
                st.session_state.messages.append({"role": "assistant", "content": final_output})
            else:
                message_placeholder.markdown(full_response)
                st.session_state.messages.append({"role": "assistant", "content": full_response})

        except Exception as e:
            message_placeholder.error(f"Error: {e}")
