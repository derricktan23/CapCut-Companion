import streamlit as st
import pandas as pd
import requests
from datetime import datetime

# ========== Configuration ==========
API_URL = "https://capcut-companion-flaskapp.onrender.com"
ADMIN_THEME = {
    "primaryColor": "#4CAF50",
    "backgroundColor": "#FFFFFF",
    "secondaryBackgroundColor": "#F1F8E9",
    "textColor": "#000000",
    "font": "sans serif"
}

st.set_page_config(
    page_title="Admin Dashboard - CapCut AI Assistant",
    page_icon="🛠️",
    layout="wide"
)

# Apply custom theme
st.markdown(f"""
<style>
    .stApp {{
        background-color: {ADMIN_THEME['backgroundColor']};
        color: {ADMIN_THEME['textColor']};
        font-family: {ADMIN_THEME['font']};
    }}
    .stSidebar {{
        background-color: {ADMIN_THEME['secondaryBackgroundColor']};
    }}
    .header {{
        font-size: 24px;
        font-weight: bold;
        color: {ADMIN_THEME['primaryColor']};
        margin-bottom: 10px;
    }}
    .section {{
        padding: 20px;
        border-radius: 10px;
        background-color: {ADMIN_THEME['secondaryBackgroundColor']};
        margin-bottom: 20px;
    }}
</style>
""", unsafe_allow_html=True)


# Add to admin_app.py
def fetch_survey_results():
    """Fetch survey data from backend"""
    try:
        response = requests.get(f"{API_URL}/survey/results")
        if response.status_code == 200:
            return response.json()
        return {}
    except Exception as e:
        st.error(f"Error: {str(e)}")
        return {}

    st.header("📝 Survey Results")
    
    results = fetch_survey_results()
    
    if results:
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("Rating Distribution")
            ratings = pd.DataFrame(results['ratings'])
            st.bar_chart(ratings)
        
        with col2:
            st.subheader("Common Feedback Themes")
            themes = pd.DataFrame(results['themes'])
            st.dataframe(themes)
        
        st.subheader("Raw Responses")
        st.dataframe(pd.DataFrame(results['responses']))
    else:
        st.info("No survey responses yet")

# ========== Helper Functions ==========
def fetch_customer_insights():
    """Fetch customer insights from the backend."""
    try:
        response = requests.get(f"{API_URL}/customer-insights")
        if response.status_code == 200:
            return pd.DataFrame(response.json().get('contacts', []))
        else:
            st.error(f"Failed to fetch customer insights: {response.status_code}")
            return pd.DataFrame()
    except Exception as e:
        st.error(f"Error connecting to server: {str(e)}")
        return pd.DataFrame()

def fetch_rag_documents():
    """Fetch RAG documents from the backend."""
    try:
        response = requests.get(f"{API_URL}/rag-documents")
        if response.status_code == 200:
            return response.json().get('documents', [])
        else:
            st.error(f"Failed to fetch RAG documents: {response.status_code}")
            return []
    except Exception as e:
        st.error(f"Error connecting to server: {str(e)}")
        return []

def upload_rag_document(title, content, doc_type):
    """Upload a new RAG document to the backend."""
    try:
        payload = {
            "title": title,
            "content": content,
            "doc_type": doc_type
        }
        response = requests.post(f"{API_URL}/upload-rag-document", json=payload)
        if response.status_code == 201:
            st.success("Document uploaded successfully!")
            return True
        else:
            st.error(f"Failed to upload document: {response.status_code}")
            return False
    except Exception as e:
        st.error(f"Error uploading document: {str(e)}")
        return False

# ========== Main Interface ==========
st.title("🛠️ Admin Dashboard - CapCut AI Assistant")
st.markdown("Manage customer insights, train the chatbot with RAG documents, and monitor system performance.")

# Tabs for different admin functionalities
tab1, tab2, tab3, tab4 = st.tabs(["Customer Insights", "RAG Management", "Train Chatbot", "Survey Results"])

# Tab 1: Customer Insights
with tab1:
    st.header("📊 Customer Insights")
    
    # Fetch and display customer insights
    with st.spinner("Fetching customer insights..."):
        customer_data = fetch_customer_insights()
    
    if not customer_data.empty:
        st.dataframe(customer_data)
        
        # Download button for customer data
        csv_data = customer_data.to_csv(index=False).encode('utf-8')
        st.download_button(
            label="📥 Download Customer Data",
            data=csv_data,
            file_name="customer_insights.csv",
            mime="text/csv"
        )
    else:
        st.info("No customer data available.")

# Tab 2: RAG Management
with tab2:
    st.header("📚 RAG Document Management")
    
    # Fetch and display existing RAG documents
    with st.spinner("Fetching RAG documents..."):
        rag_documents = fetch_rag_documents()
    
    if rag_documents:
        for doc in rag_documents:
            with st.expander(doc["title"]):
                st.write(f"**Type:** {doc['doc_type']}")
                st.write(f"**Uploaded At:** {doc['uploaded_at']}")
                st.write(doc["content"])
    else:
        st.info("No RAG documents available.")
    
    # Upload a new RAG document
    st.subheader("Upload New Document")
    
    with st.form("upload_form"):
        title = st.text_input("Document Title")
        content = st.text_area("Document Content", height=200)
        doc_type = st.selectbox("Document Type", ["FAQ", "Tutorial", "Guide"])
        
        submitted = st.form_submit_button("Upload Document")
        
        if submitted and title and content and doc_type:
            upload_rag_document(title, content, doc_type)

# Tab 3: Train Chatbot
with tab3:
    st.header("🤖 Train Chatbot with New Data")
    
    # Instructions for training the chatbot
    st.markdown("""
        To train the chatbot, ensure that all relevant RAG documents are uploaded.
        
        When ready, click the button below to trigger the training process.
        
        The chatbot will use these documents to improve its responses.
    """)
    
    # Trigger training process with a unique key
    if st.button("Start Training", key="train_chatbot_button"):
        with st.spinner("Training the chatbot..."):
            try:
                response = requests.post(f"{API_URL}/train-chatbot")
                if response.status_code == 200:
                    st.success("Chatbot training completed successfully!")
                else:
                    st.error(f"Failed to train chatbot: {response.status_code}")
            except Exception as e:
                st.error(f"Error starting training process: {str(e)}")

# Tab 4: Survey Results
with tab4:
    st.header("📝 Survey Results")
    
    results = fetch_survey_results()
    
    if results:
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("Rating Distribution")
            ratings = pd.DataFrame(results['ratings'])
            st.bar_chart(ratings)
        
        with col2:
            st.subheader("Common Feedback Themes")
            themes = pd.DataFrame(results['themes'])
            st.dataframe(themes)
        
        st.subheader("Raw Responses")
        st.dataframe(pd.DataFrame(results['responses']))
    else:
        st.info("No survey responses yet.")

    st.header("🤖 Train Chatbot with New Data")
    
    # Instructions for training the chatbot
    st.markdown("""
        To train the chatbot, ensure that all relevant RAG documents are uploaded.
        
        When ready, click the button below to trigger the training process.
        
        The chatbot will use these documents to improve its responses.
    """)
    
    # Trigger training process (mocked here)
    if st.button("Start Training"):
        with st.spinner("Training the chatbot..."):
            try:
                response = requests.post(f"{API_URL}/train-chatbot")
                if response.status_code == 200:
                    st.success("Chatbot training completed successfully!")
                else:
                    st.error(f"Failed to train chatbot: {response.status_code}")
            except Exception as e:
                st.error(f"Error starting training process: {str(e)}")
