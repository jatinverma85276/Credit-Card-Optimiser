# Authentication System Documentation

## Overview

The system now includes a complete authentication system with user signup and login functionality. Passwords are securely hashed using bcrypt.

## Database Schema

### user_auth Table
```sql
CREATE TABLE user_auth (
    id SERIAL PRIMARY KEY,
    user_id VARCHAR UNIQUE NOT NULL,      -- Generated: "user_abc123def456"
    email VARCHAR UNIQUE NOT NULL,         -- User's email (unique)
    name VARCHAR NOT NULL,                 -- User's full name
    hashed_password VARCHAR NOT NULL,      -- Bcrypt hashed password
    is_active BOOLEAN DEFAULT TRUE,        -- Account status
    created_at TIMESTAMP,
    updated_at TIMESTAMP
);
```

## API Endpoints

### 1. Signup (Create Account)

**POST** `/auth/signup`

Create a new user account with hashed password.

**Request Body:**
```json
{
  "name": "Jatin Kumar",
  "email": "jatinv85276@gmail.com",
  "password": "SecurePassword123!"
}
```

**Response (Success - 200):**
```json
{
  "user_id": "user_1771606239250",
  "name": "Jatin Kumar",
  "email": "jatinv85276@gmail.com",
  "message": "Account created successfully"
}
```

**Response (Error - 400):**
```json
{
  "detail": "Email already registered"
}
```

**Example cURL:**
```bash
curl -X POST http://localhost:8000/auth/signup \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Jatin Kumar",
    "email": "jatinv85276@gmail.com",
    "password": "SecurePassword123!"
  }'
```

---

### 2. Login (Authenticate)

**POST** `/auth/login`

Authenticate user with email and password.

**Request Body:**
```json
{
  "email": "jatinv85276@gmail.com",
  "password": "SecurePassword123!"
}
```

**Response (Success - 200):**
```json
{
  "user_id": "user_1771606239250",
  "name": "Jatin Kumar",
  "email": "jatinv85276@gmail.com",
  "message": "Login successful"
}
```

**Response (Error - 401):**
```json
{
  "detail": "Invalid email or password"
}
```

**Example cURL:**
```bash
curl -X POST http://localhost:8000/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "jatinv85276@gmail.com",
    "password": "SecurePassword123!"
  }'
```

---

## Complete User Flow

### Step 1: User Signup
```javascript
// Frontend signup
const signupResponse = await fetch('/auth/signup', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    name: "Jatin Kumar",
    email: "jatinv85276@gmail.com",
    password: "SecurePassword123!"
  })
});

const userData = await signupResponse.json();
// userData.user_id = "user_1771606239250"
// Store user_id in localStorage or session
```

### Step 2: User Login (Returning User)
```javascript
// Frontend login
const loginResponse = await fetch('/auth/login', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    email: "jatinv85276@gmail.com",
    password: "SecurePassword123!"
  })
});

const userData = await loginResponse.json();
// userData.user_id = "user_1771606239250"
// Store user_id in localStorage or session
```

### Step 3: Use Chat API
```javascript
// After login/signup, use the user_id for chat
const chatResponse = await fetch('/chat', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    message: "I'm spending 5000 on Amazon",
    user: {
      id: userData.user_id,
      name: userData.name,
      email: userData.email
    }
  })
});
```

---

## Security Features

### 1. Password Hashing
- Uses **bcrypt** algorithm (industry standard)
- Automatic salt generation
- Configurable work factor for future-proofing
- Passwords are NEVER stored in plain text

### 2. Email Uniqueness
- Email addresses are unique across the system
- Duplicate email registration is prevented
- Case-sensitive email matching

### 3. User ID Generation
- Unique user_id generated on signup
- Format: `user_<16_hex_characters>`
- Example: `user_1771606239250`

### 4. Account Status
- `is_active` flag for account management
- Inactive accounts cannot login
- Allows for account suspension without deletion

---

## Password Requirements

### Recommended (Implement in Frontend)
- Minimum 8 characters
- At least one uppercase letter
- At least one lowercase letter
- At least one number
- At least one special character

### Example Validation (Frontend)
```javascript
function validatePassword(password) {
  const minLength = 8;
  const hasUpper = /[A-Z]/.test(password);
  const hasLower = /[a-z]/.test(password);
  const hasNumber = /\d/.test(password);
  const hasSpecial = /[!@#$%^&*(),.?":{}|<>]/.test(password);
  
  return password.length >= minLength && 
         hasUpper && hasLower && 
         hasNumber && hasSpecial;
}
```

---

## Migration

### Run Migration
```bash
python migrate_add_auth.py
```

**What it does:**
- Creates `user_auth` table
- Creates indexes on `user_id` and `email`
- Sets up constraints for uniqueness

**Expected Output:**
```
✅ Migration completed successfully!
✅ Created user_auth table
✅ Created indexes on user_id and email
```

---

## Error Handling

### Signup Errors

| Error | Status | Description |
|-------|--------|-------------|
| Email already registered | 400 | Email is already in use |
| Invalid email format | 422 | Email format is invalid |
| Missing required fields | 422 | Name, email, or password missing |
| Server error | 500 | Database or server issue |

### Login Errors

