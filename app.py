import streamlit as st
import asyncio
# Import your teammates' code
import tools
import agent
import audio

st.set_page_config(page_title="Autonomix Voice Agent", layout="centered")
st.title("🎙️ AI Customer Support Agent")

# Initialize DB (Run once)
if "db_init" not in st.session_state:
    tools.init_db()
    st.session_state.db_init = True

if "messages" not in st.session_state:
    st.session_state.messages = []

# Display Chat History
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

col1, col2 = st.columns(2)

with col1:
    if st.button("🎤 Start Listening"):
        with st.spinner("Listening..."):
            # CALL PERSON C's CODE
            user_text = audio.listen() 
            
        st.session_state.messages.append({"role": "user", "content": user_text})
        with st.chat_message("user"):
            st.markdown(user_text)

        with st.spinner("Thinking..."):
            # CALL PERSON B's CODE
            response_text = agent.get_response(user_text)
        
        st.session_state.messages.append({"role": "assistant", "content": response_text})
        with st.chat_message("assistant"):
            st.markdown(response_text)
            
        with st.spinner("Speaking..."):
            # CALL PERSON C's CODE
            audio.speak(response_text)

with col2:
    if st.button("🔄 Reset"):
        st.session_state.messages = []
        st.rerun()