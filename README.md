# 📊 Financial Document RAG System (FastAPI + PostgreSQL + FAISS)

A backend system for managing financial documents with **Role-Based Access Control (RBAC)** and a **Retrieval-Augmented Generation (RAG)** pipeline using FAISS for semantic search.

---

## 🚀 Features

### 🔐 Authentication & Authorization
- User registration & login (JWT-based)
- Role-Based Access Control (RBAC)
- Roles: Admin, Financial Analyst, Auditor, Client

### 📄 Document Management
- Upload financial documents (PDF)
- Store metadata (title, company, type)
- View, search, and delete documents
- Metadata-based filtering

### 🧠 RAG (Retrieval-Augmented Generation)
- PDF text extraction
- Chunking + embedding (Sentence Transformers)
- FAISS vector database
- Per-document indexing
- Global semantic search across all documents

---

## 🏗️ Tech Stack

- **Backend:** FastAPI
- **Database:** PostgreSQL
- **ORM:** SQLAlchemy
- **Auth:** JWT (python-jose)
- **Vector DB:** FAISS
- **Embeddings:** SentenceTransformers (MiniLM)
- **PDF Processing:** PyPDF

---

## 📁 Project Structure

```
project/
│
├── main.py              # FastAPI app entry point; defines all API endpoints (auth, documents, RAG)
├── models.py            # SQLAlchemy models (database tables: users, roles, documents)
├── database.py          # Database connection setup and session management (PostgreSQL)
├── auth.py              # JWT authentication, token handling, and role-based access control (RBAC)
├── rag.py               # RAG pipeline: chunking, embeddings, FAISS indexing, semantic search
├── schemas.py           # Pydantic schemas for request/response validation
├── pdf_utils.py         # Utility functions for extracting text from PDF files
├── .env                 # Environment variables (DB URL, secret key)
├── uploads/             # Stores uploaded PDF documents
└── faiss_indexes/       # Stores FAISS vector indexes (one per document)

```
---

## 🔄 API Workflow
- Register → /auth/register
- Login → /auth/login
- Authorize (Bearer token in Swagger)
- Create roles → /roles/create
- Assign roles → /users/assign-role
- Upload document → /documents/upload
- Index document → /rag/index-document
- Search → /rag/search

---

