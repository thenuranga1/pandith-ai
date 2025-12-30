import streamlit as st
from groq import Groq
import requests
import io
from PIL import Image
import time

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

# Hugging Face Configuration (The Classic Reliable Model)
# මේ මොඩල් එක (v1.5) කවදාවත් වරදින්නෙ නෑ. 100% Free & Open.
API_URL = "https://api-inference.huggingface.co/models/runwayml/stable-diffusion-v1-5"

headers = {"Authorization": f"Bearer {st.secrets['HF_TOKEN']}"} if "HF_TOKEN" in st.secrets else None

def query_huggingface(prompt):
    if not headers:
        return None, "Error: HF_TOKEN not found in secrets."
    
    payload = {"inputs": prompt}
    try:
        # අපි Timeout එකක් දාමු තත්පර 30ක
        response = requests.post(API_URL, headers=headers, json=payload, timeout=30)
        
        # 1. Success
        if response.status_code == 200:
            return response.content, None
            
        # 2. Loading
        elif "estimated_time" in response.text:
            return None, "⚠️ Model එක Load වෙමින් පවතී. කරුණාකර තත්පර 20කින් නැවත උත්සාහ කරන්න."
        
        # 3. Other Errors
        else:
            return None, f"API Error: {response.status_code} - {response.reason}"
            
    except Exception as e:
        return None, f"Connection Error: {str(e)}"

# --- SIDEBAR ---
with st.sidebar:
    st.title("Pandith AI 🧠")
    st.caption("Developed by a Sri Lankan Developer 🇱🇰")
    st.markdown("---")
    st.markdown("✅ **Text:** Llama 3.3 (Groq)\n\n✅ **Images:** Stable Diffusion v1.5")
    
    if st.button("Clear Chat / New Chat 🗑️"):
        st.session_state.messages = []
        st.rerun()

# --- CHAT LOGIC ---
system_prompt = """You are Pandith AI (පණ්ඩිත් AI). Answer primarily in Sinhala.
CRITICAL: If the user asks for an image/picture/drawing, start your response with "###GENERATE_IMAGE###" followed by a detailed English prompt."""

if "messages" not in st.session_state:
    st.session_state.messages = []
    st.session_state.messages.append({"role": "assistant", "content": "ආයුබෝවන්! මම Pandith AI. ඔබට අවශ්‍ය පින්තූරයක් කියන්න."})

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
                
                # Hugging Face Call
                image_bytes, error_msg = query_huggingface(image_prompt)
                
                if image_bytes:
                    try:
                        image = Image.open(io.BytesIO(image_bytes))
                        message_placeholder.empty()
                        st.image(image, caption=f"Generated: {image_prompt}", use_column_width=True)
                        
                        st.session_state.messages.append({
                            "role": "assistant", 
                            "content": image, 
                            "caption": image_prompt,
                            "type": "image"
                        })
                    except:
                        message_placeholder.error("Error: රූපය පෙන්වීමට නොහැක.")
                else:
                    message_placeholder.error(error_msg)
            else:
                message_placeholder.markdown(full_response)
                st.session_state.messages.append({"role": "assistant", "content": full_response})

        except Exception as e:
            message_placeholder.error(f"System Error: {e}")
