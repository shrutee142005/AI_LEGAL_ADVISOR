 AI Legal Advisor

An AI-powered legal assistance system designed to help users understand Indian legal documents, constitutional rights, and legal information through Natural Language Processing, RAG (Retrieval-Augmented Generation), and Generative AI.

 Features

-  PDF Upload — Upload legal documents/PDFs for analysis.
-  Document Summarization — Generate simplified summaries of uploaded legal documents.
-  Legal Question Answering — Ask questions related to Indian law and receive AI-generated answers.
-  Legal Document Retrieval — Retrieve relevant information from a legal knowledge base.
- 🇮🇳 Indian Constitution Support — Provides information related to Fundamental Rights and constitutional articles.
-  RAG-based Responses — Combines document retrieval with generative AI for context-aware answers.
-  User Authentication — Secure registration and login using JWT authentication.
-  Vector Database — Stores document embeddings for semantic search.

 Technologies Used

Backend

- Python
- Flask
- REST API
- JWT Authentication

AI / ML

- Generative AI
- RAG (Retrieval-Augmented Generation)
- Text Embeddings
- Natural Language Processing

Database

- PostgreSQL
- Vector Database

Document Processing

- PDF processing
- "pypdf"

Development Tools

- Git
- GitHub
- Postman
- VS Code

 Project Structure

AI_LEGAL_ADVISOR/
│
├── backend/
     |___ app/
     |___legal documents/
     |___ tests/
     |__migrations/
├── frontend/
└── README.md

⚙️ Installation

1. Clone the repository

git clone <https://github.com/shrutee142005/AI_LEGAL_ADVISOR.git>
cd AI_LEGAL_ADVISOR

2. Create a virtual environment

python -m venv venv

3. Activate the virtual environment

Windows PowerShell:

venv\Scripts\Activate.ps1

4. Install dependencies

pip install -r requirements.txt

 Environment Variables

Create a ".env" file and add the required configuration:

GEMINI_API_KEY=your_api_key
DATABASE_URL=your_database_url
JWT_SECRET_KEY=your_secret_key

«Never upload API keys, passwords, or other secrets to GitHub.»

 Running the Project

After activating the virtual environment and configuring the environment variables:

python run.py

The backend server will start locally.

 How It Works

User
  ↓
Upload PDF / Ask Legal Question
  ↓
Document Processing
  ↓
Text Extraction
  ↓
Text Embedding
  ↓
Vector Database
  ↓
Relevant Information Retrieval
  ↓
Generative AI
  ↓
Context-Aware Legal Response

 RAG Pipeline

The system follows a Retrieval-Augmented Generation approach:

1. Legal documents are uploaded and processed.
2. Text is extracted from the documents.
3. Text is converted into embeddings.
4. Embeddings are stored in a vector database.
5. User queries are converted into embeddings.
6. Relevant legal information is retrieved.
7. Retrieved context is provided to the Generative AI model.
8. The system generates a context-aware response.

 Authentication

The application uses JWT-based authentication for protected API endpoints.

Typical flow:

Register
   ↓
Login
   ↓
JWT Token
   ↓
Authenticated API Requests

 API Testing

APIs can be tested using Postman.

Example operations include:

- User Registration
- User Login
- PDF Upload
- Legal Query
- Document Summarization
- Protected API Requests

 Disclaimer

This project is intended for educational and informational purposes only.

The AI-generated responses should not be considered professional legal advice. Users should consult a qualified legal professional for advice regarding specific legal matters.

🔮 Future Improvements

- 🌐 Multilingual legal assistance
- 🎙️ Voice-based legal queries
- 📱 Mobile application
- 📑 Support for additional legal document formats
- ⚡ Improved retrieval accuracy
- 🧑‍⚖️ Lawyer consultation integration
- 📊 Legal case analysis
- 🔍 Advanced semantic legal search

 Author

 Kumbakonam krishna Shree Shrutee Harshita

Artificial intelligence and Data Science / Data & AI Enthusiast

---

 If you find this project useful, consider giving the repository a star!