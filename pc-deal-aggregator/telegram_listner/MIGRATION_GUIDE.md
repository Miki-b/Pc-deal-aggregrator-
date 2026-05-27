# Migration Guide: MongoDB → PostgreSQL + FastAPI

This guide helps you migrate from the old MongoDB/Express setup to the new FastAPI/Prisma setup.

## 🔄 What's Changed

| Old | New |
|-----|-----|
| MongoDB | PostgreSQL + Prisma |
| Express.js | FastAPI |
| AI Parser (Gemini) | Hybrid Parser (Regex + spaCy) |
| Manual listener script | Integrated service with API control |
| Mongoose models | Prisma schema + Pydantic models |

## 📊 Data Migration

### Step 1: Export from MongoDB

```bash
# Export all deals to JSON
mongoexport --db=pc_deals --collection=deals --out=deals_backup.json --jsonArray
```

### Step 2: Transform Data

Create `migrate_data.py`:

```python
import json
import asyncio
from app.core.database import connect_db, prisma

async def migrate():
    await connect_db()
    
    # Load MongoDB export
    with open('deals_backup.json', 'r', encoding='utf-8') as f:
        old_deals = json.load(f)
    
    print(f"Found {len(old_deals)} deals to migrate")
    
    migrated = 0
    for deal in old_deals:
        try:
            # Transform MongoDB document to Prisma format
            prisma_deal = {
                "title": deal.get("title"),
                "model": deal.get("model"),
                "rawMessage": deal.get("raw_message", ""),
                "imagePath": deal.get("image_path"),
                "processor": deal.get("processor"),
                "generation": deal.get("generation"),
                "ram": deal.get("ram"),
                "storage": deal.get("storage"),
                "screenSize": deal.get("screen_size"),
                "resolution": deal.get("resolution"),
                "graphicsCard": deal.get("graphics_card"),
                "graphicsMemory": deal.get("graphics_memory"),
                "batteryLife": deal.get("battery_life"),
                "condition": deal.get("condition"),
                "price": deal.get("price"),
                "currency": deal.get("currency", "Birr"),
                "contactNumbers": deal.get("contact_numbers", []),
                "urls": deal.get("urls", []),
                "categories": deal.get("categories", []),
                "generalScore": deal.get("general_score", 0),
                "categoryScores": deal.get("category_scores", {}),
            }
            
            # Create in PostgreSQL
            await prisma.deal.create(data=prisma_deal)
            migrated += 1
            
            if migrated % 100 == 0:
                print(f"Migrated {migrated} deals...")
                
        except Exception as e:
            print(f"Error migrating deal: {e}")
            continue
    
    print(f"\n✅ Migration complete! Migrated {migrated}/{len(old_deals)} deals")

if __name__ == "__main__":
    asyncio.run(migrate())
```

Run it:
```bash
python migrate_data.py
```

### Step 3: Verify Migration

```bash
# Check count in PostgreSQL
curl http://localhost:8000/api/v1/deals/stats

# Compare with MongoDB
mongo pc_deals --eval "db.deals.count()"
```

## 🔧 Code Migration

### Old: MongoDB Repository

```python
# Old code
from infrastructure.database.mongo_client import db

class DealRepository:
    collection = db["deals"]
    
    @staticmethod
    def insert(deal_dict: dict):
        result = DealRepository.collection.insert_one(deal_dict)
        return result.inserted_id
```

### New: Prisma Service

```python
# New code
from app.core.database import prisma
from app.services.deal_service import DealService

deal_service = DealService(prisma)
deal = await deal_service.create_deal(deal_dict)
```

### Old: Express API

```javascript
// Old code
app.get("/api/v1/deals", async (req, res) => {
    const deals = await DealRepository.getAllDeals();
    res.json(deals);
});
```

### New: FastAPI

```python
# New code
@router.get("/deals", response_model=PaginatedDeals)
async def get_deals(page: int = 1, page_size: int = 50):
    deal_service = DealService(prisma)
    deals, total = await deal_service.get_deals(
        skip=(page-1)*page_size,
        limit=page_size
    )
    return PaginatedDeals(deals=deals, total=total, ...)
```

