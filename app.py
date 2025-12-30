import streamlit as st
from groq import Groq
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
    /* Loading Spinner for Images */
    .stImage { display: flex; justify-content: center; }
</style>
""", unsafe_allow_html=True)

# --- API SETUP ---
try:
    if "GROQ_API_KEY" in st.secrets:
        client = Groq(api_key=st.secrets["GROQ_API_KEY"])
    else:
        st.error("⚠️ API Key එක දාලා නෑ! Settings වලට GROQ_API_KEY එක දාන්න.")
        st.stop()
except Exception as e:
    st.error(f"⚠️ Connection Error: {e}")

# --- SIDEBAR ---
with st.sidebar:
    st.title("Pandith AI 🧠")
    st.caption("Developed by a Sri Lankan Developer 🇱🇰")
    st.markdown("---")
    st.markdown("✅ **Text Generation** (Llama 3.3)\n\n✅ **Image Generation** (Experimental)")
    
    if st.button("Clear Chat / New Chat 🗑️"):
        st.session_state.messages = []
        st.rerun()
    
    st.markdown("---")
    st.markdown("Powered by **Groq & Pollinations**")

# --- CHAT LOGIC ---

# SYSTEM INSTRUCTION (The Brain's Rules)
system_prompt = """You are Pandith AI (පණ්ඩිත් AI), a helpful AI assistant developed in Sri Lanka.
You answer primarily in Sinhala. If the question is in English, answer in English.

CRITICAL INSTRUCTION FOR IMAGES:
If the user asks to generate an image, draw something, or create a picture, do NOT say you cannot.
Instead, generate a detailed descriptive prompt in English for that image.
Your entire response must start EXCLUSIVELY with the flag "###GENERATE_IMAGE###" followed by the English prompt on a new line.Do not add any other text before or after.

Example User: "බල්ලෙක් අඳින්න"
Example Assistant Output:
###GENERATE_IMAGE###
A cute golden retriever puppy sitting in a grassy field at sunset, cinematic lighting, 4k.

Example User: "මට කොළඹ නගරයේ පින්තූරයක් ඕන"
Example Assistant Output:
###GENERATE_IMAGE###
A futuristic view of Colombo city skyline with lotus tower at night, cyberpunk style, neon lights, busy streets."""

if "messages" not in st.session_state:
    st.session_state.messages = []
    st.session_state.messages.append({
        "role": "assistant", 
        "content": "ආයුබෝවන්! මම Pandith AI. මට දැන් ඔබ වෙනුවෙන් පින්තූර නිර්මාණය කිරීමටද හැකියි. (උදාහරණයක් ලෙස: 'ලස්සන ගමක පින්තූරයක් අඳින්න' යැයි පවසන්න)."
    })

for message in st.session_state.messages:
    role = "user" if message["role"] == "user" else "assistant"
    avatar = "👤" if role == "user" else "🧠"
    # Only show text messages in history to keep it clean
    if "Is an Image" not in message:
        with st.chat_message(role, avatar=avatar):
            st.markdown(message["content"])

if prompt := st.chat_input("ඔබේ ප්‍රශ්නය (හෝ පින්තූරය) මෙතන ඉල්ලන්න..."):
    st.chat_message("user", avatar="👤").markdown(prompt)
    st.session_state.messages.append({"role": "user", "content": prompt})

    with st.chat_message("assistant", avatar="🧠"):
        message_placeholder = st.empty()
        message_placeholder.markdown("සිතමින් පවතී... ⚡")
        
        try:
            # Ask Groq to generate response or image prompt
            completion = client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[
                    {"role": "system", "content": system_prompt},
                    *st.session_state.messages
                ],
                temperature=0.7,
                max_tokens=1024,
                top_p=1,
                stream=True,
                stop=None,
            )
            
            full_response = ""
            for chunk in completion:
                if chunk.choices[0].delta.content:
                    full_response += chunk.choices[0].delta.content
                    # Only show streaming if it's not an image prompt tag yet
                    if "###GENERATE_IMAGE###" not in full_response:
                         message_placeholder.markdown(full_response + "▌")
            
            # Check if AI wants to generate an image
            if "###GENERATE_IMAGE###" in full_response:
                message_placeholder.markdown("පින්තූරය නිර්මාණය කරමින්... 🎨")
                # Extract the prompt
                image_prompt = full_response.replace("###GENERATE_IMAGE###", "").strip()
                # Encode prompt for URL
                encoded_prompt = urllib.parse.quote(image_prompt)
                # Use Pollinations.ai free API
                image_url = f"https://image.pollinations.ai/prompt/{encoded_prompt}?nologo=true"
                
                # Display Image
                message_placeholder.empty()
                st.markdown(f"_Based on prompt: {image_prompt}_")
                st.image(image_url, caption="Generated by Pandith AI", use_column_width=True)
                # Save to history differently so we don't feed image URLs back to Groq
                st.session_state.messages.append({"role": "assistant", "content": f"(Image generated based on: {prompt})", "Is an Image": True})

            else:
                # Normal text response
                message_placeholder.markdown(full_response)
                st.session_state.messages.append({"role": "assistant", "content": full_response})
            
        except Exception as e:
            message_placeholder.error(f"⚠️ Error: {e}")
