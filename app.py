import streamlit as st
from groq import Groq
import requests
import io
from PIL import Image
import urllib.parse

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
        st.error("⚠️ GROQ API Key එක දාලා නෑ!")
        st.stop()
except:
    st.error("⚠️ Secrets හරියට සෙට් වෙලා නෑ.")
    st.stop()

# --- IMAGE GENERATION FUNCTIONS ---

# 1. Hugging Face (Primary Option)
HF_API_URL = "https://api-inference.huggingface.co/models/stabilityai/stable-diffusion-2-1"
hf_headers = {"Authorization": f"Bearer {st.secrets['HF_TOKEN']}"} if "HF_TOKEN" in st.secrets else None

def generate_image_hf(prompt):
    if not hf_headers:
        return None
    try:
        response = requests.post(HF_API_URL, headers=hf_headers, json={"inputs": prompt}, timeout=15)
        if response.status_code == 200:
            return Image.open(io.BytesIO(response.content))
        else:
            return None # HF Failed
    except:
        return None # Connection Failed

# 2. Pollinations AI (Backup Option)
def generate_image_pollinations(prompt):
    try:
        encoded_prompt = urllib.parse.quote(prompt)
        url = f"https://image.pollinations.ai/prompt/{encoded_prompt}?nologo=true"
        response = requests.get(url, timeout=15)
        if response.status_code == 200:
            return Image.open(io.BytesIO(response.content))
        return None
    except:
        return None

# --- SIDEBAR ---
with st.sidebar:
    st.title("Pandith AI 🧠")
    st.caption("Sri Lankan AI 🇱🇰")
    st.markdown("---")
    st.markdown("✅ **Text:** Llama 3.3 (Groq)")
    st.markdown("✅ **Images:** Hybrid Engine (HF + Backup)")
    
    if st.button("Clear Chat / New Chat 🗑️"):
        st.session_state.messages = []
        st.rerun()

# --- CHAT LOGIC ---
system_prompt = """You are Pandith AI (පණ්ඩිත් AI). Answer primarily in Sinhala.
CRITICAL: If the user asks for an image/picture/drawing, start your response with "###GENERATE_IMAGE###" followed by a detailed English prompt."""

if "messages" not in st.session_state:
    st.session_state.messages = []
    st.session_state.messages.append({"role": "assistant", "content": "ආයුබෝවන්! මම Pandith AI. ඔබට අවශ්‍ය පින්තූරයක් කියන්න. මම ක්‍රම දෙකකින් උත්සාහ කර පින්තූරය ලබා දෙන්නම්."})

# Display History
for message in st.session_state.messages:
    role = "user" if message["role"] == "user" else "assistant"
    avatar = "👤" if role == "user" else "🧠"
    
    if message.get("type") == "image":
        with st.chat_message("assistant", avatar="🧠"):
            st.image(message["content"], caption=message["caption"])
    else:
        with st.chat_message(role, avatar=avatar):
            st.markdown(message["content"])

# Input
if prompt := st.chat_input("ප්‍රශ්නය හෝ පින්තූරය මෙතන..."):
    st.chat_message("user", avatar="👤").markdown(prompt)
    st.session_state.messages.append({"role": "user", "content": prompt})

    with st.chat_message("assistant", avatar="🧠"):
        message_placeholder = st.empty()
        message_placeholder.markdown("සිතමින් පවතී... ⚡")
        
        try:
            # 1. Get Text from Groq
            clean_history = [{"role": m["role"], "content": m["content"]} for m in st.session_state.messages if m.get("type") != "image"]
            
            completion = client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[{"role": "system", "content": system_prompt}, *clean_history],
                temperature=0.7,
                max_tokens=1024,
                stream=True
            )
            
            full_response = ""
            for chunk in completion:
                if chunk.choices[0].delta.content:
                    full_response += chunk.choices[0].delta.content
                    if "###GENERATE_IMAGE###" not in full_response:
                        message_placeholder.markdown(full_response + "▌")

            # 2. Check for Image Request
            if "###GENERATE_IMAGE###" in full_response:
                message_placeholder.markdown("පින්තූරය නිර්මාණය කරමින්... 🎨")
                image_prompt = full_response.replace("###GENERATE_IMAGE###", "").strip()
                
                # --- HYBRID GENERATION LOGIC ---
                final_image = None
                source = ""

                # Attempt 1: Hugging Face (High Quality)
                final_image = generate_image_hf(image_prompt)
                source = "Hugging Face"
                
                # Attempt 2: Pollinations (Backup if HF fails)
                if final_image is None:
                    # message_placeholder.markdown("Server Busy. Backup Server භාවිතා කරමින්... 🔄")
                    final_image = generate_image_pollinations(image_prompt)
                    source = "Backup Server"

                # Display Result
                if final_image:
                    message_placeholder.empty()
                    st.image(final_image, caption=f"Generated: {image_prompt} ({source})", use_column_width=True)
                    
                    st.session_state.messages.append({
                        "role": "assistant", 
                        "content": final_image, 
                        "caption": f"{image_prompt} ({source})",
                        "type": "image"
                    })
                else:
                    message_placeholder.error("Error: පින්තූරය සෑදීමට නොහැකි විය. කරුණාකර නැවත උත්සාහ කරන්න.")

            else:
                message_placeholder.markdown(full_response)
                st.session_state.messages.append({"role": "assistant", "content": full_response})

        except Exception as e:
            message_placeholder.error(f"System Error: {e}")
