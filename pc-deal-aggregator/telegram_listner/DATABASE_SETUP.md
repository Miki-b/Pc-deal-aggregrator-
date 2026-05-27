# Database Setup Guide

You have several options for setting up PostgreSQL for this project.

---

## ✅ Current Status

You have a Prisma Postgres connection string, but it's not connecting. This could be due to:
- Database not fully provisioned yet
- Network/firewall issues
- Connection string needs activation

---

## 🎯 Option 1: Prisma Postgres (What you have)

### Check Status

1. Go to https://console.prisma.io
2. Check if your database is "Active"
3. If it's "Provisioning", wait a few minutes

### Test Connection

```bash
python test_db_connection.py
```

### If it works, push schema:

```bash
prisma db push
```

---

## 🚀 Option 2: Supabase (Recommended - Free & Easy)

### Steps:

1. **Sign up**: https://supabase.com
2. **Create project**: Click "New Project"
3. **Get connection string**:
   - Go to Project Settings → Database
   - Copy "Connection string" (URI mode)
   - It looks like: `postgresql://postgres:[YOUR-PASSWORD]@db.xxx.supabase.co:5432/postgres`

4. **Update .env**:
```env
DATABASE_URL=postgresql://postgres:your_password@db.xxx.supabase.co:5432/postgres
```

5. **Push schema**:
```bash
prisma db push
```

### Advantages:
- ✅ Free tier (500MB)
- ✅ Instant setup
- ✅ Web dashboard
- ✅ Reliable

---

## 💻 Option 3: Local PostgreSQL

### Windows Installation:

1. **Download**: https://www.postgresql.org/download/windows/
2. **Install**: Run installer, remember your password
3. **Create database**:
```bash
# Open Command Prompt
psql -U postgres
CREATE DATABASE pc_deals;
\q
```

4. **Update .env**:
```env
DATABASE_URL=postgresql://postgres:your_password@localhost:5432/pc_deals
```

5. **Push schema**:
```bash
prisma db push
```

### Advantages:
- ✅ Full control
- ✅ No internet needed
- ✅ Fast
- ✅ Free

### Disadvantages:
- ❌ Manual setup
- ❌ Need to manage backups
- ❌ Only accessible locally

---

## 🌐 Option 4: Neon (Serverless PostgreSQL)

### Steps:

1. **Sign up**: https://neon.tech
2. **Create project**: Click "Create Project"
3. **Get connection string**: Copy from dashboard
4. **Update .env**:
```env
DATABASE_URL=postgresql://user:pass@ep-xxx.us-east-2.aws.neon.tech/neondb
```

5. **Push schema**:
```bash
prisma db push
```

### Advantages:
- ✅ Free tier (3GB)
- ✅ Serverless (auto-scales)
- ✅ Fast
- ✅ Modern

---

## 🔧 Troubleshooting

### Error: Can't reach database server

**Solutions**:
1. Check internet connection
2. Verify DATABASE_URL is correct
3. Check if database is active
4. Try a different database option

### Error: Authentication failed

**Solutions**:
1. Double-check password in DATABASE_URL
2. Make sure there are no extra spaces
3. URL-encode special characters in password

### Error: Database doesn't exist

**Solutions**:
1. Create the database first
2. Or use a database that auto-creates (Supabase, Neon)

---

## 📝 After Database is Working

Once your database connection works:

```bash
# 1. Generate Prisma client
prisma generate

# 2. Push schema (creates tables)
prisma db push

# 3. Test connection
python test_db_connection.py

# 4. Start the server
python app/main.py

# 5. View data (optional)
prisma studio
```

---

## 🎯 Recommended Path

For quickest setup:

1. **Try Supabase** (5 minutes)
   - Free, reliable, easy
   - Best for getting started

2. **Or use Local PostgreSQL** (10 minutes)
   - If you want full control
   - Good for development

3. **Keep Prisma Postgres** as backup
   - Check if it activates later
   - Good for production

---

## 💡 Quick Start with Supabase

```bash
# 1. Sign up at supabase.com
# 2. Create project
# 3. Copy connection string
# 4. Update .env:

DATABASE_URL=postgresql://postgres:your_password@db.xxx.supabase.co:5432/postgres

# 5. Run setup:
prisma generate
prisma db push

# 6. Start app:
python app/main.py
```

---

## 🆘 Still Having Issues?

1. **Check .env file**: Make sure DATABASE_URL has no quotes
2. **Test connection**: Run `python test_db_connection.py`
3. **Check logs**: Look for specific error messages
4. **Try different database**: Supabase is most reliable for quick start

---

**Once database is connected, everything else will work smoothly!** 🚀
