import streamlit as st
import requests
import uuid
from datetime import datetime  # Add this line here

# ========== Updated Configuration ==========
API_URL = "http://localhost:8080"  # Changed to local backend
SESSION_TIMEOUT = 300  # 5 minutes for session persistence

# ========== Enhanced Theme Configuration ==========
CAPCUT_THEME = {
    "primaryColor": "#4CAF50",
    "backgroundColor": "#F5F5F5",
    "secondaryBackgroundColor": "#FFFFFF",
    "textColor": "#000000",
    "font": "sans serif"
}

st.set_page_config(
    page_title="CapCut AI Assistant",
    page_icon="🎬",
    layout="centered"
)

# Apply custom theme
st.markdown(f"""
<style>
    .survey-badge {{
        background-color: {CAPCUT_THEME['primaryColor']};
        color: white !important;
        padding: 8px 16px;
        border-radius: 20px;
        display: inline-block;
        margin: 10px 0;
    }}
    .stChatInput textarea {{
        border: 2px solid {CAPCUT_THEME['primaryColor']} !important;
        border-radius: 8px !important;
    }}
</style>
""", unsafe_allow_html=True)

# ========== Session State Initialization ==========
if 'chat_history' not in st.session_state:
    st.session_state.chat_history = []
if 'session_id' not in st.session_state:
    st.session_state.session_id = str(uuid.uuid4())
if 'last_interaction' not in st.session_state:
    st.session_state.last_interaction = datetime.now()

# ========== Updated Helper Functions ==========
def handle_chat_request(user_input: str) -> dict:
    """Handle chat requests with offline model backend"""
    try:
        response = requests.post(
            f"{API_URL}/chat",
            json={
                'message': user_input,
                'session_id': st.session_state.session_id
            },
            timeout=10
        )
        return response.json() if response.status_code == 200 else None
    except requests.exceptions.RequestException as e:
        st.error(f"Connection error: {str(e)}")
        return None

def display_response(response_data: dict):
    """Display formatted response from backend"""
    if not response_data:
        return
    
    # Update session ID if needed
    st.session_state.session_id = response_data.get('session_id', st.session_state.session_id)
    
    # Display response with context-aware formatting
    response_text = response_data.get('response', '')
    intent = response_data.get('intent', 'general')
    
    if intent == 'editing_operation':
        st.markdown(f"**🎯 Editing Assistant:** {response_text}")
    else:
        st.markdown(f"**🤖 CapCut AI:** {response_text}")

# ========== Main Interface ==========
st.title("🎬 CapCut AI Assistant")
st.markdown("""
**Smart Editing Features:**
- 🎥 AI-powered trimming
- ✨ Magic effects & filters
- 🎞️ Pro transitions
- 🤖 24/7 AI assistance
""")

# Display chat history
for msg in st.session_state.chat_history:
    if msg['is_user']:
        st.markdown(f"**👤 You:** {msg['text']}")
    else:
        st.markdown(f"**🤖 Assistant:** {msg['text']}")

# Chat input with session management
user_input = st.chat_input("Ask about video editing...")
if user_input:
    # Add user input to history
    st.session_state.chat_history.append({'text': user_input, 'is_user': True})
    
    # Get backend response
    response_data = handle_chat_request(user_input)
    
    if response_data:
        # Add response to history
        st.session_state.chat_history.append({
            'text': response_data['response'],
            'is_user': False
        })
        
        # Display response with intent-based formatting
        display_response(response_data)
        
        # Update interaction timestamp
        st.session_state.last_interaction = datetime.now()
        
        # Rerun to refresh display
        st.rerun()
    else:
        st.error("Failed to get response from AI assistant")

# Session timeout handling
if (datetime.now() - st.session_state.last_interaction).seconds > SESSION_TIMEOUT:
    st.warning("Session timed out due to inactivity")
    st.session_state.clear()
    st.rerun()
