# Quick Start Guide

Get up and running in 5 minutes!

## 1️⃣ Install Dependencies

```bash
cd telegram_listner
pip install -r requirements.txt
```

## 2️⃣ Configure Database

**Option A: Local PostgreSQL**

```bash
# Install PostgreSQL (if not installed)
# Windows: Download from postgresql.org
# Mac: brew install postgresql
# Linux: sudo apt install postgresql

# Create database
createdb pc_deals

# Update .env
DATABASE_URL="postgresql://postgres:password@localhost:5432/pc_deals?schema=public"
```

**Option B: Cloud PostgreSQL (Recommended)**

Use a free tier from:
- [Supabase](https://supabase.com) - Free tier with 500MB
- [Neon](https://neon.tech) - Free tier with 3GB
- [Railway](https://railway.app) - Free tier with 512MB

Copy the connection string to `.env`:
```env
DATABASE_URL="postgresql://user:pass@host:5432/db?schema=public"
```

## 3️⃣ Configure Telegram

1. Go to https://my.telegram.org
2. Login with your phone number
3. Click "API development tools"
4. Create a new application
5. Copy `api_id` and `api_hash` to `.env`:

```env
TELEGRAM_API_ID=12345678
TELEGRAM_API_HASH=abcdef1234567890abcdef1234567890
```

## 4️⃣ Run Setup

```bash
python setup.py
```

This will:
- Generate Prisma client
- Create database tables
- Create necessary directories

## 5️⃣ Start the Server

```bash
python app/main.py
```

Visit http://localhost:8000/docs to see the API!

## 6️⃣ Start Listening

**Option A: Via API**

```bash
curl -X POST http://localhost:8000/api/v1/telegram/start
```

**Option B: Standalone**

```bash
python start_listener.py
```

On first run, you'll be asked to authenticate:
```
Enter phone number: +251912345678
Enter code: 12345
```

## 7️⃣ Test It!

Send a test message to your watched channel, or scrape history:

```bash
curl -X POST http://localhost:8000/api/v1/telegram/scrape \
  -H "Content-Type: application/json" \
  -d '{
    "channel": "@pcagregator",
    "limit": 100,
    "days_back": 30
  }'
```

Check the deals:
```bash
curl http://localhost:8000/api/v1/deals
```

## 🎉 You're Done!

Now you can:
- View deals at `/api/v1/deals`
- Get statistics at `/api/v1/deals/stats`
- Access images at `/images/{filename}`
- Explore the full API at `/docs`

## 🆘 Troubleshooting

**Database connection error?**
```bash
# Test connection
psql $DATABASE_URL -c "SELECT 1"
```

**Telegram authentication error?**
```bash
# Delete session file and try again
rm session_name.session
python start_listener.py
```

**Port already in use?**
```bash
# Change port in .env
PORT=8001
```

**Need help?** Check the full [README.md](README.md)
