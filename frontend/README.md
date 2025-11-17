To open this repo

Clone this

Backend 

 .\redis-server.exe

celery -A backend.workers.celery_app worker --loglevel=info --pool=solo

uvicorn main:app --reload

Frontend

npm run dev
