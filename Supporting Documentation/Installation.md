# INSTALLATION GUIDE

This guide will help you install and run the **Vibe Check** project on your local computer.
Vibe Check is a full-stack application built with:
* React + Vite (Frontend)
* Python Flask (Backend)
* Firebase (Authentication / Database)
* Gemini API (AI Features)

---

# System Requirements
Before starting, make sure you have:
* Node.js (Latest LTS recommended)
* npm (comes with Node.js)
* Python 3.10 or newer
* pip (Python package manager)
* Git

---

# Step 1: Download the Project
## Option A: Clone Repository

```bash
git clone https://github.com/yourusername/vibe-check.git
cd vibe-check
```

## Option B: Download ZIP
1. Open GitHub repository
2. Click **Code**
3. Click **Download ZIP**
4. Extract files
5. Open extracted folder

---

# Step 2: Setup Frontend
Move into frontend folder:

```bash
cd client
```

Install dependencies:
```bash
npm install
```

Start frontend server:
```bash
npm run dev
```

Frontend will run on:
```bash
http://localhost:5173
```

---

# Step 3: Setup Backend
Open a new terminal window.
Move into backend folder:
```bash
cd backend
```

Create virtual environment:
```bash
python -m venv venv
```

Activate virtual environment:
## Windows
```bash
venv\Scripts\activate
```

## Mac / Linux
```bash
source venv/bin/activate
```

Install backend dependencies:
```bash
pip install -r requirements.txt
```

Run Flask server:
```bash
python app.py
```

Backend will run on:
```bash
http://localhost:5000
```

---

# Step 4: Configure Environment Variables
Create a `.env` file in the project root or required folders.
Use values from `.env.example`
Example:
```env
VITE_FIREBASE_API_KEY=your_key
VITE_FIREBASE_AUTH_DOMAIN=your_project.firebaseapp.com
VITE_FIREBASE_PROJECT_ID=your_project_id

GEMINI_API_KEY=your_key
SECRET_KEY=your_secret_key
```

---

# Step 5: Firebase Setup
1. Go to Firebase Console
2. Create project
3. Enable Authentication
4. Enable Email/Password Sign-in
5. Copy Firebase config keys
6. Paste into `.env`

---

# Step 6: Gemini API Setup
1. Get Gemini API key from Google AI Studio
2. Copy key
3. Paste into `.env`

```env
GEMINI_API_KEY=your_key
```

---

# Running Full Project
Keep both servers running:

## Terminal 1
```bash
cd Emotional Assitant
npm run dev
```

## Terminal 2
```bash
cd backend
python app.py
```

Now open:
```bash
http://localhost:5173
```

---

# Common Problems
## npm not recognized
Install Node.js from official website.

## pip not recognized
Reinstall Python and enable PATH option.

## Firebase errors
Check keys in `.env`

## API not responding
Ensure Flask backend is running.

## CORS error
Enable Flask CORS in backend.

---

# Need Help?
If something does not work:
1. Check terminal errors
2. Verify `.env` values
3. Restart both servers

---

# Success 🎉
If everything is configured correctly, Vibe Check will run locally and be ready to use.
