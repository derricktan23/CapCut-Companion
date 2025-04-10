from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import re
import chromadb
from chromadb.api.types import Documents, EmbeddingFunction, Embeddings
import google.generativeai as genai
import logging
import os
import spacy
import uuid
from typing import Dict, Tuple

# Initialize Flask app
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///capcut.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# Configure Gemini
genai.configure(api_key=os.getenv("GOOGLE_API_KEY", "AIzaSyB2xtOw_jC7uOGb4cHd5ITMmW9ZCqdMx9Q"))

# Load NLP model
nlp = spacy.load("en_core_web_sm")

# Database Models

class CustomerInsight(db.Model):
    __tablename__ = 'customer_insights'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), nullable=False)
    use_case = db.Column(db.String(100), nullable=False)

class HelpDocument(db.Model):
    __tablename__ = 'help_documents'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    content = db.Column(db.Text, nullable=False)
    doc_type = db.Column(db.String(50), index=True)
    uploaded_at = db.Column(db.DateTime, default=datetime.utcnow)

# Add to Database Models
class SurveyResponse(db.Model):
    __tablename__ = 'survey_responses'
    id = db.Column(db.Integer, primary_key=True)
    session_id = db.Column(db.String(36), index=True)
    question = db.Column(db.String(200))
    answer = db.Column(db.Text)
    responded_at = db.Column(db.DateTime, default=datetime.utcnow)


# Initialize database
with app.app_context():
    db.create_all()

# RAG Configuration
class CapcutEmbeddingFunction(EmbeddingFunction):
    def __init__(self):
        self.model = 'models/embedding-001'
    
    def __call__(self, input: Documents) -> Embeddings:
        """Generate embeddings using Gemini API"""
        try:
            return genai.embed_content(
                model=self.model,
                content=input,
                task_type="retrieval_document"
            )["embedding"]
        except Exception as e:
            logging.error(f"Embedding error: {str(e)}")
            return [[]] * len(input)  # Return empty embeddings on failure

def get_chroma_collection():
    """Get or create Chroma collection with error handling"""
    try:
        client = chromadb.PersistentClient(path='./capcut_rag_store')
        return client.get_or_create_collection(
            name="capcut_knowledge_v1",
            embedding_function=CapcutEmbeddingFunction()
        )
    except Exception as e:
        logging.error(f"ChromaDB error: {str(e)}")
        raise

# Core Functions
def preprocess_text(text: str) -> str:
    """Clean user input for processing"""
    return re.sub(r'[^\w\s\?]', '', text.lower()).strip()

def detect_editing_intent(text: str) -> Tuple[str, Dict]:
    """Analyze user input for video editing context"""
    try:
        doc = nlp(text)
        intent = "general"
        entities = {}
        
        # Detection logic
        editing_verbs = {'edit', 'trim', 'cut', 'merge', 'adjust', 'add'}
        tools = {'transition', 'filter', 'text', 'effect', 'audio'}
        
        for token in doc:
            if token.lemma_ in editing_verbs:
                intent = "editing_operation"
            if token.lemma_ in tools:
                entities.setdefault('tools', []).append(token.text)
        
        if 'premium' in text or 'pro' in text:
            entities['premium'] = True
            
        return intent, entities
    except Exception as e:
        logging.error(f"NLU error: {str(e)}")
        return "general", {}

