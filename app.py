import streamlit as st
import os
import asyncio
import tools
import agent
import audio  # Person C's code

# --- PAGE CONFIGURATION ---
st.set_page_config(page_title="Autonomix Voice Agent", layout="centered")
st.title("🎙️ Nova: AI Customer Support")

# --- 1. DB CHECK ---
if not os.path.exists("database.db"):
    st.error("🚨 CRITICAL: 'database.db' not found! Run 'setup_db.py' first.")
    st.stop()

# --- 2. AI INIT ---
if "ai_agent" not in st.session_state:
    try:
        with st.spinner("Initializing AI Brain..."):
            st.session_state.ai_agent = agent.VoiceAgent()
        st.success("System Online")
    except Exception as e:
        st.error(f"Failed to start AI: {e}")

# --- 3. CHAT HISTORY ---
if "messages" not in st.session_state:
    st.session_state.messages = []

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# --- 4. MAIN LOOP ---
col1, col2 = st.columns(2)

with col1:
    if st.button("🎤 Start Listening", type="primary"):
        # STEP A: RECORD AUDIO
        with st.spinner("Listening..."):
            try:
                # audio.listen() returns a FILE PATH now
                wav_path = audio.listen()
            except Exception as e:
                st.error(f"Mic Error: {e}")
                wav_path = None

        # STEP B: TRANSCRIBE AUDIO
        user_text = None
        if wav_path:
            with st.spinner("Transcribing..."):
                user_text = audio.transcribe(wav_path)
                # Cleanup temp file
                if os.path.exists(wav_path):
                    os.remove(wav_path)

        # STEP C: PROCESS TEXT
        if user_text:
            st.session_state.messages.append({"role": "user", "content": user_text})
            with st.chat_message("user"):
                st.markdown(user_text)

            with st.spinner("Thinking..."):
                try:
                    response_text = st.session_state.ai_agent.get_response(user_text)
                except Exception as e:
                    response_text = "I encountered an error."
                    st.error(f"AI Error: {e}")
            
            st.session_state.messages.append({"role": "assistant", "content": response_text})
            with st.chat_message("assistant"):
                st.markdown(response_text)
                
            # STEP D: SPEAK RESPONSE
            with st.spinner("Speaking..."):
                try:
                    asyncio.run(audio.speak(response_text))
                except Exception as e:
                    st.warning(f"Audio Output Failed: {e}")
        elif wav_path:
            st.warning("I didn't hear anything clearly.")

with col2:
    if st.button("🔄 Reset"):
        st.session_state.messages = []
        st.rerun()

# --- SIDEBAR DEBUG ---
with st.sidebar:
    st.write("Database: ✅ Connected")
    st.write("Model: ✅ Gemini Flash")
    
    manual_input = st.text_input("Manual Text Input:")
    if manual_input and st.button("Send Text"):
        st.session_state.messages.append({"role": "user", "content": manual_input})
        response = st.session_state.ai_agent.get_response(manual_input)
        st.session_state.messages.append({"role": "assistant", "content": response})
        asyncio.run(audio.speak(response))
        st.rerun()