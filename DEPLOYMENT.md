# 🚀 Railway Deployment Guide

## Prerequisites
- GitHub account
- Railway account (sign up at https://railway.app)
- Your code pushed to GitHub

## Step-by-Step Deployment

### 1. Push Your Code to GitHub

```bash
git add .
git commit -m "Prepare for Railway deployment"
git push origin main
```

### 2. Create Railway Project

1. Go to https://railway.app
2. Click "Start a New Project"
3. Select "Deploy from GitHub repo"
4. Choose your repository
5. Railway will auto-detect your Python app

### 3. Add PostgreSQL Database

1. In your Railway project, click "New"
2. Select "Database" → "PostgreSQL"
3. Railway will create a database and set `DATABASE_URL` automatically

### 4. Configure Environment Variables

In Railway dashboard, go to your service → Variables tab and add:

```
OPENAI_API_KEY=your_openai_key
GOOGLE_API_KEY=your_google_key
GEMINI_API_KEY=your_gemini_key
MODEL=gemini/gemini-2.0-flash-thinking-exp-01-21

LANGSMITH_TRACING=true
LANGSMITH_ENDPOINT=https://api.smith.langchain.com
LANGSMITH_API_KEY=your_langsmith_key
LANGSMITH_PROJECT=Credit Card

# Database variables (Railway auto-sets these from PostgreSQL service)
# DB_HOST, DB_PORT, DB_USER, DB_PASSWORD, DB_NAME
# Or use DATABASE_URL directly
```

### 5. Update Database Connection (Important!)

Railway provides `DATABASE_URL` automatically. Update `app/db/database.py`:

```python
import os
from dotenv import load_dotenv

load_dotenv()

# Railway provides DATABASE_URL, use it if available
DATABASE_URL = os.getenv("DATABASE_URL")

# Fallback to individual variables for local development
if not DATABASE_URL:
    DB_HOST = os.getenv("DB_HOST", "localhost")
    DB_PORT = os.getenv("DB_PORT", "5432")
    DB_USER = os.getenv("DB_USER", "postgres")
    DB_PASSWORD = os.getenv("DB_PASSWORD", "")
    DB_NAME = os.getenv("DB_NAME", "credit_card_ai")
    DATABASE_URL = f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
```

### 6. Deploy!

Railway will automatically:
- Install dependencies from `requirements.txt`
- Run database migrations (if configured)
- Start your FastAPI server
- Provide a public URL (e.g., `your-app.railway.app`)

### 7. Initialize Database

After first deployment, you may need to run migrations:

1. Go to Railway dashboard
2. Click on your service
3. Go to "Settings" → "Deploy"
4. Or use Railway CLI:

```bash
railway run python app/db/init_db.py
```

### 8. Test Your Deployment

```bash
# Health check
curl https://your-app.railway.app/health

# Test signup
curl -X POST https://your-app.railway.app/auth/signup \
  -H "Content-Type: application/json" \
  -d '{"name":"Test User","email":"test@example.com","password":"password123"}'
```

## Railway CLI (Optional)

For easier management, install Railway CLI:

```bash
# Install
npm i -g @railway/cli

# Login
railway login

# Link to project
railway link

# View logs
railway logs

# Run commands in Railway environment
railway run python main.py
```

## Monitoring

- **Logs**: Railway dashboard → Your service → Logs
- **Metrics**: Railway dashboard → Your service → Metrics
- **Health**: Check `/health` endpoint

## Troubleshooting

### Database Connection Issues
- Ensure PostgreSQL service is running
- Check `DATABASE_URL` is set correctly
- Verify database is in same Railway project

### Build Failures
- Check `requirements.txt` is complete
- Verify Python version compatibility
- Check Railway build logs

### Timeout Issues
- Railway has no timeout limits (unlike Vercel)
- Check your LangGraph operations complete
- Monitor memory usage in Metrics

## Cost Estimate

Railway Pricing:
- **Hobby Plan**: $5/month credit (free tier)
- **Usage-based**: ~$0.000463/GB-hour
- **PostgreSQL**: Included in usage

Your app should fit comfortably in the free tier for development/testing.

## Production Checklist

- [ ] Environment variables configured
- [ ] PostgreSQL database connected
- [ ] Database initialized with tables
- [ ] Health endpoint returns 200
- [ ] CORS configured for your frontend
- [ ] API keys secured (not in code)
- [ ] Monitoring/logging enabled
- [ ] Backup strategy for database

## Next Steps

1. Deploy frontend (Vercel/Netlify)
2. Update frontend API URL to Railway URL
3. Set up custom domain (optional)
4. Configure CI/CD for auto-deployments

---

Need help? Check Railway docs: https://docs.railway.app