# API Endpoints
@app.route('/chat', methods=['POST'])
def handle_chat():
    """Process chat requests with video editing context"""
    data = request.get_json()
    
    # Validate request
    if not data or 'message' not in data:
        return jsonify({"error": "Invalid request format"}), 400
        
    user_message = data.get('message', '').strip()
    session_id = data.get('session_id', str(uuid.uuid4()))

    if not user_message:
        return jsonify({"error": "Empty message received"}), 400

    try:
        # Preprocess input
        cleaned_text = preprocess_text(user_message)
        if not cleaned_text:
            return jsonify({"error": "Invalid message content"}), 400

        # Intent detection
        intent, entities = detect_editing_intent(cleaned_text)
        
        # Retrieve context
        rag_context = []
        try:
            collection = get_chroma_collection()
            if collection.count() > 0:
                results = collection.query(
                    query_texts=[cleaned_text],
                    n_results=3,
                    include=["documents"]
                )
                rag_context = results['documents'][0] if results['documents'] else []
        except Exception as e:
            logging.error(f"RAG error: {str(e)}")

        # Generate response
        try:
            prompt = f"""As CapCut's AI assistant specializing in video editing:
            Context: {" | ".join(rag_context[:3])}
            Query: {user_message}
            
            Provide a concise answer under 50 words. {"[PREMIUM]" if entities.get('premium') else ''}"""
            
            model = genai.GenerativeModel('gemini-1.5-flash')
            response = model.generate_content(
                prompt,
                safety_settings={
                    'HARM_CATEGORY_HARASSMENT': 'BLOCK_NONE',
                    'HARM_CATEGORY_HATE_SPEECH': 'BLOCK_NONE',
                    'HARM_CATEGORY_SEXUALLY_EXPLICIT': 'BLOCK_NONE',
                    'HARM_CATEGORY_DANGEROUS_CONTENT': 'BLOCK_NONE'
                }
            )
            response_text = response.text[:500]  # Limit response length
        except Exception as e:
            logging.error(f"Generation error: {str(e)}")
            response_text = "I'm having trouble answering that. Please try again later."

        return jsonify({
            "response": response_text,
            "session_id": session_id,
            "intent": intent
        })
        
    except Exception as e:
        logging.error(f"Critical error: {str(e)}")
        return jsonify({"error": "Internal server error"}), 500

@app.route('/rag/documents', methods=['GET'])
def manage_documents():
    """Handle RAG document operations"""
    try:
        documents = HelpDocument.query.order_by(HelpDocument.uploaded_at.desc()).all()
        return jsonify([{
            "id": doc.id,
            "title": doc.title,
            "type": doc.doc_type,
            "summary": doc.content[:100] + "..." if len(doc.content) > 100 else doc.content
        } for doc in documents])
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    
def process_survey_step(state, user_input):
    """Dynamic survey flow logic with updated options"""
    flow = {
        'start': {
            'question': "📝 Did you enjoy using CapCut today?",
            'choices': ["👍", "👎"],  # Thumbs up/down
            'handler': lambda x: 'recommendation' if x in ["👍", "👎"] else 'start'
        },
        'recommendation': {
            'question': "📝 How likely are you to recommend us to a friend?",
            'choices': ["Likely", "Unlikely", "Neutral"],  # Updated options
            'handler': lambda x: 'feature_usage' if x in ["Likely", "Unlikely", "Neutral"] else 'recommendation'
        },
        'feature_usage': {
            'question': "📝 Which feature did you use most?",
            'choices': ["Trimming", "Effects", "Text", "Transitions"],
            'handler': lambda x: 'improvement' if x in ["Trimming", "Effects", "Text", "Transitions"] else 'feature_usage'
        },
        'improvement': {
            'question': "📝 What would you like us to focus on improving?",
            'choices': ["Ease of Use", "Performance", "Templates", "Tutorials"],  # Updated options
            'handler': lambda x: 'end'
        }
    }
    
    current_step = state['step']
    step_config = flow[current_step]
    
    # Validate input for multiple-choice steps
    if step_config['choices'] and user_input not in step_config['choices']:
        return {
            'next_question': step_config['question'],
            'choices': step_config['choices'],
            'current_question': None,
            'completed': False
        }
    
    # Store answer
    state['answers'][current_step] = user_input
    next_step = step_config['handler'](user_input)
    
    # Update state
    state['step'] = next_step
    
    return {
        'next_question': flow.get(next_step, {}).get('question', ''),
        'choices': flow.get(next_step, {}).get('choices', []),
        'current_question': step_config['question'],
        'completed': next_step == 'end'
    }


