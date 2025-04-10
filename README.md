# CapCut Companion Backend

The **CapCut Companion Backend** is a Flask application that supports the CapCut AI Assistant. It provides APIs for chatbot interactions, survey management, document handling, and customer insights.

---

## **Table of Contents**
1. [Features](#features)
2. [Setup Instructions](#setup-instructions)
3. [API Endpoints](#api-endpoints)
4. [Database Models](#database-models)
5. [Survey Flow Logic](#survey-flow-logic)
6. [Error Handling](#error-handling)
7. [Contributing](#contributing)

---

## **Features**

- **Chatbot API**: AI responses for video editing queries using SpaCy and ChromaDB.
- **Survey Management**: Dynamic surveys with user responses stored for analysis.
- **RAG Document Management**: Upload and retrieve help documents.
- **Customer Insights**: Access customer data for analysis.

---

## **Setup Instructions**

### **Using Conda**

1. **Install Miniconda or Anaconda**:  
   - [Download Miniconda](https://docs.conda.io/en/latest/miniconda.html)  
   - [Download Anaconda](https://www.anaconda.com/products/distribution)

2. **Create a Conda environment**:
   ```bash
   conda create --name capcut-companion python=3.10
   ```

3. **Activate the environment**:
   ```bash
   conda activate capcut-companion
   ```

4. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

5. **Set up the database and run the server**:
   ```bash
   python backend.py
   ```

---

## **API Endpoints**

- **`/chat` (POST)**: Responds to chat queries.
- **`/rag-documents` (GET)**: Fetches help documents.
- **`/survey` (POST)**: Manages survey interactions.
- **`/survey/results` (GET)**: Retrieves survey results.
- **`/customer-insights` (GET)**: Fetches customer data.

---

## **Database Models**

- **HelpDocument**: Stores help documents.
- **SurveyResponse**: Stores survey responses.
- **CustomerInsight**: Stores customer information.

---

## **Survey Flow Logic**

1. **Question**: Did you enjoy using CapCut?  
2. **Question**: How likely are you to recommend us?  
3. **Question**: Which feature did you use most?  
4. **Question**: What should we improve?

---

## **Error Handling**

- Logs errors and returns appropriate status codes.
- Handles missing or invalid input gracefully.

---

## **Contributing**

1. Fork the repository.
2. Create a new branch.
3. Commit changes and push.
4. Open a pull request.

---