### Old: AI Parser

```python
# Old code - costs money, slow
from app.agents.ai_agent import AIAgentParser

parser = AIAgentParser()
result = parser.parse(message_text)  # 1-3 seconds, API call
```

### New: Hybrid Parser

```python
# New code - free, instant
from app.parsers.hybrid_parser import HybridParser

parser = HybridParser()
result = parser.parse(message_text)  # <0.01 seconds, no API
```

## 🚀 Deployment Changes

### Old Deployment

```bash
# Start MongoDB
mongod

# Start Express API
cd Express-api
npm start

# Start Telegram listener (separate terminal)
cd telegram_listner
python listener.py
```

### New Deployment

```bash
# Start PostgreSQL (or use cloud)
# Already running

# Start FastAPI (includes everything)
cd telegram_listner
python app/main.py

# Start listener via API
curl -X POST http://localhost:8000/api/v1/telegram/start
```

## 📝 Environment Variables

### Old `.env`

```env
API_ID=12345
API_HASH=abc123
MONGO_URI=mongodb://localhost:27017
WATCHED_CHANNELS=@pcagregator
GOOGLE_API_KEY=xyz789
```

### New `.env`

```env
DATABASE_URL=postgresql://user:pass@localhost:5432/pc_deals
TELEGRAM_API_ID=12345
TELEGRAM_API_HASH=abc123
TELEGRAM_WATCHED_CHANNELS=@pcagregator
# No GOOGLE_API_KEY needed!
```

## 🎯 Feature Comparison

| Feature | Old | New |
|---------|-----|-----|
| **Database** | MongoDB | PostgreSQL |
| **ORM** | Mongoose | Prisma |
| **API Framework** | Express.js | FastAPI |
| **Parser** | AI (Gemini) | Hybrid (Regex + spaCy) |
| **Parsing Cost** | $0.0001-0.001/msg | $0 |
| **Parsing Speed** | 1-3 sec | <0.01 sec |
| **API Docs** | Manual | Auto-generated (Swagger) |
| **Type Safety** | ❌ | ✅ (Pydantic + Prisma) |
| **Async Support** | Partial | Full |
| **Pagination** | Manual | Built-in |
| **Filtering** | Basic | Advanced |
| **Statistics** | None | Built-in |
| **Image Serving** | Static | Static |
| **Listener Control** | Manual script | API endpoints |
| **Historical Scraping** | Manual | API endpoint |

## ✅ Benefits of New System

1. **Cost Savings**: No AI API costs (save $1-10 per 10k messages)
2. **Performance**: 100-300x faster parsing
3. **Type Safety**: Prisma + Pydantic catch errors at compile time
4. **Better API**: Auto-generated docs, validation, async support
5. **Easier Deployment**: Single service instead of multiple
6. **Better DX**: FastAPI hot reload, better error messages
7. **Scalability**: PostgreSQL scales better than MongoDB for this use case
8. **Advanced Queries**: Better filtering, sorting, aggregations

## 🔄 Gradual Migration Strategy

If you want to migrate gradually:

### Phase 1: Run Both Systems
- Keep old system running
- Start new system on different port
- Compare results

### Phase 2: Migrate Data
- Export from MongoDB
- Import to PostgreSQL
- Verify data integrity

### Phase 3: Switch Traffic
- Update clients to use new API
- Monitor for issues
- Keep old system as backup

### Phase 4: Decommission Old System
- Stop old services
- Archive MongoDB data
- Remove old code

## 🆘 Rollback Plan

If you need to rollback:

1. **Keep MongoDB backup**:
   ```bash
   mongodump --db=pc_deals --out=backup/
   ```

2. **Keep old code**:
   ```bash
   git branch old-system
   ```

3. **Document issues** before rolling back

4. **Restore if needed**:
   ```bash
   mongorestore backup/
   git checkout old-system
   ```

## 📞 Support

If you encounter issues during migration:
1. Check the [README.md](README.md)
2. Review [QUICKSTART.md](QUICKSTART.md)
3. Check server logs
4. Compare old vs new data structures

---

**Migration typically takes 1-2 hours for a clean setup!**