# Add Survey Endpoint
# Add to existing SurveyResponse model and endpoints
@app.route('/survey', methods=['POST'])
def handle_survey():
    """Handle interactive survey flow with multiple-choice answers"""
    data = request.get_json()
    session_id = data.get('session_id')
    user_input = data.get('message', '').strip()
    
    if not session_id:
        return jsonify({"error": "Missing session ID"}), 400

    survey_state = get_survey_state(session_id)
    
    try:
        processed = process_survey_step(survey_state, user_input)
        
        if processed['current_question']:
            response = SurveyResponse(
                session_id=session_id,
                question=processed['current_question'],
                answer=user_input
            )
            db.session.add(response)
            db.session.commit()
        
        return jsonify({
            "response": processed['next_question'],
            "choices": processed.get('choices', []),
            "completed": processed['completed'],
            "session_id": session_id
        })
        
    except Exception as e:
        logging.error(f"Survey error: {str(e)}")
        return jsonify({"error": "Survey processing failed"}), 500



def get_survey_state(session_id):
    """Get or initialize survey state"""
    if not hasattr(app, 'survey_states'):
        app.survey_states = {}
    
    if session_id not in app.survey_states:
        app.survey_states[session_id] = {
            'step': 'start',
            'answers': {}
        }
    
    return app.survey_states[session_id]


# Endpoint: Fetch Customer Insights
@app.route('/customer-insights', methods=['GET'])
def get_customer_insights():
    """Handle GET requests for customer insights"""
    try:
        # Fetch customer insights from the database
        customer_insights = CustomerInsight.query.all()
        results = [
            {"id": insight.id, "name": insight.name, "email": insight.email, "use_case": insight.use_case}
            for insight in customer_insights
        ]
        return jsonify({"contacts": results}), 200
    except Exception as e:
        logging.error(f"Error fetching customer insights: {str(e)}")
        return jsonify({"error": "Failed to fetch customer insights"}), 500

# Endpoint: Fetch RAG Documents
@app.route('/rag-documents', methods=['GET'])
def get_rag_documents():
    """Handle GET requests for RAG documents"""
    try:
        # Fetch RAG documents from the database
        rag_documents = HelpDocument.query.order_by(HelpDocument.uploaded_at.desc()).all()
        results = [
            {"id": doc.id, "title": doc.title, "type": doc.doc_type, "uploaded_at": doc.uploaded_at.strftime("%Y-%m-%d %H:%M:%S")}
            for doc in rag_documents
        ]
        return jsonify({"documents": results}), 200
    except Exception as e:
        logging.error(f"Error fetching RAG documents: {str(e)}")
        return jsonify({"error": "Failed to fetch RAG documents"}), 500

# Endpoint: Fetch Survey Results
@app.route('/survey/results', methods=['GET'])
def get_survey_results():
    """Handle GET requests for survey results"""
    try:
        # Mocked survey results (replace with database queries as needed)
        survey_results = {
            "ratings": [
                {"rating": 5, "count": 10},
                {"rating": 4, "count": 7},
                {"rating": 3, "count": 5},
                {"rating": 2, "count": 2},
                {"rating": 1, "count": 1}
            ],
            "themes": [
                {"theme": "Ease of Use", "count": 15},
                {"theme": "Performance", "count": 10},
                {"theme": "Templates", "count": 8},
                {"theme": "Tutorials", "count": 5}
            ],
            "responses": [
                {"id": 1, "question": "Did you enjoy using CapCut today?", "answer": "👍"},
                {"id": 2, "question": "How likely are you to recommend us to a friend?", "answer": "Likely"}
            ]
        }
        return jsonify(survey_results), 200
    except Exception as e:
        logging.error(f"Error fetching survey results: {str(e)}")
        return jsonify({"error": "Failed to fetch survey results"}), 500


if __name__ == "__main__":
    app.run(host='0.0.0.0', port=8080, debug=True)
