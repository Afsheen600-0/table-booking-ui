import streamlit as st
import requests
import uuid

# Configuration
WEBHOOK_URL = "https://hammadulhassan90.app.n8n.cloud/webhook/4b54feca-c7ae-4b2b-83eb-7315280b2b01"

# Page setup
st.set_page_config(
    page_title="Table Booking Chatbot",
    page_icon="🍽️",
    layout="centered"
)

st.title("🍽️ Table Booking Agent")
st.markdown("Welcome! I can help you book a table. How can I assist you today?")

# Initialize chat variables in session state
if "messages" not in st.session_state:
    st.session_state.messages = []

if "session_id" not in st.session_state:
    st.session_state.session_id = str(uuid.uuid4())

# Display existing chat messages
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Handle user input
prompt = st.chat_input("Type your message here...")
if prompt:
    # 1. Display user message
    with st.chat_message("user"):
        st.markdown(prompt)
    
    # 2. Add user message to session state
    st.session_state.messages.append({"role": "user", "content": prompt})
    
    # 3. Request bot response from n8n webhook
    with st.chat_message("assistant"):
        with st.spinner("Connecting to agent..."):
            try:
                # n8n default AI Chat trigger typically expects "chatInput" and "sessionId" 
                # We also include "message", "text", and "query" just in case it's a generic webhook
                payload = {
                    "chatInput": prompt,
                    "sessionId": st.session_state.session_id,
                    "message": prompt,
                    "text": prompt,
                    "query": prompt
                }
                
                response = requests.post(WEBHOOK_URL, json=payload, timeout=30)
                response.raise_for_status()
                
                # Attempt to parse response from n8n
                try:
                    data = response.json()
                    bot_reply = None
                    
                    # Try to extract common fields that n8n might return
                    if isinstance(data, dict):
                        bot_reply = data.get("output") or data.get("message") or data.get("text") or data.get("response")
                    
                    # If we couldn't find a specific field or it returned something else, convert it to string
                    if not bot_reply:
                        bot_reply = str(data)
                
                except ValueError:
                    # Generic fallback if response is purely plain text
                    bot_reply = response.text
                
                # 4. Display bot message
                st.markdown(bot_reply)
                
                # 5. Add bot message to session state
                st.session_state.messages.append({"role": "assistant", "content": bot_reply})
                
            except requests.exceptions.RequestException as e:
                error_msg = f"Sorry, there was an error communicating with the agent. Please try again later. ({e})"
                st.error(error_msg)
                st.session_state.messages.append({"role": "assistant", "content": error_msg})
