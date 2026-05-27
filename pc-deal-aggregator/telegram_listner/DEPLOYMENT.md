# Deployment Guide

Complete guide for deploying the PC Deal Aggregator to production.

---

## 🎯 Deployment Options

1. **Cloud Platform** (Recommended)
   - Railway
   - Render
   - Fly.io
   - DigitalOcean App Platform

2. **VPS** (More Control)
   - DigitalOcean Droplet
   - AWS EC2
   - Google Cloud Compute
   - Linode

3. **Containerized** (Most Flexible)
   - Docker + Docker Compose
   - Kubernetes

---

## 🚀 Option 1: Railway (Easiest)

### Prerequisites
- GitHub account
- Railway account (free tier available)

### Steps

1. **Push to GitHub**
```bash
git init
git add .
git commit -m "Initial commit"
git remote add origin https://github.com/yourusername/pc-deal-aggregator.git
git push -u origin main
```

2. **Create `railway.json`**
```json
{
  "$schema": "https://railway.app/railway.schema.json",
  "build": {
    "builder": "NIXPACKS"
  },
  "deploy": {
    "startCommand": "prisma generate && prisma db push && python app/main.py",
    "restartPolicyType": "ON_FAILURE",
    "restartPolicyMaxRetries": 10
  }
}
```

3. **Create `Procfile`**
```
web: prisma generate && prisma db push && uvicorn app.main:app --host 0.0.0.0 --port $PORT
```

4. **Deploy on Railway**
   - Go to railway.app
   - Click "New Project"
   - Select "Deploy from GitHub repo"
   - Choose your repository
   - Add PostgreSQL database (from Railway marketplace)
   - Set environment variables (see below)
   - Deploy!

### Environment Variables on Railway
```
DATABASE_URL=<auto-filled by Railway>
TELEGRAM_API_ID=your_api_id
TELEGRAM_API_HASH=your_api_hash
TELEGRAM_WATCHED_CHANNELS=@pcagregator
PORT=8000
```

---

## 🐳 Option 2: Docker

### Create `Dockerfile`

```dockerfile
FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application
COPY . .

# Generate Prisma client
RUN prisma generate

# Expose port
EXPOSE 8000

# Start command
CMD ["sh", "-c", "prisma db push && uvicorn app.main:app --host 0.0.0.0 --port 8000"]
```

### Create `docker-compose.yml`

```yaml
version: '3.8'

services:
  db:
    image: postgres:15-alpine
    environment:
      POSTGRES_USER: pcdeals
      POSTGRES_PASSWORD: your_secure_password
      POSTGRES_DB: pc_deals
    volumes:
      - postgres_data:/var/lib/postgresql/data
    ports:
      - "5432:5432"
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U pcdeals"]
      interval: 10s
      timeout: 5s
      retries: 5

  api:
    build: .
    ports:
      - "8000:8000"
    environment:
      DATABASE_URL: postgresql://pcdeals:your_secure_password@db:5432/pc_deals?schema=public
      TELEGRAM_API_ID: ${TELEGRAM_API_ID}
      TELEGRAM_API_HASH: ${TELEGRAM_API_HASH}
      TELEGRAM_WATCHED_CHANNELS: ${TELEGRAM_WATCHED_CHANNELS}
    depends_on:
      db:
        condition: service_healthy
    volumes:
      - ./downloaded_images:/app/downloaded_images
      - ./session_name.session:/app/session_name.session
    restart: unless-stopped

volumes:
  postgres_data:
```

### Deploy with Docker

```bash
# Build and start
docker-compose up -d

# View logs
docker-compose logs -f api

# Stop
docker-compose down

# Rebuild after changes
docker-compose up -d --build
```

---

## 🖥️ Option 3: VPS (DigitalOcean)

### 1. Create Droplet

- Choose Ubuntu 22.04 LTS
- Select size (minimum: 2GB RAM)
- Add SSH key
- Create droplet

### 2. Initial Setup

```bash
# SSH into server
ssh root@your_server_ip

# Update system
apt update && apt upgrade -y

# Install Python 3.11
apt install -y python3.11 python3.11-venv python3-pip

# Install PostgreSQL
apt install -y postgresql postgresql-contrib

# Install Nginx
apt install -y nginx

# Install Supervisor (for process management)
apt install -y supervisor
```

