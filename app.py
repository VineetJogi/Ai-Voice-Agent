import streamlit as st
import os
import asyncio
import tools
import agent
import audio

# --- PAGE CONFIGURATION & STYLING ---
st.set_page_config(
    page_title="Nova | AI Support Agent",
    page_icon="🎙️",
    layout="wide", # Changed to wide for a dashboard feel
    initial_sidebar_state="expanded"
)

# Custom CSS for Production-Grade Look
st.markdown("""
    <style>
    /* Main Background & Fonts */
    .stApp {
        background-color: #0e1117;
        font-family: 'Inter', sans-serif;
    }
    
    /* Header Styling */
    .main-header {
        text-align: center;
        padding: 2rem 0;
        background: linear-gradient(90deg, #1e2130 0%, #0e1117 100%);
        border-radius: 15px;
        margin-bottom: 2rem;
        box-shadow: 0 4px 15px rgba(0,0,0,0.3);
    }
    .main-header h1 {
        color: #fff;
        font-weight: 700;
        font-size: 2.5rem;
        margin: 0;
    }
    .main-header p {
        color: #a0a0a0;
        font-size: 1.1rem;
    }
    
    /* Status Badges */
    .status-badge {
        display: inline-block;
        padding: 5px 15px;
        border-radius: 20px;
        font-size: 0.85rem;
        font-weight: 600;
        margin-right: 10px;
    }
    .status-ok { background-color: #1f3a28; color: #4ade80; border: 1px solid #1f3a28; }
    .status-err { background-color: #3a1f1f; color: #f87171; border: 1px solid #3a1f1f; }
    
    /* Chat Bubble Styling Override */
    .stChatMessage {
        background-color: #1c1f2e;
        border-radius: 15px;
        border: 1px solid #2d303e;
    }
    
    /* Button Styling */
    div.stButton > button:first-child {
        width: 100%;
        border-radius: 8px;
        height: 3rem;
        font-weight: 600;
        transition: all 0.3s ease;
    }
    /* Primary Action Button (Mic) */
    div.stButton > button[kind="primary"] {
        background: linear-gradient(135deg, #6366f1 0%, #4f46e5 100%);
        border: none;
        box-shadow: 0 4px 14px rgba(99, 102, 241, 0.4);
    }
    div.stButton > button[kind="primary"]:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 20px rgba(99, 102, 241, 0.6);
    }
    
    /* Spinner Customization */
    .stSpinner > div {
        border-top-color: #6366f1 !important;
    }
    </style>
""", unsafe_allow_html=True)

# --- SYSTEM CHECKS ---
if not os.path.exists("database.db"):
    st.error("🚨 CRITICAL: 'database.db' not found! Run 'setup_db.py' first.")
    st.stop()

# --- AI INITIALIZATION ---
if "ai_agent" not in st.session_state:
    try:
        with st.spinner("🧠 Booting Neural Interface..."):
            st.session_state.ai_agent = agent.VoiceAgent()
        # No success message needed, the UI will show it
    except Exception as e:
        st.error(f"Failed to start AI: {e}")

if "messages" not in st.session_state:
    st.session_state.messages = []

# --- SIDEBAR: COMMAND CENTER ---
with st.sidebar:
    st.image("https://cdn-icons-png.flaticon.com/512/4712/4712035.png", width=80) # Placeholder generic AI icon
    st.markdown("### Control Panel")
    
    # Visual Status Indicators
    st.markdown("""
        <div style='margin-bottom: 20px;'>
            <div class='status-badge status-ok'>● System Online</div>
            <div class='status-badge status-ok'>● DB Connected</div>
        </div>
    """, unsafe_allow_html=True)
    
    st.divider()
    
    st.markdown("#### ⌨️ Manual Override")
    manual_input = st.text_input("Text Input:", placeholder="Type command here...", label_visibility="collapsed")
    
    if manual_input and st.button("Send Text", use_container_width=True):
        st.session_state.messages.append({"role": "user", "content": manual_input})
        response = st.session_state.ai_agent.get_response(manual_input)
        st.session_state.messages.append({"role": "assistant", "content": response})
        asyncio.run(audio.speak(response))
        st.rerun()
        
    st.divider()
    if st.button("🗑️ Clear Context", type="secondary", use_container_width=True):
        st.session_state.messages = []
        st.rerun()
        
    st.markdown("<div style='position: fixed; bottom: 20px; font-size: 12px; color: #555;'>Autonomix v1.0.0</div>", unsafe_allow_html=True)

# --- MAIN LAYOUT ---

# 1. Custom Header
st.markdown("""
    <div class='main-header'>
        <h1>🎙️ NOVA</h1>
        <p>Autonomous Customer Support Interface</p>
    </div>
""", unsafe_allow_html=True)

# 2. Chat Area Container
chat_container = st.container()

# 3. Action Area (Fixed at bottom conceptually, or clearly separated)
st.divider()
col_mic, col_status = st.columns([1, 4])

with col_mic:
    # Main Voice Interaction Button
    start_listening = st.button("🔴 Activate Voice", type="primary", use_container_width=True)

with col_status:
    # Dynamic Status Text
    status_placeholder = st.empty()

# --- MAIN LOGIC EXECUTION ---

# Render Chat History
with chat_container:
    if not st.session_state.messages:
        st.info("👋 Hello! I'm Nova. Click 'Activate Voice' to speak or use the sidebar to type.")
    
    for message in st.session_state.messages:
        avatar = "👤" if message["role"] == "user" else "🤖"
        with st.chat_message(message["role"], avatar=avatar):
            st.markdown(message["content"])

# Handle Voice Logic
if start_listening:
    # Step 1: Record Audio
    status_placeholder.info("👂 Listening for input...")
    wav_path = None
    try:
        wav_path = audio.listen()
    except Exception as e:
        st.error(f"Microphone Error: {e}")
        wav_path = None

    # Step 2: Transcribe Audio
    user_text = None
    if wav_path:
        status_placeholder.info("📝 Transcribing audio...")
        user_text = audio.transcribe(wav_path)
        if os.path.exists(wav_path):
            os.remove(wav_path)

    # Step 3: Process Text
    if user_text:
        # Append User Message immediately
        st.session_state.messages.append({"role": "user", "content": user_text})
        
        # Display immediately
        with chat_container:
             with st.chat_message("user", avatar="👤"):
                st.markdown(user_text)

        status_placeholder.info("🧠 Nova is thinking...")
        
        try:
            response_text = st.session_state.ai_agent.get_response(user_text)
        except Exception as e:
            response_text = "I encountered a system error."
            st.error(f"AI Error: {e}")
        
        # Append Assistant Message
        st.session_state.messages.append({"role": "assistant", "content": response_text})
        
        # Display response
        with chat_container:
            with st.chat_message("assistant", avatar="🤖"):
                st.markdown(response_text)
            
        # Step 4: Speak Response
        status_placeholder.success("✅ Complete")
        try:
            asyncio.run(audio.speak(response_text))
        except Exception as e:
            st.warning(f"Audio Output Failed: {e}")
            
    elif wav_path:
        status_placeholder.warning("⚠️ No voice detected. Please try again.")
    else:
        status_placeholder.empty()
