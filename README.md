# 📘 Interact RAG

A modern **Retrieval-Augmented Generation (RAG)** platform designed for one thing above all: **easy editing of vector store chunks**. Upload PDFs, search semantically, and refine knowledge instantly through a clean web UI.

---

## ✨ Key Features

* **Interactive Editing (Core)**: Search, edit, and update document chunks in real time.
* **Document Ingestion**: Upload PDFs with multiple chunking strategies.
* **Semantic Search**: Query using advanced embedding models.
* **Vector Store Management**: Create, import, and export vector stores.
* **Modern UI + API**: React frontend, FastAPI backend, Docker support.

---

## 🚀 Quick Start

### With Docker 

```bash
git clone https://github.com/BevinV/Interact-Rag.git
cd Interact-RAG
docker compose up
```

### Manual Install (Without Docker)(Recommended)

* **Backend**: `cd backend && pip install -r requirements.txt && uvicorn main:app`
* **Frontend**: `cd frontend && npm install && npm start`

---

## 🎯 Usage

1. **Upload PDFs** → Configure chunking + embedding.
2. **Query Documents** → Semantic search with adjustable results.
3. **Edit Chunks (Core)** → Click *Edit*, update text, save instantly.
4. **Manage Stores** → Import/export vector stores easily.

---

## 📂 Structure

```
interactive-rag-system/
├── backend/     
├── frontend/   
├── storage/     
├── docker-compose.yml
└── README.md
```

---

## ⚙️ Config

* `STORAGE_DIR` (backend)
* `REACT_APP_API_URL` (frontend)

Models: `all-MiniLM-L6-v2` (default), `all-mpnet-base-v2`, `multi-qa-MiniLM-L6-cos-v1`
Chunking: `fixed_size`, `recursive`, `sliding_window`


---