| Error | Status | Description |
|-------|--------|-------------|
| Invalid email or password | 401 | Credentials don't match |
| Account inactive | 401 | Account has been deactivated |
| Invalid email format | 422 | Email format is invalid |
| Server error | 500 | Database or server issue |

---

## Testing

### Test Signup
```bash
# Test successful signup
curl -X POST http://localhost:8000/auth/signup \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Test User",
    "email": "test@example.com",
    "password": "TestPass123!"
  }'

# Test duplicate email (should fail)
curl -X POST http://localhost:8000/auth/signup \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Another User",
    "email": "test@example.com",
    "password": "AnotherPass123!"
  }'
```

### Test Login
```bash
# Test successful login
curl -X POST http://localhost:8000/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "password": "TestPass123!"
  }'

# Test wrong password (should fail)
curl -X POST http://localhost:8000/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "password": "WrongPassword"
  }'
```

---

## Integration with Existing System

### Before (No Auth)
```javascript
// Direct chat without authentication
fetch('/chat', {
  body: JSON.stringify({
    message: "...",
    user: { id: "hardcoded_id", name: "...", email: "..." }
  })
});
```

### After (With Auth)
```javascript
// 1. User signs up or logs in
const authResponse = await fetch('/auth/login', { ... });
const { user_id, name, email } = await authResponse.json();

// 2. Store credentials (localStorage, session, etc.)
localStorage.setItem('user', JSON.stringify({ user_id, name, email }));

// 3. Use stored credentials for chat
const user = JSON.parse(localStorage.getItem('user'));
fetch('/chat', {
  body: JSON.stringify({
    message: "...",
    user: { id: user.user_id, name: user.name, email: user.email }
  })
});
```

---

## Best Practices

### Frontend
1. **Store user_id securely** after login/signup
2. **Validate password** before sending to backend
3. **Handle errors gracefully** with user-friendly messages
4. **Clear credentials** on logout
5. **Implement session timeout** for security

### Backend (Already Implemented)
1. ✅ Passwords hashed with bcrypt
2. ✅ Email uniqueness enforced
3. ✅ SQL injection prevention (SQLAlchemy ORM)
4. ✅ Error messages don't leak sensitive info
5. ✅ Account status management

---

## Future Enhancements

Potential improvements:
1. **JWT Tokens** - Add token-based authentication
2. **Password Reset** - Email-based password recovery
3. **Email Verification** - Verify email on signup
4. **OAuth Integration** - Google, Facebook login
5. **2FA** - Two-factor authentication
6. **Rate Limiting** - Prevent brute force attacks
7. **Session Management** - Track active sessions
8. **Password History** - Prevent password reuse

---

## Dependencies

### New Dependencies Added
```
passlib[bcrypt]  # Password hashing
python-multipart # Form data parsing
```

### Install
```bash
pip install -r requirements.txt
```

---

## Database Queries

### Get User by Email
```python
from app.services.auth_service import get_user_by_email

user = get_user_by_email(db, "test@example.com")
```

### Get User by User ID
```python
from app.services.auth_service import get_user_by_user_id

user = get_user_by_user_id(db, "user_1771606239250")
```

### Verify Password
```python
from app.services.auth_service import verify_password

is_valid = verify_password("plain_password", user.hashed_password)
```

---

## Troubleshooting

### Issue: "Email already registered"
**Cause:** Email is already in the database  
**Solution:** Use login instead of signup, or use a different email

### Issue: "Invalid email or password"
**Cause:** Wrong credentials or account inactive  
**Solution:** Check email/password, ensure account is active

### Issue: Migration fails
**Cause:** Table might already exist  
**Solution:** Check if table exists: `\d user_auth` in psql

### Issue: Import error for passlib
**Cause:** Dependencies not installed  
**Solution:** Run `pip install -r requirements.txt`

---

## Complete Example Flow

```bash
# 1. Run migration
python migrate_add_auth.py

# 2. Start server
uvicorn main:app --reload

# 3. Signup
curl -X POST http://localhost:8000/auth/signup \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Jatin Kumar",
    "email": "jatinv85276@gmail.com",
    "password": "SecurePass123!"
  }'

# Response: { "user_id": "user_abc123", "name": "Jatin Kumar", ... }

# 4. Login (later)
curl -X POST http://localhost:8000/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "jatinv85276@gmail.com",
    "password": "SecurePass123!"
  }'

# Response: { "user_id": "user_abc123", "name": "Jatin Kumar", ... }

# 5. Use chat with authenticated user
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{
    "message": "I want to spend 5000 on Amazon",
    "user": {
      "id": "user_abc123",
      "name": "Jatin Kumar",
      "email": "jatinv85276@gmail.com"
    }
  }'
```

---

## Security Checklist

- [x] Passwords hashed with bcrypt
- [x] Email uniqueness enforced
- [x] SQL injection prevention
- [x] Account status management
- [x] Secure password verification
- [ ] JWT tokens (future)
- [ ] Rate limiting (future)
- [ ] Email verification (future)
- [ ] 2FA (future)

---

## Summary

The authentication system provides:
- ✅ Secure user signup with password hashing
- ✅ User login with credential verification
- ✅ Email-based user identification
- ✅ Account status management
- ✅ Integration with existing chat system
- ✅ Complete error handling
- ✅ Production-ready security

Users can now create accounts, login securely, and use the credit card optimization system with their authenticated identity!
