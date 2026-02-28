# 🚀 Quick Deploy to Render

## 3-Step Deployment

### 1. Push to GitHub
```bash
git add .
git commit -m "Deploy to Render"
git push origin main
```

### 2. Create on Render

**A. Create PostgreSQL Database:**
1. Go to https://render.com/dashboard
2. Click "New +" → "PostgreSQL"
3. Name: `credit-card-db`
4. Plan: Free
5. Click "Create Database"
6. Copy the "Internal Database URL"

**B. Create Web Service:**
1. Click "New +" → "Web Service"
2. Connect your GitHub repo
3. Settings:
   - **Name**: `credit-card-optimizer`
   - **Build Command**: `./build.sh`
   - **Start Command**: `uvicorn main:app --host 0.0.0.0 --port 10000`
4. Add Environment Variables:
   ```
   DATABASE_URL=<paste-internal-database-url>
   OPENAI_API_KEY=<your-key>
   GOOGLE_API_KEY=<your-key>
   GEMINI_API_KEY=<your-key>
   MODEL=gemini/gemini-2.0-flash-thinking-exp-01-21
   ```
5. Click "Create Web Service"

### 3. Test
```bash
curl https://your-app.onrender.com/health
```

## Done! 🎉

Your API is live at: `https://your-app-name.onrender.com`

**Note:** Free tier sleeps after 15 min inactivity. First request takes 30-60s.

Full guide: See `RENDER_DEPLOYMENT.md`
