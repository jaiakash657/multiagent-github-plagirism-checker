Multi-Agent GitHub Plagiarism Detection System

A scalable system to detect code plagiarism and similarity across GitHub repositories using a multi-agent architecture.
The system combines lexical, structural, semantic, and contributor-based analysis to generate a final similarity score (in %).

🚀 Features

        Multi-agent plagiarism detection

        Threshold-based agent execution

        Weighted similarity aggregation

        Asynchronous processing with Celery

        Frontend-ready percentage scores

        Scalable and production-friendly architecture

🧠 Similarity Agents

        SimHash – Fast lexical similarity

        Winnowing – Substring fingerprint matching

        AST – Structural similarity

        Semantic – Embedding-based deep similarity

        Contributor – Author and repo metadata comparison

        Fingerprint – Early pruning heuristic

🛠️ Tech Stack

Backend

        Python 3.10+

        FastAPI

        Celery

        Redis

        PostgreSQL

        FAISS

        Tree-sitter

Frontend

        React

        Vite

        Tailwind CSS

📂 Project Structure

        backend/
        ├── app/
        │   ├── main.py
        │   ├── orchestrator/
        │   ├── agents/
        │   ├── core/
        │   └── celery_app.py
        ├── requirements.txt
        └── .env

        frontend/
        ├── src/
        ├── package.json
        └── vite.config.js

⚙️ Setup Instructions (Copy–Paste Friendly)

          1️⃣ Clone the Repository
          git clone <your-repo-url>
          cd <repo-folder>

          🔧 Backend Setup
          2️⃣ Create Virtual Environment
          python -m venv venv


          Activate it:

          Windows

          venv\Scripts\activate


          Linux / Mac

          source venv/bin/activate

          3️⃣ Install Backend Dependencies
          cd backend
          pip install -r requirements.txt

🔴 Start Redis (Required)

Option A: Local Redis
redis-server

Option B: Docker Redis

docker run -p 6379:6379 redis


Keep Redis running in a separate terminal.

🧵 Start Celery Worker

Open a new terminal, activate venv again, then:

cd backend
celery -A app.celery_app worker --loglevel=info

🚀 Start FastAPI Backend (Uvicorn)

Open another terminal, activate venv again, then:

cd backend
uvicorn app.main:app --reload


Backend will be available at:

http://127.0.0.1:8000

🌐 Frontend Setup
4️⃣ Install Frontend Dependencies
cd frontend
npm install

5️⃣ Start Frontend
npm run dev


Frontend will run at:

http://localhost:5173

📡 API Usage
Analyze a GitHub Repository

Endpoint

POST /analyze


Request Body

{
  "repo_url": "https://github.com/user/repository"
}


Sample Response

{
  "final_similarity": 34.4,
  "verdict": "Low Similarity",
  "agent_scores": {
    "simhash": 32.8,
    "winnowing": 34.7,
    "semantic": 36.3,
    "contributor": 40.0
  }
}

📊 Similarity Verdicts
Score Range	Verdict
0–30%	Very Low Similarity
30–60%	Moderate Similarity
60%+	High Similarity
🧪 Use Cases

Academic plagiarism detection

Assignment similarity checking

Recruitment coding assignment screening

Open-source code comparison

🔮 Future Enhancements

Persistent similarity database

Cross-language plagiarism detection

Visualization dashboards

GitHub Actions integration

Continuous learning from new repos

👨‍💻 Author

Jai Akash
B.Tech CSE | Full Stack & AI Developer
Focused on scalable systems, AI, and cloud-native architectures.