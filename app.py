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
    @import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;600;800&display=swap');
    
    /* Hide Streamlit default UI elements for a cleaner look */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    
    .stApp {
        background-color: #0f172a;
        color: #f8fafc;
        font-family: 'Outfit', sans-serif;
    }
    
    /* Premium Header Styling */
    .chat-header {
        text-align: center;
        padding: 35px 20px;
        background: linear-gradient(135deg, #f59e0b 0%, #d97706 100%);
        border-radius: 20px;
        margin-bottom: 35px;
        box-shadow: 0 10px 30px -5px rgba(245, 158, 11, 0.4);
        position: relative;
        overflow: hidden;
        animation: fadeInDown 0.8s ease-out;
    }
    
    /* Subtle background pattern in header */
    .chat-header::after {
        content: '';
        position: absolute;
        top: 0; left: 0; right: 0; bottom: 0;
        background: radial-gradient(circle at right center, rgba(255,255,255,0.2) 0%, transparent 60%);
        pointer-events: none;
    }

    .chat-header h1 {
        color: #ffffff;
        margin: 0;
        font-weight: 800;
        font-size: 3rem;
        letter-spacing: -1px;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.15);
    }
    
    .chat-header p {
        color: #fffbeb;
        font-size: 1.25rem;
        font-weight: 300;
        margin-top: 10px;
        opacity: 0.95;
    }
    
    /* Chat Message Bubbles */
    [data-testid="stChatMessage"] {
        border-radius: 16px;
        padding: 20px;
        margin-bottom: 15px;
        background: rgba(30, 41, 59, 0.6);
        border: 1px solid rgba(255, 255, 255, 0.05);
        backdrop-filter: blur(10px);
        -webkit-backdrop-filter: blur(10px);
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
        transition: transform 0.2s ease, box-shadow 0.2s ease, background 0.2s ease;
    }
    
    [data-testid="stChatMessage"]:hover {
        transform: translateY(-2px);
        box-shadow: 0 8px 15px -3px rgba(0, 0, 0, 0.2);
        background: rgba(30, 41, 59, 0.8);
    }
    
    /* Input Container Styling */
    [data-testid="stChatInput"] {
        padding-bottom: 20px;
    }
    
    /* Animations */
    @keyframes fadeInDown {
        from {
            opacity: 0;
            transform: translate3d(0, -30px, 0);
        }
        to {
            opacity: 1;
            transform: translate3d(0, 0, 0);
        }
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
