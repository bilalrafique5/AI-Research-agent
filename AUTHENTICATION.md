# Authentication Guide - AI Research Agent

## Setup Instructions

### 1. Install Required Packages
```bash
pip install -r requirements.txt
```

### 2. Configure MongoDB

#### Option A: Local MongoDB
```bash
# Install MongoDB if not already installed
# Start MongoDB service
mongod
```

#### Option B: MongoDB Atlas (Cloud)
1. Create account at https://www.mongodb.com/cloud/atlas
2. Create a free cluster
3. Get your connection string

### 3. Configure Environment Variables

Copy `.env.example` to `.env` and update:

```env
# MongoDB Configuration
MONGODB_URL=mongodb://localhost:27017  # or your MongoDB Atlas URL
DATABASE_NAME=ai_research_agent

# JWT Configuration (change this to a secure random key!)
SECRET_KEY=your-super-secret-key-change-this-12345

# API Keys
GROQ_API_KEY=your_groq_api_key_here
TAVILY_API_KEY=your_tavily_api_key_here
```

## API Endpoints

### Authentication Endpoints

#### 1. **Register New User**
```bash
POST /auth/register
Content-Type: application/json

{
  "username": "john_doe",
  "email": "john@example.com",
  "password": "SecurePassword123",
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

#### 2. **Login**
```bash
POST /auth/login
Content-Type: application/json

{
  "username": "john_doe",
  "password": "SecurePassword123"
}
```

**Response:** Same as register

#### 3. **Get Current User**
```bash
GET /auth/me
Authorization: Bearer <your_access_token>
```

**Response:**
```json
{
  "username": "john_doe",
  "email": "john@example.com",
  "full_name": "John Doe",
  "created_at": "2024-01-01T12:00:00"
}
```

---

### Research Endpoints (Requires Authentication)

#### 1. **Execute Research**
```bash
POST /api/research
Authorization: Bearer <your_access_token>
Content-Type: application/json

{
  "query": "AI agents future trends"
}
```

**Response:**
```json
{
  "status": "success",
  "result": {
    "plan": [...],
    "summary": "...",
    "sources": [
      {
        "title": "Source Title",
        "url": "https://example.com",
        "domain": "example.com",
        "confidence": "95%"
      }
    ],
    "report": "...",
    "evaluation": {
      "clarity_score": 85,
      "accuracy_score": 90,
      "completeness_score": 88,
      "overall_score": 87,
      "passed": true,
      ...
    },
    "pdf_path": "/path/to/reports/research_report_20240101_120000.pdf",
    "message": "Research completed with sources and confidence scores"
  }
}
```

#### 2. **Get Research History**
```bash
GET /api/research-history
Authorization: Bearer <your_access_token>
```

**Response:**
```json
{
  "status": "success",
  "count": 5,
  "history": [
    {
      "_id": "507f1f77bcf86cd799439011",
      "query": "AI agents future trends",
      "created_at": "2024-01-01T12:00:00",
      "result": {
        "overall_score": 87,
        "sources_count": 5,
        "pdf_path": "..."
      }
    }
  ]
}
```

#### 3. **Download PDF Report**
```bash
GET /api/download-report/research_report_20240101_120000.pdf
Authorization: Bearer <your_access_token>
```

Returns the PDF file for download.

---

## Using with cURL or Postman

### Register
```bash
curl -X POST "http://localhost:8000/auth/register" \
  -H "Content-Type: application/json" \
  -d '{
    "username": "john_doe",
    "email": "john@example.com",
    "password": "SecurePassword123",
    "full_name": "John Doe"
  }'
```

### Login
```bash
curl -X POST "http://localhost:8000/auth/login" \
  -H "Content-Type: application/json" \
  -d '{
    "username": "john_doe",
    "password": "SecurePassword123"
  }'
```

### Perform Research (with token)
```bash
curl -X POST "http://localhost:8000/api/research" \
  -H "Authorization: Bearer YOUR_TOKEN_HERE" \
  -H "Content-Type: application/json" \
  -d '{"query": "AI agents future"}'
```

### Get Research History
```bash
curl -X GET "http://localhost:8000/api/research-history" \
  -H "Authorization: Bearer YOUR_TOKEN_HERE"
```

---

## Using with Python

```python
import requests

BASE_URL = "http://localhost:8000"

# Register
register_response = requests.post(f"{BASE_URL}/auth/register", json={
    "username": "john_doe",
    "email": "john@example.com",
    "password": "SecurePassword123",
    "full_name": "John Doe"
})

token = register_response.json()["access_token"]

# Perform research
headers = {"Authorization": f"Bearer {token}"}

research_response = requests.post(
    f"{BASE_URL}/api/research",
    headers=headers,
    json={"query": "AI agents future"}
)

print(research_response.json())

# Get research history
history_response = requests.get(
    f"{BASE_URL}/api/research-history",
    headers=headers
)

print(history_response.json())
```

---

## Token Management

- **Token Type:** JWT (JSON Web Token)
- **Default Expiration:** 30 minutes
- **Header Format:** `Authorization: Bearer <token>`
- **Storage:** Safely store tokens (localStorage in web apps, secure storage on mobile)

### Refreshing Token
Currently, get a new token by logging in again. To implement refresh tokens, add a new endpoint.

---

## Security Notes

1. ⚠️ Change `SECRET_KEY` in `.env` to a secure random string
2. Use HTTPS in production
3. Keep tokens secure, never expose in URLs or logs
4. Use strong passwords (minimum 6 characters recommended: 12+ with special characters)
5. Implement rate limiting for auth endpoints in production
6. MongoDB should be protected with authentication in production

---

## Troubleshooting

### "MongoDB connection failed"
- Ensure MongoDB is running
- Check `MONGODB_URL` in `.env`
- Verify MongoDB credentials if using Atlas

### "Invalid authentication credentials"
- Token may have expired
- Re-login to get a new token
- Check token format in Authorization header

### "Username or email already registered"
- Use a different username/email
- Or login if account already exists

---

## File Structure

```
config/
  database.py          # MongoDB connection
models/
  user.py              # User schemas
utils/
  auth.py              # JWT and password hashing
api/
  auth.py              # Auth endpoints
  dependencies.py      # Auth dependencies
  routes.py            # Research endpoints
```
