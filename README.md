Got it 👍
Here’s the **README.md** with a clear **structure section** included:

---

# Project Setup Guide

This project has two parts: **Frontend (Angular)** and **Backend (FastAPI + Gemini API)**.
Follow the steps below to set up and run both.

---

## 🚀 Frontend Setup (Angular)

1. Navigate to the frontend directory:

   ```bash
   cd frontend
   ```

2. Install dependencies:

   ```bash
   npm install
   ```

3. Start the Angular development server:

   ```bash
   ng serve
   ```

4. Generate a new component (optional):

   ```bash
   ng g c <component-name>
   ```

5. Generate a new service (optional):

   ```bash
   ng g s <service-name>
   ```

---

## ⚡ Backend Setup (FastAPI + Gemini API)

1. Navigate to the backend directory:

   ```bash
   cd backend
   ```

2. Create a `.env` file in the root of the backend folder and add your Gemini API key:

   ```
   GEMINI_API_KEY=your_api_key_here
   ```

3. Create and activate a virtual environment:

   **Windows (PowerShell / CMD):**

   ```bash
   python -m venv venv
   venv\Scripts\activate
   ```

   **Linux/Mac:**

   ```bash
   python3 -m venv venv
   source venv/bin/activate
   ```

4. Install dependencies:

   ```bash
   pip install -r requirements.txt
   ```

5. Start the backend server:

   ```bash
   uvicorn main:app --reload
   ```

---

## 📂 Project Structure

```
project-root/
│
├── frontend/                # Angular frontend
│   ├── src/                 # Source code
│   ├── angular.json         # Angular config file
│   └── package.json         # Frontend dependencies
│
├── backend/                 # FastAPI backend
│   ├── main.py              # Entry point for FastAPI app
│   ├── requirements.txt     # Python dependencies
│   ├── .env                 # Environment variables (ignored in Git)
│   └── venv/                # Virtual environment (ignored in Git)
│
└── README.md                # Setup instructions
```

---

## ✅ Notes

* Keep your `.env` file private. Do **not** push it to GitHub.
* Frontend runs by default on **[http://localhost:4200](http://localhost:4200)**
* Backend runs by default on **[http://127.0.0.1:8000](http://127.0.0.1:8000)**

---