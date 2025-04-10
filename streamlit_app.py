import streamlit as st
import requests
import uuid

# ========== Configuration ==========
API_URL = "http://127.0.0.1:8080"
CAPCUT_THEME = {
    "primaryColor": "#000000",
    "backgroundColor": "#FFFFFF",
    "secondaryBackgroundColor": "#FFFFFF",
    "textColor": "#000000",
    "font": "sans serif"
}

st.set_page_config(
    page_title="CapCut AI Assistant",
    page_icon="🎬",
    layout="wide"
)

# Apply custom theme
st.markdown(f"""
<style>
    .survey-badge {{
        background-color: #4CAF50;
        color: white !important;
        padding: 8px 16px;
        border-radius: 20px;
        display: inline-block;
        margin: 10px 0;
    }}
    .stChatInput textarea {{
        border: 1px solid #4CAF50 !important;
    }}
</style>
""", unsafe_allow_html=True)

# ========== Session State Initialization ==========
if 'chat_history' not in st.session_state:
    st.session_state.chat_history = []
if 'survey_active' not in st.session_state:
    st.session_state.survey_active = False
if 'survey_session' not in st.session_state:
    st.session_state.survey_session = str(uuid.uuid4())
if 'awaiting_survey_response' not in st.session_state:
    st.session_state.awaiting_survey_response = False
if 'current_choices' not in st.session_state:
    st.session_state.current_choices = []

# ========== Helper Functions ==========
def handle_survey_interaction(user_input: str):
    """Handle survey conversation flow with error handling"""
    try:
        response = requests.post(
            f"{API_URL}/survey",
            json={
                'session_id': st.session_state.survey_session,
                'message': user_input
            },
            timeout=5  # Add timeout for better error handling
        )
        
        if response.status_code == 200:
            return response.json()
        else:
            st.error(f"Survey error: {response.text}")
            return None
            
    except requests.exceptions.RequestException as e:
        st.error(f"Connection error: {str(e)}")
        return None

def display_chat_message(message: str, is_user: bool = False):
    """Display chat messages with survey styling"""
    avatar = "👤" if is_user else "🤖"
    with st.chat_message("user" if is_user else "assistant", avatar=avatar):
        if "💎 PREMIUM" in message:
            st.markdown(f'<div class="premium-badge">💎 PREMIUM FEATURE</div>', unsafe_allow_html=True)
            message = message.replace("💎 PREMIUM FEATURE", "")
        elif "📝 Survey:" in message:
            st.markdown(f'<div class="survey-badge">{message}</div>', unsafe_allow_html=True)
        else:
            st.markdown(message)

# ========== Main Interface ==========
st.title("🎬 CapCut AI Assistant")
st.markdown("Flexible editing • Magical AI tools • Team collaboration • Stock assets")