### 3. Setup PostgreSQL

```bash
# Switch to postgres user
sudo -u postgres psql

# Create database and user
CREATE DATABASE pc_deals;
CREATE USER pcdeals WITH PASSWORD 'your_secure_password';
GRANT ALL PRIVILEGES ON DATABASE pc_deals TO pcdeals;
\q
```

### 4. Setup Application

```bash
# Create app user
adduser --disabled-password --gecos "" pcdeals
su - pcdeals

# Clone repository
git clone https://github.com/yourusername/pc-deal-aggregator.git
cd pc-deal-aggregator/telegram_listner

# Create virtual environment
python3.11 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Setup environment
cp .env.example .env
nano .env  # Edit with your values

# Setup database
prisma generate
prisma db push

# Test run
python app/main.py
# Press Ctrl+C after confirming it works
```

### 5. Setup Supervisor

Create `/etc/supervisor/conf.d/pcdeals.conf`:

```ini
[program:pcdeals]
directory=/home/pcdeals/pc-deal-aggregator/telegram_listner
command=/home/pcdeals/pc-deal-aggregator/telegram_listner/venv/bin/uvicorn app.main:app --host 0.0.0.0 --port 8000
user=pcdeals
autostart=true
autorestart=true
stderr_logfile=/var/log/pcdeals/err.log
stdout_logfile=/var/log/pcdeals/out.log
environment=PATH="/home/pcdeals/pc-deal-aggregator/telegram_listner/venv/bin"

[program:pcdeals-listener]
directory=/home/pcdeals/pc-deal-aggregator/telegram_listner
command=/home/pcdeals/pc-deal-aggregator/telegram_listner/venv/bin/python start_listener.py
user=pcdeals
autostart=true
autorestart=true
stderr_logfile=/var/log/pcdeals/listener_err.log
stdout_logfile=/var/log/pcdeals/listener_out.log
environment=PATH="/home/pcdeals/pc-deal-aggregator/telegram_listner/venv/bin"
```

```bash
# Create log directory
mkdir -p /var/log/pcdeals
chown pcdeals:pcdeals /var/log/pcdeals

# Reload supervisor
supervisorctl reread
supervisorctl update
supervisorctl start pcdeals
supervisorctl start pcdeals-listener

# Check status
supervisorctl status
```

### 6. Setup Nginx

Create `/etc/nginx/sites-available/pcdeals`:

```nginx
server {
    listen 80;
    server_name your_domain.com;

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    location /images/ {
        alias /home/pcdeals/pc-deal-aggregator/telegram_listner/downloaded_images/;
    }
}
```

```bash
# Enable site
ln -s /etc/nginx/sites-available/pcdeals /etc/nginx/sites-enabled/
nginx -t
systemctl restart nginx
```

### 7. Setup SSL (Let's Encrypt)

```bash
# Install certbot
apt install -y certbot python3-certbot-nginx

# Get certificate
certbot --nginx -d your_domain.com

# Auto-renewal is set up automatically
```

---

## 🔒 Production Checklist

### Security

- [ ] Change all default passwords
- [ ] Use environment variables (never hardcode secrets)
- [ ] Enable HTTPS/SSL
- [ ] Configure firewall (UFW)
  ```bash
  ufw allow 22/tcp
  ufw allow 80/tcp
  ufw allow 443/tcp
  ufw enable
  ```
- [ ] Disable DEBUG mode (`DEBUG=False`)
- [ ] Configure specific CORS origins
- [ ] Add rate limiting
- [ ] Regular security updates
- [ ] Use strong PostgreSQL password
- [ ] Restrict database access

### Performance

- [ ] Enable database connection pooling
- [ ] Add Redis for caching (optional)
- [ ] Configure Nginx caching
- [ ] Enable gzip compression
- [ ] Monitor resource usage
- [ ] Set up log rotation

### Monitoring

- [ ] Set up error tracking (Sentry)
- [ ] Configure uptime monitoring (UptimeRobot)
- [ ] Set up log aggregation
- [ ] Monitor database performance
- [ ] Set up alerts

