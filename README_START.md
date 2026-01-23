# Backend Instructions
Since the automated python environment setup failed, please ensure you have Python 3.9+ installed and run:
cd ops_platform/backend
pip install -r requirements.txt
uvicorn app.main:app --reload

# Frontend Instructions
The frontend environment (Node.js) is ready. I am starting the frontend server for you.
cd ops_platform/frontend
npm install
npm run dev
