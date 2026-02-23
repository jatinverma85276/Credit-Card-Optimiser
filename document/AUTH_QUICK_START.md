# Authentication Quick Start Guide

## 🚀 Setup (2 minutes)

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Run Migration
```bash
python migrate_add_auth.py
```

### 3. Start Server
```bash
uvicorn main:app --reload
```

## 📝 Complete User Flow

### Step 1: User Signup
```bash
curl -X POST http://localhost:8000/auth/signup \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Jatin Kumar",
    "email": "jatinv85276@gmail.com",
    "password": "MySecurePass123!"
  }'
```

**Response:**
```json
{
  "user_id": "user_1771606239250",
  "name": "Jatin Kumar",
  "email": "jatinv85276@gmail.com",
  "message": "Account created successfully"
}
```

**Save the `user_id` - you'll need it for all future requests!**

---

### Step 2: User Login (Returning Users)
```bash
curl -X POST http://localhost:8000/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "jatinv85276@gmail.com",
    "password": "MySecurePass123!"
  }'
```

**Response:**
```json
{
  "user_id": "user_1771606239250",
  "name": "Jatin Kumar",
  "email": "jatinv85276@gmail.com",
  "message": "Login successful"
}
```

---

### Step 3: Use Chat API
```bash
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{
    "message": "I want to spend 5000 on Amazon",
    "user": {
      "id": "user_1771606239250",
      "name": "Jatin Kumar",
      "email": "jatinv85276@gmail.com"
    }
  }'
```

## 🔐 Security Features

✅ **Bcrypt Password Hashing** - Industry standard encryption  
✅ **Unique Email Validation** - No duplicate accounts  
✅ **Secure Password Storage** - Never stored in plain text  
✅ **Account Status Management** - Enable/disable accounts  

## 💻 Frontend Integration

### React/JavaScript Example

```javascript
// 1. Signup
async function signup(name, email, password) {
  const response = await fetch('http://localhost:8000/auth/signup', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ name, email, password })
  });
  
  if (response.ok) {
    const data = await response.json();
    // Store user data
    localStorage.setItem('user', JSON.stringify(data));
    return data;
  } else {
    const error = await response.json();
    throw new Error(error.detail);
  }
}

// 2. Login
async function login(email, password) {
  const response = await fetch('http://localhost:8000/auth/login', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ email, password })
  });
  
  if (response.ok) {
    const data = await response.json();
    // Store user data
    localStorage.setItem('user', JSON.stringify(data));
    return data;
  } else {
    throw new Error('Invalid credentials');
  }
}

// 3. Use Chat
async function sendMessage(message) {
  const user = JSON.parse(localStorage.getItem('user'));
  
  const response = await fetch('http://localhost:8000/chat', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      message,
      user: {
        id: user.user_id,
        name: user.name,
        email: user.email
      }
    })
  });
  
  return await response.json();
}

// 4. Logout
function logout() {
  localStorage.removeItem('user');
}
```

## 🎯 API Endpoints Summary

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/auth/signup` | POST | Create new account |
| `/auth/login` | POST | Authenticate user |
| `/chat` | POST | Send message (requires user) |
| `/user/{user_id}` | GET | Get user profile |
| `/user/{user_id}/threads` | GET | Get user's threads |
| `/chat/thread/{thread_id}` | DELETE | Delete thread |

## ⚠️ Common Errors

### "Email already registered"
**Cause:** Email is already in use  
**Solution:** Use login instead, or use different email

### "Invalid email or password"
**Cause:** Wrong credentials  
**Solution:** Check email/password spelling

### "422 Unprocessable Entity"
**Cause:** Invalid email format or missing fields  
**Solution:** Ensure all required fields are provided

## 📋 Password Requirements (Recommended)

- Minimum 8 characters
- At least one uppercase letter
- At least one lowercase letter
- At least one number
- At least one special character

## 🧪 Testing

### Test Signup
```bash
curl -X POST http://localhost:8000/auth/signup \
  -H "Content-Type: application/json" \
  -d '{"name":"Test User","email":"test@test.com","password":"Test123!"}'
```

### Test Login
```bash
curl -X POST http://localhost:8000/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"test@test.com","password":"Test123!"}'
```

### Test Wrong Password (Should Fail)
```bash
curl -X POST http://localhost:8000/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"test@test.com","password":"WrongPass"}'
```

## 📚 Full Documentation

For complete details, see:
- **AUTH_DOCUMENTATION.md** - Complete authentication guide
- **API_REFERENCE.md** - All API endpoints
- **USER_SPECIFIC_SYSTEM.md** - System architecture

## ✨ That's It!

You now have a secure authentication system integrated with your credit card optimizer!

### Complete Flow Summary:
1. User signs up → Gets `user_id`
2. User logs in → Gets `user_id` (returning users)
3. User chats → Uses `user_id` for personalization
4. System provides personalized recommendations based on user's cards
