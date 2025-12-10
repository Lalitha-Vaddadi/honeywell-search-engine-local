# API Documentation

Base URL: `http://localhost:8000/api`

## Authentication

All protected endpoints require a JWT token in the `Authorization` header:
```
Authorization: Bearer <access_token>
```

---

## Auth Endpoints

### POST `/auth/register`

Register a new user account.

**Request Body:**
```json
{
  "email": "user@example.com",
  "password": "securepassword",
  "name": "John Doe"
}
```

**Response (201 Created):**
```json
{
  "success": true,
  "data": {
    "access_token": "eyJhbGciOiJIUzI1...",
    "refresh_token": "eyJhbGciOiJIUzI1...",
    "token_type": "bearer",
    "expires_in": 1800,
    "user": {
      "id": "uuid-string",
      "email": "user@example.com",
      "name": "John Doe",
      "created_at": "2024-01-15T10:30:00Z",
      "last_login": "2024-01-15T10:30:00Z"
    }
  },
  "message": "Registration successful"
}
```

**Errors:**
- `400 Bad Request`: Email already registered

---

### POST `/auth/login`

Authenticate user and get tokens.

**Request Body:**
```json
{
  "email": "user@example.com",
  "password": "securepassword"
}
```

**Response (200 OK):**
```json
{
  "success": true,
  "data": {
    "access_token": "eyJhbGciOiJIUzI1...",
    "refresh_token": "eyJhbGciOiJIUzI1...",
    "token_type": "bearer",
    "expires_in": 1800,
    "user": {
      "id": "uuid-string",
      "email": "user@example.com",
      "name": "John Doe",
      "created_at": "2024-01-15T10:30:00Z",
      "last_login": "2024-01-15T10:30:00Z"
    }
  },
  "message": "Login successful"
}
```

**Errors:**
- `401 Unauthorized`: Invalid email or password

---

### POST `/auth/refresh`

Refresh access token using refresh token.

**Request Body:**
```json
{
  "refresh_token": "eyJhbGciOiJIUzI1..."
}
```

**Response (200 OK):**
```json
{
  "success": true,
  "data": {
    "access_token": "eyJhbGciOiJIUzI1...",
    "refresh_token": "eyJhbGciOiJIUzI1...",
    "token_type": "bearer",
    "expires_in": 1800
  },
  "message": "Token refreshed successfully"
}
```

**Errors:**
- `401 Unauthorized`: Invalid or expired refresh token

---

### POST `/auth/logout`

Logout user (invalidate tokens).

**Headers:**
```
Authorization: Bearer <access_token>
```

**Response (200 OK):**
```json
{
  "success": true,
  "message": "Logout successful"
}
```

---

### GET `/auth/me`

Get current authenticated user's profile.

**Headers:**
```
Authorization: Bearer <access_token>
```

**Response (200 OK):**
```json
{
  "success": true,
  "data": {
    "id": "uuid-string",
    "email": "user@example.com",
    "name": "John Doe",
    "created_at": "2024-01-15T10:30:00Z",
    "last_login": "2024-01-15T10:30:00Z"
  }
}
```

**Errors:**
- `401 Unauthorized`: Invalid or expired token

---

## Error Response Format

All errors follow this format:

```json
{
  "success": false,
  "error": {
    "code": "ERROR_CODE",
    "message": "Human readable error message"
  }
}
```

### Common Error Codes:
- `VALIDATION_ERROR`: Invalid request body or parameters
- `UNAUTHORIZED`: Missing or invalid authentication
- `NOT_FOUND`: Resource not found
- `CONFLICT`: Resource already exists
- `INTERNAL_ERROR`: Server error

---

## Documents Endpoints (Coming Soon)

### POST `/documents/upload`
Upload a PDF document.

### GET `/documents`
List all documents for the authenticated user.

### GET `/documents/{id}`
Get document details.

### DELETE `/documents/{id}`
Delete a document.

---

## Search Endpoints (Coming Soon)

### POST `/search`
Search across all documents.

### GET `/search/{id}/results`
Get search results.

---

## Interactive Documentation

When the backend is running, visit:
- **Swagger UI:** http://localhost:8000/docs
- **ReDoc:** http://localhost:8000/redoc