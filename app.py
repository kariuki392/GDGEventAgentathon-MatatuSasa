# pyrefly: ignore [missing-import]
import streamlit as st
import os
from agent import get_agent_client, create_chat_session

# Set page config
st.set_page_config(
    page_title="Matatu Sasa - Nairobi Transit Agent",
    page_icon="🚐",
    layout="centered"
)

# Custom CSS for aesthetics
st.markdown("""
<style>
    .stApp {
        background-color: #f8f9fa;
        color: #212529;
    }
    .chat-header {
        text-align: center;
        padding: 20px;
        background: linear-gradient(90deg, #FFD700 0%, #FFA500 100%);
        border-radius: 10px;
        margin-bottom: 20px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
    }
    .chat-header h1 {
        color: #000;
        margin: 0;
        font-family: 'Inter', sans-serif;
    }
    .chat-header p {
        color: #333;
        font-size: 1.1em;
    }
</style>
""", unsafe_allow_html=True)

st.markdown('<div class="chat-header"><h1>🚐 Matatu Sasa</h1><p>Your street-smart Nairobian transit assistant</p></div>', unsafe_allow_html=True)

# Ensure API Key is available
if not os.getenv("GEMINI_API_KEY"):
    st.warning("⚠️ GEMINI_API_KEY is not set. Please enter it below to continue:")
    api_key = st.text_input("Gemini API Key", type="password")
    if api_key:
        os.environ["GEMINI_API_KEY"] = api_key
        st.success("API Key set! Let's go.")
        st.rerun()
    else:
        st.stop()

# Initialize session state variables
if "chat_session" not in st.session_state:
    try:
        st.session_state.client = get_agent_client()
        st.session_state.chat_session = create_chat_session(st.session_state.client)
    except Exception as e:
        st.error(f"Error initializing agent: {e}")
        st.stop()

if "messages" not in st.session_state:
    st.session_state.messages = []
    # Add initial greeting
    st.session_state.messages.append({
        "role": "model", 
        "content": "Niaje! I'm Matatu Sasa. Where are you heading to today? (e.g., 'How do I get from Kawangware to Ruai?')"
    })

# Display chat messages from history on app rerun
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Accept user input
if prompt := st.chat_input("Where to?"):
    # Add user message to chat history
    st.session_state.messages.append({"role": "user", "content": prompt})
    
    # Display user message in chat message container
    with st.chat_message("user"):
        st.markdown(prompt)

    # Display assistant response in chat message container
    with st.chat_message("model"):
        with st.spinner("Ngoja kidogo, let me check the routes..."):
            try:
                # Send message to Gemini
                response = st.session_state.chat_session.send_message(prompt)
                st.markdown(response.text)
                
                # Add assistant response to chat history
                st.session_state.messages.append({"role": "model", "content": response.text})
            except Exception as e:
                error_msg = f"Pole, something went wrong: {str(e)}"
                st.error(error_msg)
                st.session_state.messages.append({"role": "model", "content": error_msg})
