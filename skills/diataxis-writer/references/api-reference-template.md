# API Reference

## Base URL

```
https://api.example.com/v1
```

## Authentication

All API requests require an API key in the header:

```http
Authorization: Bearer YOUR_API_KEY
```

## Endpoints

### [Resource Name]

#### List [Resources]

```http
GET /[resources]
```

**Parameters:**

| Name | Type | In | Required | Description |
|------|------|-----|----------|-------------|
| `limit` | integer | query | No | Maximum results (default: 20, max: 100) |
| `offset` | integer | query | No | Number of results to skip |

**Response:**

```json
{
  "data": [
    {
      "id": "string",
      "name": "string",
      "created_at": "2024-01-01T00:00:00Z"
    }
  ],
  "pagination": {
    "total": 100,
    "limit": 20,
    "offset": 0
  }
}
```

#### Get [Resource]

```http
GET /[resources]/{id}
```

**Parameters:**

| Name | Type | In | Required | Description |
|------|------|-----|----------|-------------|
| `id` | string | path | Yes | Resource ID |

**Response:**

```json
{
  "id": "string",
  "name": "string",
  "created_at": "2024-01-01T00:00:00Z"
}
```

#### Create [Resource]

```http
POST /[resources]
```

**Request Body:**

```json
{
  "name": "string",
  "description": "string"
}
```

**Response:** `201 Created`

#### Update [Resource]

```http
PATCH /[resources]/{id}
```

**Request Body:**

```json
{
  "name": "string",
  "description": "string"
}
```

#### Delete [Resource]

```http
DELETE /[resources]/{id}
```

**Response:** `204 No Content`

## Error Responses

| Status | Code | Description |
|--------|------|-------------|
| 400 | `bad_request` | Invalid request parameters |
| 401 | `unauthorized` | Missing or invalid API key |
| 404 | `not_found` | Resource not found |
| 429 | `rate_limited` | Too many requests |
| 500 | `internal_error` | Server error |

**Error Format:**

```json
{
  "error": {
    "code": "string",
    "message": "string",
    "details": {}
  }
}
```

## Rate Limiting

- 1000 requests per hour per API key
- Rate limit headers included in all responses:
  - `X-RateLimit-Limit`
  - `X-RateLimit-Remaining`
  - `X-RateLimit-Reset`
