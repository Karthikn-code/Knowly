# Knowly

<p align="center">
  **AI-Powered Document Assistant**
  <br />
  Upload documents, ask questions, and discover information through intelligent conversations.
</p>

<p align="center">
  <a href="https://knowly-ten-amber.vercel.app">Live Demo</a> ·
  <a href="https://github.com/Karthikn-code/Knowly">Source Code</a>
</p>

---

## Overview

Knowly is an AI-powered document assistant that allows users to interact with their documents using natural language.

Powered by **Retrieval-Augmented Generation (RAG)**, Knowly processes uploaded documents, retrieves relevant information through semantic search, and generates context-aware responses using Google Gemini.

The application combines a modern web interface, secure Google authentication, and vector-based document retrieval to make information discovery easier.

## Features

- **Google Authentication:** Secure sign-in using Google OAuth 2.0.
- **Document Upload:** Supports PDF, TXT, DOCX, PPTX, and XLSX files.
- **AI-Powered Q&A:** Ask natural-language questions about uploaded documents.
- **Retrieval-Augmented Generation:** Generate responses using relevant document context.
- **Semantic Search:** Find relevant content using vector similarity and pgvector.
- **Conversation Management:** Create and manage document-related conversations.
- **Private Documents:** User-specific document ownership and access control.
- **Cloud Storage:** Persistent document storage using Tigris.

## Technology Stack

| Component | Technology |
|---|---|
| Frontend | Next.js, React, TypeScript |
| Styling | Tailwind CSS |
| Backend | Python, FastAPI |
| Database | PostgreSQL, SQLAlchemy |
| Vector Search | pgvector |
| AI | Google Gemini |
| Authentication | Google OAuth 2.0 |
| Document Storage | Tigris |
| Deployment | Vercel, Render, Neon |

## Architecture

```text
             USER
              |
              v
       NEXT.JS FRONTEND
           (Vercel)
              |
              v
       NEXT.JS API PROXY
              |
              v
        FASTAPI BACKEND
           (Render)
              |
       +------+------+
       |      |      |
       v      v      v
    GOOGLE  GEMINI  TIGRIS
    OAUTH    API    STORAGE
              |
              v
      DOCUMENT PROCESSING
              |
              v
       TEXT EXTRACTION
              |
              v
        TEXT CHUNKING
              |
              v
       EMBEDDING GENERATION
              |
              v
      POSTGRESQL + PGVECTOR
            (Neon)
              |
              v
        SEMANTIC SEARCH
              |
              v
       CONTEXT RETRIEVAL
              |
              v
        AI RESPONSE
```

## Supported Documents

| Format | Extension |
|---|---|
| PDF | `.pdf` |
| Text | `.txt` |
| Word | `.docx` |
| PowerPoint | `.pptx` |
| Excel | `.xlsx` |

Maximum upload size: **20 MB per document**.

## Getting Started

### Prerequisites

- Python 3.12+
- Node.js and npm
- Docker Desktop
- Google OAuth 2.0 credentials
- Google Gemini API key

### 1. Clone the repository

```bash
git clone https://github.com/Karthikn-code/Knowly.git
cd Knowly
```

### 2. Backend setup

```powershell
cd backend

python -m venv .venv
.\.venv\Scripts\Activate.ps1

pip install -r requirements.txt

Copy-Item .env.example .env
```

Configure the required credentials and database settings in `backend/.env`.

Set the upload limit to 20 MB:

```env
MAX_UPLOAD_SIZE_BYTES=20971520
```

### 3. Start the database

From the `backend` directory:

```powershell
docker compose up -d
alembic upgrade head
```

### 4. Frontend setup

Open another terminal:

```powershell
cd frontend

npm install
```

Create `frontend/.env.local`:

```env
BACKEND_API_URL=http://127.0.0.1:8000
```

### 5. Run the application

Start the backend:

```powershell
cd backend
.\.venv\Scripts\Activate.ps1
python -m uvicorn main:app --reload
```

Start the frontend in another terminal:

```powershell
cd frontend
npm run dev
```

Open **http://localhost:3000** in your browser.

## Testing

Run backend tests:

```powershell
cd backend
pytest
```

## Deployment

Knowly is deployed using:

- **Frontend:** Vercel
- **Backend:** Render
- **Database:** Neon PostgreSQL with pgvector
- **Document Storage:** Tigris

Production deployment requires configuring the appropriate environment variables, Google OAuth redirect URLs, database credentials, and storage credentials.

## Author

**Karthik N**

- GitHub: [Karthikn-code](https://github.com/Karthikn-code)
- Project: [Knowly](https://github.com/Karthikn-code/Knowly)

---

<p align="center">
  Built with Next.js, FastAPI, PostgreSQL, and Google Gemini.
</p>