# Survey trigger sidebar with feature visuals
with st.sidebar:
    st.markdown("""
    <style>
        .feature-card {
            background: #FFFFFF;
            border-radius: 10px;
            padding: 15px;
            margin: 15px 0;
            box-shadow: 0 2px 5px rgba(0,0,0,0.1);
            transition: transform 0.2s;
        }
        .feature-card:hover {
            transform: translateY(-3px);
        }
        .feature-icon {
            font-size: 24px;
            color: #4CAF50;
            margin-bottom: 10px;
        }
    </style>
    """, unsafe_allow_html=True)

    # Survey trigger button
    if not st.session_state.survey_active:
        if st.button("📝 Take Quick Survey (2 mins)", help="Help us improve!", key="survey_trigger"):
            st.session_state.survey_active = True
            st.session_state.awaiting_survey_response = True
            st.session_state.survey_session = str(uuid.uuid4())
            st.rerun()

    # Feature cards
    st.markdown("""
    <div class="feature-card">
        <div class="feature-icon">🎥</div>
        <h3>Smart Trimming</h3>
        <p>AI-powered scene detection for perfect cuts every time.</p>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("""
    <div class="feature-card">
        <div class="feature-icon">✨</div>
        <h3>Magic Effects</h3>
        <p>100+ filters and transitions powered by AI.</p>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("""
    <div class="feature-card">
        <div class="feature-icon">📈</div>
        <h3>4K Export</h3>
        <p>Cinema-quality video rendering (Pro feature).</p>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("""
    <div class="feature-card">
        <div class="feature-icon">🤖</div>
        <h3>AI Assistant</h3>
        <p>24/7 editing help and suggestions.</p>
    </div>
    """, unsafe_allow_html=True)


# Initialize conversation
if not st.session_state.chat_history:
    st.session_state.chat_history.append({
        'text': "Hi! I'm your CapCut Assistant. 🚀 How can I help you with video editing today?",
        'is_user': False
    })

# Display chat history
for msg in st.session_state.chat_history:
    display_chat_message(msg['text'], msg['is_user'])

# Survey interaction flow
if st.session_state.survey_active:
    # Initial survey prompt
    if st.session_state.awaiting_survey_response:
        with st.spinner("Loading survey..."):
            survey_response = handle_survey_interaction("")
            
        if survey_response:
            # Store choices and question from backend response
            st.session_state.current_choices = survey_response.get('choices', [])
            st.session_state.chat_history.append({
                'text': f"📝 Survey: {survey_response.get('response', '')}",
                'is_user': False
            })
            st.session_state.awaiting_survey_response = False
            st.rerun()
    
    # Display choices as buttons in columns
    if len(st.session_state.current_choices) > 0:
        cols = st.columns(2)
        for idx, choice in enumerate(st.session_state.current_choices):
            with cols[idx % 2]:
                if st.button(choice, key=f"survey_opt_{idx}"):
                    # Add user selection to chat history
                    st.session_state.chat_history.append({
                        'text': choice,
                        'is_user': True
                    })
                    
                    with st.spinner("Processing..."):
                        survey_response = handle_survey_interaction(choice)
                    
                    if survey_response:
                        if survey_response.get('completed', False):
                            # End survey and thank user
                            st.session_state.survey_active = False
                            st.session_state.chat_history.append({
                                'text': "📝 Thank you for your feedback! 🎉 Your insights help us improve.",
                                'is_user': False
                            })
                        else:
                            # Update choices for next question
                            st.session_state.current_choices = survey_response.get('choices', [])
                            st.session_state.chat_history.append({
                                'text': f"📝 Survey: {survey_response.get('response', '')}",
                                'is_user': False
                            })
                    
                    # Refresh UI for next step
                    st.rerun()

# Regular chat interface
else:
    user_input = st.chat_input("Your video editing question...")
    if user_input:
        # Add user input to chat history
        st.session_state.chat_history.append({'text': user_input, 'is_user': True})
        
        try:
            response = requests.post(
                f"{API_URL}/chat",
                json={
                    'message': user_input,
                    'session_id': st.session_state.get('session_id')
                },
                timeout=5
            )
            
            if response.status_code == 200:
                data = response.json()
                bot_response = data.get('response', "I'm here to help!")
                
                if not st.session_state.get('session_id'):
                    # Store session ID from backend response
                    st.session_state['session_id'] = data.get('session_id')
                
                # Add bot response to chat history
                st.session_state.chat_history.append({
                    'text': bot_response,
                    'is_user': False
                })
                
                # Periodic survey prompt after every 5 interactions
                interaction_count = st.session_state.get('interaction_count', 0) + 1
                if interaction_count % 5 == 0:
                    st.session_state.chat_history.append({
                        'text': "📝 We'd love your feedback! Type 'survey' or click the button to help us improve!",
                        'is_user': False
                    })
                
                # Update interaction count in session state
                st.session_state['interaction_count'] = interaction_count
                
            else:
                # Handle backend errors gracefully
                st.error("Failed to get response from assistant.")
            
        except Exception as e:
            # Handle connection errors gracefully
            st.error(f"Connection error: {str(e)}")
        
        # Refresh UI after processing input or errors
        st.rerun()
