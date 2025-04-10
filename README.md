

# **CapCut Companion Backend**

The **CapCut Companion Backend** is a Flask-based application that powers the CapCut AI Assistant. It provides APIs for chatbot interactions, survey handling, RAG (Retrieval-Augmented Generation) document management, and customer insights. This backend is designed to enhance user experience by integrating AI-driven features for video editing.

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
## **Setup Instructions**

### **Prerequisites**
1. Python 3.10+
2. Flask
3. SQLite database
4. Google Generative AI API key

### **Installation**
1. Clone the repository:
   ```bash
   git clone https://github.com/your-repo/capcut-companion-backend.git
   cd capcut-companion-backend
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Set up the database:
   ```bash
   python backend.py
   ```

4. Run the server:
   ```bash
   python backend.py
   ```

---

## **Survey Flow Logic**

The survey flow dynamically adjusts based on user responses:

1. Question: 📝 Did you enjoy using CapCut today?  
   - Choices: 👍 or 👎  
   - Next Step: Recommendation

2. Question: 📝 How likely are you to recommend us to a friend?  
   - Choices: Likely, Unlikely, Neutral  
   - Next Step: Feature Usage

3. Question: 📝 Which feature did you use most?  
   - Choices: Trimming, Effects, Text, Transitions  
   - Next Step: Improvement

4. Question: 📝 What would you like us to focus on improving?  
   - Choices: Ease of Use, Performance, Templates, Tutorials  
   - Next Step: End

---

## **Error Handling**

- Logs errors using Python's `logging` module.
- Returns appropriate status codes (`400`, `500`) with error messages.
- Handles missing or invalid input gracefully.

---

## **Contributing**

We welcome contributions! To contribute:

1. Fork this repository.
2. Create a new branch (`feature/my-feature`).
3. Commit your changes (`git commit -m 'Add my feature'`).
4. Push to the branch (`git push origin feature/my-feature`).
5. Open a pull request.

---
