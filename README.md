REMEMBER TO CREATE THE PROJECT OWN PYTHON ENV 


CREATE VIRTUAL ENVIRONMENT FOR TESTING
1. python -m venv venv
-> then run "venv\Scripts\Activate.ps1" (Powershell)
-> or run "venv\Scripts\activate" (CMD)


TO INSTALL DEPENDENCIES
1. cd frontend 
-> then run "npm install"
-> then run "cd .."

2. cd backend
-> then run "pip install -r requirements.txt"
-> then run "cd .."

TO RUN THE PROGRAM 
1. cd frontend
 npm run dev
 -> then run "cd .."

2. cd backend
 uvicorn main:app --reload

3. cd backend 
uvicorn api_dashboard:app --reload --port 8001