### Backup

- [ ] Automated database backups
  ```bash
  # Add to crontab
  0 2 * * * pg_dump -U pcdeals pc_deals > /backups/pc_deals_$(date +\%Y\%m\%d).sql
  ```
- [ ] Backup images directory
- [ ] Backup environment files
- [ ] Test restore procedure

---

## 📊 Monitoring Setup

### 1. Health Check Endpoint

Already available at `/health`

### 2. UptimeRobot

- Sign up at uptimerobot.com
- Add monitor for `https://your_domain.com/health`
- Set check interval to 5 minutes
- Configure email alerts

### 3. Sentry (Error Tracking)

```bash
pip install sentry-sdk[fastapi]
```

Add to `app/main.py`:

```python
import sentry_sdk

sentry_sdk.init(
    dsn="your_sentry_dsn",
    traces_sample_rate=1.0,
)
```

---

## 🔄 Deployment Workflow

### Initial Deployment

```bash
1. Setup infrastructure (database, server)
2. Clone repository
3. Install dependencies
4. Configure environment
5. Run migrations
6. Start services
7. Configure reverse proxy
8. Setup SSL
9. Test everything
10. Monitor
```

### Updates

```bash
# On server
cd /home/pcdeals/pc-deal-aggregator/telegram_listner
git pull
source venv/bin/activate
pip install -r requirements.txt
prisma generate
prisma db push
supervisorctl restart pcdeals
supervisorctl restart pcdeals-listener
```

### Rollback

```bash
git checkout <previous_commit>
supervisorctl restart pcdeals
```

---

## 🐛 Troubleshooting

### Service Won't Start

```bash
# Check logs
supervisorctl tail -f pcdeals stderr
tail -f /var/log/pcdeals/err.log

# Check if port is in use
netstat -tulpn | grep 8000

# Test manually
su - pcdeals
cd pc-deal-aggregator/telegram_listner
source venv/bin/activate
python app/main.py
```

### Database Connection Issues

```bash
# Test connection
psql -U pcdeals -d pc_deals -h localhost

# Check PostgreSQL status
systemctl status postgresql

# Check DATABASE_URL in .env
```

### Telegram Authentication

```bash
# Delete session and re-authenticate
rm session_name.session
supervisorctl restart pcdeals-listener
# Check logs for authentication prompt
```

---

## 📈 Scaling

### Vertical Scaling (Easier)

- Upgrade server resources (CPU, RAM)
- Increase database size
- Add more storage

### Horizontal Scaling (Better)

- Load balancer (Nginx)
- Multiple API instances
- Read replicas for database
- Redis for caching
- CDN for images

---

## 💰 Cost Estimates

### Small Scale (< 1000 deals/day)

- **Railway/Render**: $5-10/month
- **DigitalOcean Droplet**: $12/month (2GB)
- **Database**: Included or $7/month
- **Total**: ~$12-20/month

### Medium Scale (1000-10000 deals/day)

- **VPS**: $24/month (4GB)
- **Database**: $15/month
- **Monitoring**: $10/month
- **Total**: ~$50/month

### Large Scale (> 10000 deals/day)

- **Multiple servers**: $100+/month
- **Managed database**: $50+/month
- **CDN**: $20+/month
- **Monitoring**: $30+/month
- **Total**: ~$200+/month

---

## ✅ Post-Deployment

1. **Test all endpoints**
   ```bash
   curl https://your_domain.com/health
   curl https://your_domain.com/api/v1/deals
   ```

2. **Start Telegram listener**
   ```bash
   curl -X POST https://your_domain.com/api/v1/telegram/start
   ```

3. **Scrape historical data**
   ```bash
   curl -X POST https://your_domain.com/api/v1/telegram/scrape \
     -H "Content-Type: application/json" \
     -d '{"channel": "@pcagregator", "limit": 10000, "days_back": 180}'
   ```

4. **Monitor logs**
   ```bash
   tail -f /var/log/pcdeals/out.log
   ```

5. **Set up monitoring alerts**

6. **Document your deployment**

---

**Your PC Deal Aggregator is now live! 🎉**
