# Knowly

<p align="center">
  <strong>Your Documents. Your Knowledge. One Intelligent Assistant.</strong>
</p>

Knowly is an AI-powered document assistant that helps users organize, search, and understand their documents through intelligent question answering.

It combines document processing, semantic search, vector embeddings, and Retrieval-Augmented Generation (RAG) to generate contextual answers grounded in uploaded documents.

---

## Table of Contents

- [Overview](#overview)
- [Features](#features)
- [Technology Stack](#technology-stack)
- [System Architecture](#system-architecture)
- [Supported File Formats](#supported-file-formats)
- [Project Structure](#project-structure)
- [Getting Started](#getting-started)
- [Environment Configuration](#environment-configuration)
- [Running the Application](#running-the-application)
- [Testing](#testing)
- [Security and Privacy](#security-and-privacy)
- [Deployment](#deployment)
- [Future Scope](#future-scope)

---

## Overview

Traditional document management systems make it difficult to retrieve specific information from large collections of files.

Knowly addresses this problem by allowing users to upload documents and interact with their content using natural language.

The application processes uploaded documents, generates embeddings, stores vector representations in PostgreSQL using pgvector, and retrieves relevant information to provide context-aware AI responses.

Google OAuth 2.0 is used for authentication, and document access is restricted to the respective owners.

## Features

### Authentication and User Management
- Google OAuth 2.0 authentication.
- Secure session-based authentication.
- User identity based on Google's stable account identifier.
- User-specific document access.

### Document Management
- Upload PDF, TXT, DOCX, PPTX, and XLSX files.
- Extract and process document content.
- Split documents into manageable chunks.
- Store document metadata and extracted content.
- Maintain private document storage.

### AI-Powered Intelligence
- Gemini-powered AI responses.
- Document embeddings and vector search.
- Retrieval-Augmented Generation (RAG).
- Context-aware question answering.
- Source citations for generated answers.

### Conversations
- Document-based conversations.
- Conversation management.
- Conversation sharing functionality.
- Contextual retrieval for relevant questions.

### Security
- User-level resource ownership validation.
- CSRF protection.
- Authentication and authorization checks.
- Input validation and upload restrictions.
- Audit logging.

---

## Technology Stack

| Layer | Technologies |
|---|---|
| Frontend | Next.js, React, TypeScript |
| Styling | Tailwind CSS |
| Backend | Python, FastAPI |
| ORM | SQLAlchemy |
| Database Migrations | Alembic |
| Database | PostgreSQL |
| Vector Search | pgvector |
| AI Model | Google Gemini |
| Authentication | Google OAuth 2.0 |
| Document Processing | PyPDF, python-docx, python-pptx, openpyxl |
| Backend Testing | pytest, pytest-asyncio |
| Containerization | Docker |

---

## System Architecture

```text
                   USER
                     |
                     v
             NEXT.JS FRONTEND
                     |
                     v
               FASTAPI BACKEND
                     |
          +----------+-----------+
          |          |           |
          v          v           v
      GOOGLE     DOCUMENT     GEMINI AI
      OAUTH      PROCESSING      API
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
              POSTGRESQL
               + PGVECTOR
                     |
                     v
               SEMANTIC SEARCH
                     |
                     v
              CONTEXT RETRIEVAL
                     |
                     v
              AI RESPONSE
                     |
                     v
                CITATIONS
                     |
                     v
               USER INTERFACE
```

### RAG Workflow

1. The user uploads a document.
2. The backend validates and processes the file.
3. Text is extracted from the document.
4. Extracted text is divided into smaller chunks.
5. Embeddings are generated using the configured Gemini embedding service.
6. Document vectors and associated metadata are stored in PostgreSQL with pgvector.
7. The user's question is converted into a search representation.
8. Relevant document chunks are retrieved using semantic search.
9. Retrieved context is supplied to the Gemini generation model.
10. The generated response and relevant citations are returned to the frontend.

---

## Supported File Formats

| Document Type | Extension |
|---|---|
| PDF | `.pdf` |
| Text | `.txt` |
| Microsoft Word | `.docx` |
| Microsoft PowerPoint | `.pptx` |
| Microsoft Excel | `.xlsx` |

---

## Project Structure

```text
Knowly/
|
|-- backend/
|   |-- app/
|   |   |-- api/
|   |   |-- core/
|   |   |-- db/
|   |   |-- models/
|   |   |-- schemas/
|   |   |-- services/
|   |
|   |-- migrations/
|   |-- scripts/
|   |-- tests/
|   |-- main.py
|   |-- alembic.ini
|   |-- docker-compose.yml
|   |-- requirements.txt
|   |-- pytest.ini
|   |-- .env.example
|
|-- frontend/
|   |-- public/
|   |-- src/
|   |   |-- app/
|   |   |-- components/
|   |   |-- lib/
|   |-- package.json
|   |-- package-lock.json
|
|-- .gitignore
|-- README.md
```

---

## Getting Started

### Prerequisites

Install the following tools:

- Python 3.12
- Node.js and npm
- Docker Desktop
- Git
- Google OAuth 2.0 credentials
- Google Gemini API key

A PostgreSQL database with pgvector support is required.

### 1. Clone the Repository

```bash
git clone https://github.com/Karthikn-code/Knowly.git
cd Knowly
```

### 2. Backend Setup

Navigate to the backend directory:

```bash
cd backend
```

Create a Python virtual environment:

```bash
python -m venv .venv
```

Activate it on Windows PowerShell:

```powershell
.\.venv\Scripts\Activate.ps1
```

Install the dependencies:

```bash
pip install -r requirements.txt
```

Create your environment configuration:

```powershell
Copy-Item .env.example .env
```

Update the `.env` file with your own configuration values.

### 3. Database Setup

The backend includes a Docker Compose configuration for PostgreSQL with pgvector.

From the backend directory, run:

```bash
docker compose up -d
```

Check the database status:

```bash
docker compose ps
```

Apply database migrations:

```bash
alembic upgrade head
```

### 4. Frontend Setup

Open another terminal and navigate to the frontend:

```bash
cd frontend
```

Create the frontend environment file:

```powershell
New-Item -ItemType File -Path .env.local -Force
```

Add the backend API URL to `.env.local`:

```env
NEXT_PUBLIC_API_BASE_URL=http://127.0.0.1:8000
```

Install frontend dependencies:

```bash
npm install
```

---

## Environment Configuration

### Backend

The backend configuration is stored in:

`backend/.env`

Refer to `backend/.env.example` for the required configuration variables.

Important configuration categories include:

- Application settings.
- Gemini API credentials.
- Google OAuth client credentials.
- OAuth callback URL.
- Session and CSRF secrets.
- PostgreSQL connection settings.
- Frontend application URL.
- Private document storage configuration.

Never commit actual environment files or credentials.

### Frontend

The frontend configuration is stored in:

`frontend/.env.local`

Required variable:

| Variable | Purpose |
|---|---|
| `NEXT_PUBLIC_API_BASE_URL` | Backend API base URL |

Use the appropriate backend URL for your deployment environment.

---

## Running the Application

### Start the Backend

From the backend directory, activate the virtual environment and run:

```bash
python -m uvicorn main:app --reload
```

Backend:

`http://127.0.0.1:8000`

### Start the Frontend

From the frontend directory:

```bash
npm run dev
```

Frontend:

`http://localhost:3000`

The frontend communicates with the FastAPI backend through the configured API base URL.

---

## Testing

The backend includes automated tests covering application functionality and important integration scenarios.

Run the test suite from the backend directory:

```bash
pytest
```

Run with verbose output:

```bash
pytest -v
```

Some standalone scripts in the backend root are intended for specific development and database integration checks. They may require existing test records and configured external services.

---

## Security and Privacy

Knowly is designed with user-specific document access and secure authentication in mind.

Important security considerations:

- Google OAuth 2.0 authentication.
- Stable Google user identity.
- Owner-based document authorization.
- CSRF protection.
- Secure session configuration.
- File validation and upload size restrictions.
- Private document storage.
- Database-backed user and document records.
- Audit logging.

Users must configure their own credentials and production secrets.

Never publish:

- `.env` files.
- OAuth client secrets.
- Gemini API keys.
- Database passwords.
- Session or CSRF signing secrets.
- Private uploaded documents.

---

## Deployment

The intended production architecture separates the frontend, backend, and database.

| Component | Planned Platform |
|---|---|
| Frontend | Vercel |
| Backend | Render |
| Database | Managed PostgreSQL with pgvector |
| AI Services | Google Gemini API |
| Authentication | Google OAuth 2.0 |

Production deployment requires:

- Production environment variables.
- Managed PostgreSQL with pgvector enabled.
- Correct Google OAuth authorized origins and redirect URLs.
- Secure production cookie and CSRF settings.
- Persistent private document storage.
- Production CORS configuration.
- Deployment health checks and application testing.

Deployment configuration should be completed and verified separately for each environment.

---

## Future Scope

Potential areas for future development include:

- Additional document formats.
- Improved document organization.
- Advanced retrieval and ranking strategies.
- More AI-powered document workflows.
- Enhanced document analytics.
- Improved scalability and observability.

---

## Author

**Karthik N**

GitHub: [Karthikn-code](https://github.com/Karthikn-code)

Project Repository: [Knowly](https://github.com/Karthikn-code/Knowly)

---

<p align="center">
  <strong>Knowly — Your Documents. Your Knowledge. One Intelligent Assistant.</strong>
</p>
