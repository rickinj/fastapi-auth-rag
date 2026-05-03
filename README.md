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
├── main.py
├── models.py
├── database.py
├── auth.py
├── rag.py
├── schemas.py
├── pdf_utils.py
├── .env
├── uploads/
└── faiss_indexes/

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

