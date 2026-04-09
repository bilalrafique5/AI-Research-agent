# Security & Authentication Updates

## ✅ Changes Made

### 1. **Password Hashing: Bcrypt → Argon2**
- **Old:** Bcrypt with passlib (had compatibility issues)
- **New:** Argon2-cffi (industry standard, handles longer passwords)
- **Benefits:** 
  - No 72-byte password length limitation
  - Memory-hard algorithm (resistant to GPU attacks)
  - Better security properties
  - No version compatibility issues

### 2. **Endpoint Protection**
All API endpoints now **require Bearer token authentication**:

✅ **Protected Endpoints** (require Bearer token):
- `POST /api/research` - Execute research
- `GET /api/research-history` - Get user's research history  
- `GET /api/download-report/{filename}` - Download PDF

✅ **Public Endpoints** (no auth required):
- `GET /` - Root endpoint (info only)
- `POST /auth/register` - Register new user
- `POST /auth/login` - Login (get token)
- `GET /auth/me` - Get user info (requires Bearer token in header)

---

## 🔐 Authentication Flow

### Step 1: Register
```bash
POST /auth/register
Content-Type: application/json

{
  "username": "john_doe",
  "email": "john@example.com",
  "password": "MySecurePassword123456",  # Can be any length now!
  "full_name": "John Doe"
}
```

**Response:**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "user": {
    "username": "john_doe",
    "email": "john@example.com",
    "full_name": "John Doe",
    "created_at": "2024-01-01T12:00:00"
  }
}
```

### Step 2: Login
```bash
POST /auth/login
Content-Type: application/json

{
  "username": "john_doe",
  "password": "MySecurePassword123456"
}
```

**Response:** Same token as register

### Step 3: Use Token in Protected Endpoints
```bash
POST /api/research
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
Content-Type: application/json

{
  "query": "AI agents future"
}
```

**Requirements:**
- Header: `Authorization: Bearer <token>`
- Token format: Must be `Bearer <token>` (case-insensitive for "Bearer")
- Missing token → 401 Unauthorized
- Invalid token → 401 Unauthorized
- Expired token → 401 Unauthorized

---

## 🛡️ Security Features

1. **Argon2 Password Hashing**
   - Memory-hard algorithm
   - GPU-resistant
   - Industry standard (OWASP recommended)

2. **JWT Token Authentication**
   - 30-minute expiration
   - HS256 algorithm
   - Cryptographically signed

3. **Bearer Token Requirement**
   - All protected endpoints locked
   - Automatic validation
   - Clear error messages

4. **MongoDB User Storage**
   - Hashed passwords only
   - Indexed username & email for uniqueness
   - Audit timestamps (created_at, updated_at)

---

## 📋 Usage Examples

### cURL

**Register:**
```bash
curl -X POST "http://localhost:8000/auth/register" \
  -H "Content-Type: application/json" \
  -d '{
    "username": "john_doe",
    "email": "john@example.com",
    "password": "SecurePassword123!@#",
    "full_name": "John Doe"
  }'
```

**Login:**
```bash
curl -X POST "http://localhost:8000/auth/login" \
  -H "Content-Type: application/json" \
  -d '{
    "username": "john_doe",
    "password": "SecurePassword123!@#"
  }'
```

**Research (Protected):**
```bash
TOKEN="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."

curl -X POST "http://localhost:8000/api/research" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"query": "AI agents"}'
```

---

### Python

```python
import requests

BASE_URL = "http://localhost:8000"

# 1. Register
register_response = requests.post(
    f"{BASE_URL}/auth/register",
    json={
        "username": "john_doe",
        "email": "john@example.com",
        "password": "SecurePassword123!@#",
        "full_name": "John Doe"
    }
)

token = register_response.json()["access_token"]

# 2. Make authenticated request
headers = {"Authorization": f"Bearer {token}"}

research_response = requests.post(
    f"{BASE_URL}/api/research",
    headers=headers,
    json={"query": "AI agents future"}
)

print(research_response.json())
```

---

## ⚠️ Important Notes

1. **Change SECRET_KEY in Production**
   - Update `.env`: `SECRET_KEY=<generate-secure-random-key>`
   - Use: `python -c "import secrets; print(secrets.token_urlsafe(32))"`

2. **Token Expiration**
   - Default: 30 minutes
   - Modify in `utils/auth.py`: `ACCESS_TOKEN_EXPIRE_MINUTES`
   - User must login again when expired

3. **Password Requirements**
   - Minimum 6 characters
   - No maximum length (Argon2 handles it)
   - Recommendation: 12+ characters with mixed case, numbers, symbols

4. **Database**
   - Username & email are unique
   - Passwords are hashed (never stored in plain text)
   - Timestamps track user account creation

---

## 🚀 Ready to Use

Everything is now configured with:
- ✅ Argon2 password hashing (no bcrypt issues)
- ✅ All endpoints properly authenticated
- ✅ Bearer token required for protected endpoints
- ✅ Clean error messages for auth failures

Start your server and create an account!
