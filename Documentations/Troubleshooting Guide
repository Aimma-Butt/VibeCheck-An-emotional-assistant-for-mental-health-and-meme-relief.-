# TROUBLESHOOTING GUIDE 🛠️
This guide helps you fix common issues while running **Vibe Check**.

---

# ❌ Frontend Issues
## 1. npm not recognized

### Problem:
```bash
'npm' is not recognized as an internal or external command
```
### Solution:
* Install Node.js from official website
* Restart your computer
* Verify installation:
```bash
node -v
npm -v
```
---


## 2. node_modules missing
### Problem:
App does not start
### Solution:
```bash
cd client
npm install
```
---


## 3. Port already in use
### Problem:
```bash
Port 5173 is already in use
```
### Solution:
* Close other running apps
* Or run:
```bash
npm run dev -- --port 3000
```
---


# ❌ Backend Issues
## 4. pip not recognized
### Problem:
```bash
'pip' is not recognized
```
### Solution:
* Reinstall Python
* Enable "Add Python to PATH"
---


## 5. Module not found error
### Problem:
```bash
ModuleNotFoundError
```
### Solution:
```bash
pip install -r requirements.txt
```
---


## 6. Flask server not starting
### Solution:
```bash
python app.py
```
Or try:
```bash
flask run
```
---


# 🔐 Firebase Issues
## 7. Firebase authentication not working
### Possible Reasons:
* Wrong API key
* Project not configured
### Solution:
* Check `.env` file
* Verify Firebase console settings
* Enable Email/Password authentication
---


# 🤖 Gemini API Issues
## 8. Invalid API Key
### Problem:
API not responding
### Solution:
* Check GEMINI_API_KEY in `.env`
* Ensure key is active
---


# 🌐 CORS Errors
### Problem:
Frontend cannot connect to backend
### Solution:
Install Flask-CORS:
```bash
pip install flask-cors
```
Add in `app.py`:
```python
from flask_cors import CORS
CORS(app)
```
---


# 🔄 General Fixes
## Restart Everything
```bash
# Stop servers and restart both frontend and backend
```
## Check Logs
Always read error messages in terminal.
---


# ⚠️ Important Tips
* Always run frontend and backend separately
* Never share `.env` file publicly
* Double-check API keys
* Keep dependencies updated
---


# 🆘 Still Not Working?
Try:
1. Reinstall dependencies
2. Restart system
3. Check GitHub issues section
---


# 🎉 You're Good to Go
Most issues can be solved using the steps above.
