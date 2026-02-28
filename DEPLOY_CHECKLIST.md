# 🚀 Railway Deployment Checklist

## Before You Deploy

### 1. Commit Your Code
```bash
git add .
git commit -m "Add Railway deployment configuration"
git push origin main
```

### 2. Sign Up for Railway
- Go to https://railway.app
- Sign up with GitHub (easiest)
- Verify your account

## Deployment Steps

### Step 1: Create New Project
1. Click "New Project"
2. Select "Deploy from GitHub repo"
3. Authorize Railway to access your repo
4. Select this repository

### Step 2: Add PostgreSQL Database
1. In your project, click "+ New"
2. Select "Database"
3. Choose "PostgreSQL"
4. Wait for provisioning (~30 seconds)

### Step 3: Configure Environment Variables
Click on your web service → Variables tab → Add these:

**Required:**
```
OPENAI_API_KEY=sk-proj-...
GOOGLE_API_KEY=AIzaSy...
GEMINI_API_KEY=AIzaSy...
```

**Optional (for LangSmith tracking):**
```
LANGSMITH_TRACING=true
LANGSMITH_ENDPOINT=https://api.smith.langchain.com
LANGSMITH_API_KEY=lsv2_pt_...
LANGSMITH_PROJECT=Credit Card
```

**Model Configuration:**
```
MODEL=gemini/gemini-2.0-flash-thinking-exp-01-21
```

**Note:** Railway automatically sets `DATABASE_URL` from your PostgreSQL service!

### Step 4: Connect Database to Web Service
1. Click on your web service
2. Go to "Variables" tab
3. Click "Add Reference"
4. Select your PostgreSQL database
5. Choose `DATABASE_URL`

### Step 5: Deploy
Railway will automatically:
- Detect Python app
- Install dependencies
- Start uvicorn server
- Assign a public URL

### Step 6: Initialize Database Tables
After first deployment, run migrations:

**Option A: Railway Dashboard**
1. Go to your service → Settings
2. Scroll to "Deploy Triggers"
3. Click "Deploy" to redeploy

**Option B: Railway CLI**
```bash
npm i -g @railway/cli
railway login
railway link
railway run python app/db/init_db.py
```

### Step 7: Test Your Deployment
```bash
# Replace with your Railway URL
export API_URL="https://your-app.railway.app"

# Health check
curl $API_URL/health

# Test signup
curl -X POST $API_URL/auth/signup \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Test User",
    "email": "test@example.com",
    "password": "password123"
  }'
```

## Post-Deployment

### ✅ Verify Everything Works
- [ ] `/health` endpoint returns healthy status
- [ ] Database connection successful
- [ ] Can create user account
- [ ] Can login
- [ ] Can add credit card
- [ ] Chat endpoint responds

### 🔒 Security Checklist
- [ ] `.env` file is in `.gitignore`
- [ ] API keys are in Railway variables (not code)
- [ ] Database credentials are secure
- [ ] CORS is configured for your frontend domain

### 📊 Monitor Your App
- **Logs**: Railway Dashboard → Your Service → Logs
- **Metrics**: Railway Dashboard → Your Service → Metrics
- **Database**: Railway Dashboard → PostgreSQL → Metrics

## Common Issues

### Build Failed
- Check `requirements.txt` has all dependencies
- Verify Python version in `runtime.txt`
- Check Railway build logs

### Database Connection Error
- Ensure PostgreSQL service is running
- Verify `DATABASE_URL` is set
- Check database is in same project

### Application Crashes
- Check logs in Railway dashboard
- Verify all environment variables are set
- Ensure database tables are initialized

## Your Railway URLs

After deployment, you'll get:
- **Web Service**: `https://your-app-name.railway.app`
- **PostgreSQL**: Internal URL (auto-configured)

## Cost Monitoring

Railway Pricing:
- **Free Tier**: $5 credit/month
- **Usage**: ~$0.000463/GB-hour
- **Estimate**: Should stay within free tier for development

Check usage: Railway Dashboard → Project → Usage

## Next Steps

1. **Custom Domain** (Optional)
   - Railway Settings → Domains
   - Add your custom domain
   - Update DNS records

2. **CI/CD** (Auto-deploy on push)
   - Already configured!
   - Push to `main` branch = auto-deploy

3. **Frontend Deployment**
   - Deploy frontend on Vercel/Netlify
   - Update API URL to Railway URL
   - Configure CORS in `main.py`

4. **Monitoring**
   - Set up error tracking (Sentry)
   - Configure uptime monitoring
   - Set up alerts

## Support

- Railway Docs: https://docs.railway.app
- Railway Discord: https://discord.gg/railway
- Your deployment guide: `DEPLOYMENT.md`

---

**Ready to deploy? Let's go! 🚀**
