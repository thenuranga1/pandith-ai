import streamlit as st
from groq import Groq
import requests
import io
from PIL import Image

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
# Check for Groq Key
try:
    if "GROQ_API_KEY" in st.secrets:
        client = Groq(api_key=st.secrets["GROQ_API_KEY"])
    else:
        st.error("⚠️ GROQ API Key එක දාලා නෑ!")
        st.stop()
except:
    st.error("⚠️ Secrets හරියට සෙට් වෙලා නෑ.")
    st.stop()

# Hugging Face Configuration (Free Reliable Image API)
API_URL = "https://api-inference.huggingface.co/models/stabilityai/stable-diffusion-xl-base-1.0"
headers = {"Authorization": f"Bearer {st.secrets['HF_TOKEN']}"} if "HF_TOKEN" in st.secrets else None

def query_huggingface(prompt):
    if not headers:
        return None
    try:
        response = requests.post(API_URL, headers=headers, json={"inputs": prompt})
        return response.content
    except:
        return None

# --- SIDEBAR ---
with st.sidebar:
    st.title("Pandith AI 🧠")
    st.caption("Developed by a Sri Lankan Developer 🇱🇰")
    st.markdown("---")
    st.markdown("✅ **Text:** Llama 3.3 (Groq)\n\n✅ **Images:** Stable Diffusion XL")
    
    if st.button("Clear Chat / New Chat 🗑️"):
        st.session_state.messages = []
        st.rerun()

# --- CHAT LOGIC ---

# System Prompt
system_prompt = """You are Pandith AI (පණ්ඩිත් AI), a helpful AI assistant.
Answer primarily in Sinhala.
CRITICAL: If the user asks for an image, start your response with "###GENERATE_IMAGE###" followed by the English prompt."""

if "messages" not in st.session_state:
    st.session_state.messages = []
    st.session_state.messages.append({"role": "assistant", "content": "ආයුබෝවන්! මම Pandith AI. ඔබට ඕනෑම පින්තූරයක් දැන් උසස් තත්වයෙන් (HD) නිර්මාණය කරගන්න පුළුවන්."})

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
            # 1. Get Text/Prompt from Groq
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
                message_placeholder.markdown("පින්තූරය නිර්මාණය කරමින් (High Quality)... 🎨")
                image_prompt = full_response.replace("###GENERATE_IMAGE###", "").strip()
                
                if not headers:
                    message_placeholder.error("⚠️ Hugging Face Token එක දාලා නෑ Secrets වලට!")
                else:
                    # Call Hugging Face API
                    image_bytes = query_huggingface(image_prompt)
                    
                    if image_bytes:
                        try:
                            image = Image.open(io.BytesIO(image_bytes))
                            message_placeholder.empty()
                            st.image(image, caption=f"Generated: {image_prompt}", use_column_width=True)
                            
                            # Save image to history (special format)
                            st.session_state.messages.append({
                                "role": "assistant", 
                                "content": image, 
                                "caption": image_prompt,
                                "type": "image"
                            })
                        except:
                            message_placeholder.error("Error loading image. Try again.")
                    else:
                        message_placeholder.error("Image generation failed. Server busy.")
            else:
                message_placeholder.markdown(full_response)
                st.session_state.messages.append({"role": "assistant", "content": full_response})

        except Exception as e:
            message_placeholder.error(f"Error: {e}")
