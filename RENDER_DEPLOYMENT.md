# 🚀 Render Deployment Guide

## Why Render?
- Free PostgreSQL database (90 days, then $7/month)
- Free web service tier
- Auto-deploy from GitHub
- Built-in SSL certificates
- Easy environment variable management

## Prerequisites
- GitHub account
- Render account (sign up at https://render.com)
- Your code pushed to GitHub

## Quick Deploy (5 Minutes)

### Step 1: Push Your Code
```bash
git add .
git commit -m "Prepare for Render deployment"
git push origin main
```

### Step 2: Create Render Account
1. Go to https://render.com
2. Sign up with GitHub
3. Authorize Render to access your repositories

### Step 3: Create PostgreSQL Database

1. From Render Dashboard, click "New +"
2. Select "PostgreSQL"
3. Configure:
   - **Name**: `credit-card-db`
   - **Database**: `credit_card_ai`
   - **User**: `credit_card_user`
   - **Region**: Choose closest to you
   - **Plan**: Free (or Starter for production)
4. Click "Create Database"
5. Wait for provisioning (~1 minute)
6. **Save the Internal Database URL** (you'll need this)

### Step 4: Create Web Service

1. Click "New +" → "Web Service"
2. Connect your GitHub repository
3. Configure:
   - **Name**: `credit-card-optimizer`
   - **Region**: Same as database
   - **Branch**: `main`
   - **Root Directory**: Leave blank
   - **Runtime**: Python 3
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `uvicorn main:app --host 0.0.0.0 --port 10000`
4. Select **Free** plan
5. Click "Advanced" to add environment variables

### Step 5: Configure Environment Variables

Add these in the "Environment Variables" section:

**Required:**
```
OPENAI_API_KEY=sk-proj-your-key-here
GOOGLE_API_KEY=AIzaSy-your-key-here
GEMINI_API_KEY=AIzaSy-your-key-here
MODEL=gemini/gemini-2.0-flash-thinking-exp-01-21
```

**Database (from Step 3):**
```
DATABASE_URL=postgresql://user:password@host/dbname
```
Copy the "Internal Database URL" from your PostgreSQL service.

**Optional (LangSmith):**
```
LANGSMITH_TRACING=true
LANGSMITH_ENDPOINT=https://api.smith.langchain.com
LANGSMITH_API_KEY=lsv2_pt_your-key-here
LANGSMITH_PROJECT=Credit Card
```

### Step 6: Deploy!

1. Click "Create Web Service"
2. Render will:
   - Clone your repo
   - Install dependencies
   - Initialize database tables
   - Start your FastAPI server
3. Wait 3-5 minutes for first deploy
4. You'll get a URL like: `https://credit-card-optimizer.onrender.com`

### Step 7: Test Your Deployment

```bash
# Set your Render URL
export API_URL="https://your-app.onrender.com"

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

# Test login
curl -X POST $API_URL/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "password": "password123"
  }'
```

## Alternative: Deploy with render.yaml

If you want infrastructure-as-code:

1. Push the `render.yaml` file to your repo
2. In Render Dashboard, click "New +" → "Blueprint"
3. Connect your repository
4. Render will auto-detect `render.yaml`
5. Add your secret environment variables
6. Click "Apply"

## Important Notes

### Free Tier Limitations
- **Web Service**: 
  - Spins down after 15 minutes of inactivity
  - First request after sleep takes 30-60 seconds (cold start)
  - 750 hours/month free
- **PostgreSQL**: 
  - Free for 90 days
  - Then $7/month for Starter plan
  - 1GB storage, 97 connections

### Cold Starts
Your app will sleep after 15 minutes of inactivity. To keep it awake:

**Option 1: Upgrade to Paid Plan** ($7/month - no sleep)

**Option 2: Use a Ping Service** (Free)
- UptimeRobot: https://uptimerobot.com
- Ping your `/health` endpoint every 10 minutes

**Option 3: Accept Cold Starts**
- First request takes 30-60 seconds
- Subsequent requests are fast

### Database Initialization

The `build.sh` script automatically runs `init_db.py` during deployment.

If you need to manually initialize:
1. Go to your web service → Shell
2. Run: `python app/db/init_db.py`

## Monitoring & Logs

### View Logs
1. Go to your web service in Render Dashboard
2. Click "Logs" tab
3. Real-time logs appear here

### View Metrics
1. Click "Metrics" tab
2. See CPU, Memory, Request stats

### Database Management
1. Go to your PostgreSQL service
2. Click "Connect" → "External Connection"
3. Use these credentials with any PostgreSQL client

## Updating Your App

### Auto-Deploy (Recommended)
1. Push to GitHub: `git push origin main`
2. Render auto-deploys in 2-3 minutes
3. Zero downtime deployment

### Manual Deploy
1. Go to your web service
2. Click "Manual Deploy" → "Deploy latest commit"

## Custom Domain (Optional)

1. Go to your web service → Settings
2. Scroll to "Custom Domain"
3. Add your domain (e.g., `api.yourdomain.com`)
4. Update DNS records as shown
5. Render provides free SSL certificate

## Troubleshooting

### Build Failed
- Check logs in Render Dashboard
- Verify `requirements.txt` is complete
- Ensure Python 3.11 compatibility

### Database Connection Error
- Verify `DATABASE_URL` is set correctly
- Check database is in same region
- Ensure database is running (not suspended)

### Application Crashes
- Check logs for error messages
- Verify all environment variables are set
- Test locally first: `uvicorn main:app --reload`

### Slow First Request (Cold Start)
- This is normal on free tier
- Upgrade to paid plan ($7/month) to eliminate
- Or use ping service to keep alive

## Cost Estimate

**Free Tier (Development):**
- Web Service: Free (with cold starts)
- PostgreSQL: Free for 90 days
- Total: $0/month for 90 days

**Paid (Production):**
- Web Service: $7/month (no cold starts)
- PostgreSQL: $7/month (Starter plan)
- Total: $14/month

## Production Checklist

- [ ] PostgreSQL database created
- [ ] All environment variables set
- [ ] Database initialized with tables
- [ ] Health endpoint returns 200
- [ ] Can create user account
- [ ] Can login and get cards
- [ ] Chat endpoint works
- [ ] Logs show no errors
- [ ] CORS configured for frontend
- [ ] Custom domain added (optional)
- [ ] Monitoring/alerts set up

## Next Steps

1. **Deploy Frontend**
   - Deploy on Vercel/Netlify
   - Update API URL to Render URL
   - Configure CORS in `main.py`

2. **Set Up Monitoring**
   - UptimeRobot for uptime monitoring
   - Sentry for error tracking
   - LogTail for log aggregation

3. **Database Backups**
   - Render auto-backs up daily (paid plans)
   - Export manually: PostgreSQL → Connect → pg_dump

4. **Scale Up**
   - Upgrade to paid plan when ready
   - Add more database storage if needed
   - Enable auto-scaling

## Support

- Render Docs: https://render.com/docs
- Render Community: https://community.render.com
- Status Page: https://status.render.com

---

**Your app will be live at: `https://your-app-name.onrender.com`**

Need help? Check the logs first, then Render docs! 🚀
