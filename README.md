# Multi-Agent GitHub Plagiarism Checker

A powerful, multi-agent system designed to detect plagiarism and similarity across GitHub repositories. This application leverages a microservices-like architecture with specialized agents to analyze codebases using various techniques, including lexical analysis, semantic search, and structural fingerprinting.

## 🚀 Features

- **Multi-Agent Architecture**: Uses specialized agents for different types of similarity detection.
- **Deep Analysis**:
  - **Lexical Analysis**: Checks for text-based similarity.
  - **Semantic Analysis**: Uses embeddings (Sentence Transformers) to understand code logic and meaning.
  - **Structural Analysis**: Compares code structure and ASTs.
  - **Fingerprinting**: Uses Winnowing and SimHash algorithms for robust matching.
  - **Contributor Analysis**: Analyzes commit patterns and contributor history.
- **Asynchronous Processing**: Powered by Celery and Redis for handling large codebases efficiently.
- **Modern Frontend**: Built with React and Vite for a fast and responsive user interface.

## 🏗 System Architecture

The project consists of three main components:

1.  **Backend API (FastAPI)**: Handles user requests, manages the analysis pipeline, and aggregates results.
2.  **Worker Nodes (Celery)**: Executes the heavy-lifting analysis tasks distributed across multiple agents.
3.  **Frontend (React + Vite)**: Provides a user-friendly interface to submit repositories and view detailed reports.

### Agents
- `lexical_agent.py`: Performs text-based comparison.
- `semantic_agent.py`: Uses vector embeddings for semantic similarity.
- `structural_agent.py`: Analyzes the structural integrity and patterns of the code.
- `fingerprint_agent.py` / `winnowing_agent.py`: Implements fingerprinting algorithms for exact and near-duplicate detection.
- `simhash_agent.py`: Uses SimHash for locality-sensitive hashing.
- `contributor_agent.py`: Checks for contributor overlap and patterns.

## 🛠 Tech Stack

- **Backend**: Python, FastAPI, SQLAlchemy, Pydantic
- **ML & NLP**: Sentence Transformers, FAISS, Scikit-learn
- **Task Queue**: Celery
- **Message Broker**: Redis
- **Frontend**: React, Vite, Axios
- **Database**: PostgreSQL (via SQLAlchemy)

## 📋 Prerequisites

Before running the project, ensure you have the following installed:

- **Python** (3.9+)
- **Node.js** (16+) & **npm**
- **Redis Server** (Must be running for Celery to work)
- **Git**

## ⚙️ Installation

### 1. Clone the Repository
```bash
git clone <repository-url>
cd multiagent-github-plagirism-checker
```

### 2. Backend Setup
Navigate to the backend directory and set up the virtual environment.

```bash
# Navigate to backend (or root if using shared venv)
cd backend

# Create virtual environment
python -m venv venv

# Activate virtual environment
# Windows:
..\venv\Scripts\activate
# Linux/Mac:
source ../venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### 3. Frontend Setup
Navigate to the frontend directory and install dependencies.

```bash
cd ../frontend
npm install
```

## 🚀 Running the Application

You need to run three separate processes (terminals) to start the full application.

### Terminal 1: Redis Server
Ensure your Redis server is running.
```bash
# Windows (if installed via WSL or Memurai/Redis port)
./redis-server.exe
# Or simply start the service
```

### Terminal 2: Celery Worker
Start the Celery worker to handle background tasks. Make sure you are in the `backend` directory (or root depending on your path) and your virtual environment is activated.

```bash
# From the root directory (assuming venv is active)
cd backend
celery -A workers.celery_app.celery_app worker --pool=solo --loglevel=info
```
*Note: On Windows, `--pool=solo` is often required.*

### Terminal 3: Backend API
Start the FastAPI server.

```bash
# From the backend directory (assuming venv is active)
uvicorn main:app --reload
```
The backend will be available at `http://localhost:8000`.

### Terminal 4: Frontend
Start the React development server.

```bash
cd frontend
npm run dev
```
The frontend will be available at `http://localhost:5173`.

## 📡 API Endpoints

- **`GET /`**: Health check.
- **`GET /api/status`**: Check the status of the analysis service.
- **`POST /api/analysis`**: Submit a repository for plagiarism analysis.

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.
