# Historical scrape guide (6 months → database)

Use this workflow to **backfill** PC deal posts for analysis. The **live listener is paused** — use `scrape_history.py` instead of `start_listener.py`.

## Channels configured

| Channel | Link |
|---------|------|
| @pcagregator | https://t.me/pcagregator |
| @samcomptech | https://t.me/samcomptech |
| @sami_brand12 | https://t.me/sami_brand12 |

Edit `.env` → `TELEGRAM_SCRAPE_CHANNELS` to add more (comma-separated).

## Prerequisites

1. **Stop the live listener** if it is running (`Ctrl+C` on `start_listener.py`).
2. **Telegram logged in** — `session_name.session` must exist (`python telegram_login.py` once).
3. **Database connected** — Neon `DATABASE_URL` in `.env`, VPN off if needed.
4. **Joined the channels** — your Telegram account must be able to open each channel (public channels: open once in Telegram app).

## One-time setup

```powershell
cd telegram_listner

# Apply schema (posted_at + duplicate protection)
prisma generate
prisma db push

# Confirm login
python telegram_login.py
```

## Run the 6-month backfill

```powershell
python scrape_history.py --yes
```

This will:

- Read up to **10,000 messages per channel** (adjust in `.env`)
- Keep only the **last 180 days** (~6 months)
- **Skip images** (default)
- **Skip duplicates** (same channel + message id)
- **Skip non-deal posts** (no price/spec keywords)
- Store **posted_at** for time-series analysis

### Options

```powershell
# One channel only (quote @ on PowerShell!)
python scrape_history.py --yes --channel "@samcomptech"

# Shorter test (7 days)
python scrape_history.py --yes --days 7 --limit 200
```

## Verify data in the database

```powershell
python test_db_connection.py
```

Or in Neon SQL editor:

```sql
SELECT COUNT(*) FROM deals;
SELECT channel_id, COUNT(*) FROM deals GROUP BY channel_id;
SELECT DATE(posted_at), COUNT(*) FROM deals GROUP BY 1 ORDER BY 1;
```

## `.env` settings

```env
TELEGRAM_SCRAPE_CHANNELS=@pcagregator,@samcomptech,@sami_brand12
SCRAPE_DAYS_BACK=180
SCRAPE_LIMIT_PER_CHANNEL=10000
SCRAPE_DOWNLOAD_IMAGES=false
SCRAPE_REQUIRE_DEAL_SIGNAL=true
```

## When to turn the live listener back on

After backfill finishes and you are happy with row counts:

1. Set `TELEGRAM_WATCHED_CHANNELS` to the channels you want live.
2. Run `python start_listener.py` for **new** messages only (duplicates are still skipped).

## Troubleshooting

| Issue | Fix |
|-------|-----|
| `Can't reach database` | Disable VPN; check Neon is active |
| `PhoneNumberInvalidError` | Use `+251...` in `TELEGRAM_PHONE` |
| `Channel private` | Join channel in Telegram app first |
| Very few rows saved | Normal — filter removes non-laptop posts; try `SCRAPE_REQUIRE_DEAL_SIGNAL=false` |
| Flood wait | Wait and re-run; duplicates are skipped |

## Analysis tips

Exported fields useful for analysis: `price`, `processor`, `ram`, `storage`, `categories`, `general_score`, `posted_at`, `channel_id`, `raw_message`.
