# API Documentation

Complete reference for the PC Deal Aggregator API.

**Base URL**: `http://localhost:8000`

**Interactive Docs**: `http://localhost:8000/docs`

---

## 📋 Table of Contents

- [Authentication](#authentication)
- [Health Endpoints](#health-endpoints)
- [Deal Endpoints](#deal-endpoints)
- [Telegram Endpoints](#telegram-endpoints)
- [Response Formats](#response-formats)
- [Error Handling](#error-handling)
- [Rate Limiting](#rate-limiting)

---

## 🔐 Authentication

Currently, the API is **open** (no authentication required).

For production, consider adding:
- JWT tokens
- API keys
- OAuth2

---

## ❤️ Health Endpoints

### GET /health

Basic health check.

**Response**:
```json
{
  "status": "healthy",
  "app": "PC Deal Aggregator",
  "version": "2.0.0"
}
```

### GET /health/db

Check database connection.

**Response**:
```json
{
  "status": "healthy",
  "database": "connected",
  "deals_count": 150
}
```

### GET /health/telegram

Check Telegram service status.

**Response**:
```json
{
  "status": "healthy",
  "telegram": "connected",
  "watched_channels": ["@pcagregator"]
}
```

---

## 💼 Deal Endpoints

### GET /api/v1/deals

Get paginated list of deals with filtering.

**Query Parameters**:

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `page` | integer | 1 | Page number (≥1) |
| `page_size` | integer | 50 | Items per page (1-100) |
| `sort_by` | string | createdAt | Field to sort by |
| `sort_order` | string | desc | Sort order (asc/desc) |
| `min_price` | integer | - | Minimum price filter |
| `max_price` | integer | - | Maximum price filter |
| `categories` | string | - | Comma-separated categories |
| `processor` | string | - | Processor filter (contains) |
| `graphics_card` | string | - | Graphics card filter (contains) |
| `condition` | string | - | Condition filter (contains) |
| `min_score` | integer | - | Minimum general score |
| `search` | string | - | Search in title/model/message |

**Example Request**:
```bash
GET /api/v1/deals?page=1&page_size=20&categories=Gaming&min_price=100000&max_price=200000&sort_by=generalScore&sort_order=desc
```

**Response**:
```json
{
  "deals": [
    {
      "id": "clx123abc",
      "createdAt": "2025-05-25T10:30:00Z",
      "updatedAt": "2025-05-25T10:30:00Z",
      "title": "HP Omen i7",
      "model": "Omen",
      "processor": "Intel Core i7",
      "generation": "13th Gen",
      "ram": "32GB DDR5",
      "storage": "1TB SSD",
      "screenSize": "16 inch",
      "resolution": "2K (2560x1440)",
      "graphicsCard": "NVIDIA GeForce RTX 4060",
      "graphicsMemory": "8GB GDDR6",
      "batteryLife": "10 hours",
      "condition": "Brand New",
      "price": 195000,
      "currency": "Birr",
      "contactNumbers": ["0913066711"],
      "urls": ["https://t.me/channel/123"],
      "categories": ["Gaming", "Premium", "HP"],
      "generalScore": 12,
      "categoryScores": {"Gaming": 5},
      "imagePath": "downloaded_images/123.jpg",
      "channelId": "1234567890",
      "messageId": "123",
      "telegramUrl": "https://t.me/pcagregator/123",
      "rawMessage": "..."
    }
  ],
  "total": 150,
  "page": 1,
  "pageSize": 20,
  "totalPages": 8
}
```

---

### GET /api/v1/deals/stats

Get statistics about deals.

**Query Parameters**: Same filters as `/deals` endpoint

**Example Request**:
```bash
GET /api/v1/deals/stats?categories=Gaming
```

**Response**:
```json
{
  "totalDeals": 45,
  "avgPrice": 175000,
  "minPrice": 85000,
  "maxPrice": 350000,
  "categoriesCount": {
    "Gaming": 45,
    "Premium": 30,
    "HP": 15
  },
  "brandsCount": {
    "HP": 15,
    "Dell": 12,
    "Lenovo": 10,
    "MSI": 8
  }
}
```

---

### GET /api/v1/deals/{deal_id}

Get a specific deal by ID.

**Path Parameters**:
- `deal_id` (string, required): Deal ID

**Example Request**:
```bash
GET /api/v1/deals/clx123abc
```

**Response**: Single deal object (same structure as in list)

**Error Response** (404):
```json
{
  "detail": "Deal not found"
}
```

---

### DELETE /api/v1/deals/{deal_id}

Delete a deal by ID.

**Path Parameters**:
- `deal_id` (string, required): Deal ID

**Example Request**:
```bash
DELETE /api/v1/deals/clx123abc
```

**Response**:
```json
{
  "message": "Deal deleted successfully",
  "id": "clx123abc"
}
```

**Error Response** (404):
```json
{
  "detail": "Deal not found"
}
```

---

### GET /api/v1/deals/categories/list

Get list of all unique categories.

**Response**:
```json
{
  "categories": [
    "Budget",
    "Gaming",
    "Graphic Design",
    "HP",
    "Lenovo",
    "Mid-range",
    "Premium",
    "Programming",
    "Workstation"
  ]
}
```

---

### GET /api/v1/deals/brands/list

Get list of all unique brands.

**Response**:
```json
{
  "brands": [
    "Acer",
    "Dell",
    "HP",
    "Lenovo",
    "MSI"
  ]
}
```

---

## 📡 Telegram Endpoints

### POST /api/v1/telegram/start

Start the Telegram listener service.

**Response**:
```json
{
  "message": "Telegram service starting...",
  "status": "starting"
}
```

Or if already running:
```json
{
  "message": "Telegram service is already running",
  "status": "running"
}
```

---

### POST /api/v1/telegram/stop

Stop the Telegram listener service.

**Response**:
```json
{
  "message": "Telegram service stopped",
  "status": "stopped"
}
```

---

### GET /api/v1/telegram/status

Get Telegram service status.

**Response**:
```json
{
  "status": "running",
  "is_connected": true
}
```

---

### POST /api/v1/telegram/scrape

Scrape historical messages from a channel.

**Request Body**:
```json
{
  "channel": "@pcagregator",
  "limit": 1000,
  "days_back": 180
}
```

**Fields**:
- `channel` (string, required): Channel username or ID
- `limit` (integer, default: 100): Maximum messages to scrape
- `days_back` (integer, optional): How many days back to scrape

**Response**:
```json
{
  "message": "Started scraping @pcagregator",
  "channel": "@pcagregator",
  "limit": 1000,
  "days_back": 180,
  "status": "scraping"
}
```

**Note**: This runs in the background. Check logs for progress.

---

## 📦 Response Formats

### Deal Object

```typescript
{
  id: string;
  createdAt: string;  // ISO 8601
  updatedAt: string;  // ISO 8601
  title: string | null;
  model: string | null;
  processor: string | null;
  generation: string | null;
  ram: string | null;
  storage: string | null;
  screenSize: string | null;
  resolution: string | null;
  graphicsCard: string | null;
  graphicsMemory: string | null;
  batteryLife: string | null;
  condition: string | null;
  price: number | null;
  currency: string | null;
  contactNumbers: string[];
  urls: string[];
  categories: string[];
  generalScore: number;
  categoryScores: { [key: string]: number };
  imagePath: string | null;
  channelId: string | null;
  messageId: string | null;
  telegramUrl: string | null;
  rawMessage: string;
}
```

### Paginated Response

```typescript
{
  deals: Deal[];
  total: number;
  page: number;
  pageSize: number;
  totalPages: number;
}
```

### Statistics Response

```typescript
{
  totalDeals: number;
  avgPrice: number | null;
  minPrice: number | null;
  maxPrice: number | null;
  categoriesCount: { [category: string]: number };
  brandsCount: { [brand: string]: number };
}
```

---

## ⚠️ Error Handling

### Error Response Format

```json
{
  "detail": "Error message here"
}
```

### HTTP Status Codes

| Code | Meaning |
|------|---------|
| 200 | Success |
| 201 | Created |
| 400 | Bad Request (invalid parameters) |
| 404 | Not Found |
| 422 | Validation Error |
| 500 | Internal Server Error |

### Validation Error Example

```json
{
  "detail": [
    {
      "loc": ["query", "page"],
      "msg": "ensure this value is greater than or equal to 1",
      "type": "value_error.number.not_ge"
    }
  ]
}
```

---

## 🚦 Rate Limiting

Currently **no rate limiting** is implemented.

For production, consider:
- 100 requests/minute per IP
- 1000 requests/hour per IP
- Use libraries like `slowapi`

---

## 📊 Usage Examples

### Get Latest Gaming Laptops

```bash
curl "http://localhost:8000/api/v1/deals?categories=Gaming&sort_by=createdAt&sort_order=desc&page_size=10"
```

### Search for HP Laptops

```bash
curl "http://localhost:8000/api/v1/deals?search=HP"
```

### Get Budget Laptops Under 100k

```bash
curl "http://localhost:8000/api/v1/deals?categories=Budget&max_price=100000"
```

### Get High-Performance Laptops

```bash
curl "http://localhost:8000/api/v1/deals?min_score=10&graphics_card=RTX"
```

### Get Price Statistics

```bash
curl "http://localhost:8000/api/v1/deals/stats"
```

### Start Scraping

```bash
curl -X POST http://localhost:8000/api/v1/telegram/scrape \
  -H "Content-Type: application/json" \
  -d '{
    "channel": "@pcagregator",
    "limit": 5000,
    "days_back": 180
  }'
```

---

## 🔧 Advanced Filtering

### Multiple Categories

```bash
# Deals that are both Gaming AND Premium
curl "http://localhost:8000/api/v1/deals?categories=Gaming,Premium"
```

### Price Range

```bash
# Deals between 100k and 200k
curl "http://localhost:8000/api/v1/deals?min_price=100000&max_price=200000"
```

### Processor Filter

```bash
# All i7 laptops
curl "http://localhost:8000/api/v1/deals?processor=i7"

# All Ryzen laptops
curl "http://localhost:8000/api/v1/deals?processor=Ryzen"
```

### Graphics Card Filter

```bash
# All RTX laptops
curl "http://localhost:8000/api/v1/deals?graphics_card=RTX"

# Specific model
curl "http://localhost:8000/api/v1/deals?graphics_card=RTX%204060"
```

### Combined Filters

```bash
# Gaming laptops with i7, RTX, under 200k, sorted by score
curl "http://localhost:8000/api/v1/deals?categories=Gaming&processor=i7&graphics_card=RTX&max_price=200000&sort_by=generalScore&sort_order=desc"
```

---

## 📱 Client Libraries

### Python

```python
import requests

# Get deals
response = requests.get("http://localhost:8000/api/v1/deals", params={
    "categories": "Gaming",
    "min_price": 100000,
    "page_size": 20
})
deals = response.json()

# Get specific deal
deal = requests.get(f"http://localhost:8000/api/v1/deals/{deal_id}").json()

# Start scraping
requests.post("http://localhost:8000/api/v1/telegram/scrape", json={
    "channel": "@pcagregator",
    "limit": 1000,
    "days_back": 180
})
```

### JavaScript

```javascript
// Get deals
const response = await fetch('http://localhost:8000/api/v1/deals?categories=Gaming');
const data = await response.json();

// Get specific deal
const deal = await fetch(`http://localhost:8000/api/v1/deals/${dealId}`).then(r => r.json());

// Start scraping
await fetch('http://localhost:8000/api/v1/telegram/scrape', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    channel: '@pcagregator',
    limit: 1000,
    days_back: 180
  })
});
```

---

## 🔗 Related Documentation

- [README.md](README.md) - Full project documentation
- [QUICKSTART.md](QUICKSTART.md) - Get started in 5 minutes
- [MIGRATION_GUIDE.md](MIGRATION_GUIDE.md) - Migrate from old system

---

**For interactive API exploration, visit `/docs` when the server is running!**
