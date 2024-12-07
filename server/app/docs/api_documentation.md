# SaaS Platform API Documentation

## Authentication

All API requests require authentication using either JWT tokens or API keys.

### JWT Authentication
```http
Authorization: Bearer <token>
```

### API Key Authentication
```http
X-API-Key: <api_key>
```

## Rate Limiting

Rate limits vary by subscription tier:
- Free: 1,000 requests/day
- Basic: 10,000 requests/day
- Pro: 100,000 requests/day
- Enterprise: Unlimited

## Endpoints

### Authentication

#### Login
```http
POST /api/v1/auth/login
Content-Type: application/json

{
  "email": "user@example.com",
  "password": "password123"
}
```

### Users

#### Create User
```http
POST /api/v1/users
Content-Type: application/json

{
  "email": "user@example.com",
  "password": "password123",
  "full_name": "John Doe"
}
```

### API Keys

#### Generate API Key
```http
POST /api/v1/api-keys
Content-Type: application/json

{
  "name": "Production API Key"
}
```

### Analytics

#### Get Usage Stats
```http
GET /api/v1/analytics/usage?days=30
```

### Subscriptions

#### Create Subscription
```http
POST /api/v1/subscriptions
Content-Type: application/json

{
  "plan": "pro",
  "payment_method_id": "pm_..."
}
```

## Error Codes

- 401: Authentication failed
- 403: Permission denied
- 404: Resource not found
- 422: Validation error
- 429: Rate limit exceeded

## Webhooks

Webhooks are available for:
- Subscription status changes
- Payment failures
- Usage limit warnings

To register a webhook:
```http
POST /api/v1/webhooks
Content-Type: application/json

{
  "url": "https://your-domain.com/webhook",
  "events": ["subscription.updated", "payment.failed"]
}
```