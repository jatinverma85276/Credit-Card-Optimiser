#!/bin/bash

# Railway Deployment Test Script
# Usage: ./test_deployment.sh https://your-app.railway.app

if [ -z "$1" ]; then
    echo "❌ Error: Please provide your Railway URL"
    echo "Usage: ./test_deployment.sh https://your-app.railway.app"
    exit 1
fi

API_URL=$1
echo "🧪 Testing deployment at: $API_URL"
echo ""

# Test 1: Health Check
echo "1️⃣ Testing health endpoint..."
HEALTH=$(curl -s -o /dev/null -w "%{http_code}" $API_URL/health)
if [ $HEALTH -eq 200 ]; then
    echo "✅ Health check passed"
else
    echo "❌ Health check failed (HTTP $HEALTH)"
fi
echo ""

# Test 2: Signup
echo "2️⃣ Testing user signup..."
SIGNUP_RESPONSE=$(curl -s -X POST $API_URL/auth/signup \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Test User",
    "email": "test'$(date +%s)'@example.com",
    "password": "password123"
  }')

if echo $SIGNUP_RESPONSE | grep -q "user_id"; then
    echo "✅ Signup successful"
    USER_ID=$(echo $SIGNUP_RESPONSE | grep -o '"user_id":"[^"]*"' | cut -d'"' -f4)
    echo "   User ID: $USER_ID"
else
    echo "❌ Signup failed"
    echo "   Response: $SIGNUP_RESPONSE"
fi
echo ""

# Test 3: Login
echo "3️⃣ Testing user login..."
LOGIN_RESPONSE=$(curl -s -X POST $API_URL/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test'$(date +%s)'@example.com",
    "password": "password123"
  }')

if echo $LOGIN_RESPONSE | grep -q "Invalid email"; then
    echo "✅ Login validation working (expected for new random email)"
else
    echo "⚠️  Login response: $LOGIN_RESPONSE"
fi
echo ""

# Test 4: Get Threads
echo "4️⃣ Testing threads endpoint..."
THREADS=$(curl -s -o /dev/null -w "%{http_code}" $API_URL/chat/threads)
if [ $THREADS -eq 200 ]; then
    echo "✅ Threads endpoint accessible"
else
    echo "❌ Threads endpoint failed (HTTP $THREADS)"
fi
echo ""

# Summary
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "🎉 Deployment test complete!"
echo ""
echo "Next steps:"
echo "1. Test chat endpoint with a real user"
echo "2. Add a credit card"
echo "3. Try expense analysis"
echo "4. Monitor logs in Railway dashboard"
echo ""
echo "Your API is live at: $API_URL"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
