"""
Setup script for PC Deal Aggregator
Run this after installing requirements.txt
"""
import subprocess
import sys
import os


def run_command(command, description):
    """Run a shell command and handle errors"""
    print(f"\n{'='*60}")
    print(f"📦 {description}")
    print(f"{'='*60}")
    
    try:
        result = subprocess.run(
            command,
            shell=True,
            check=True,
            capture_output=True,
            text=True
        )
        print(result.stdout)
        print(f"✅ {description} completed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Error: {e}")
        print(f"Output: {e.stdout}")
        print(f"Error: {e.stderr}")
        return False


def check_env_file():
    """Check if .env file exists and has required variables"""
    print(f"\n{'='*60}")
    print("🔍 Checking .env file")
    print(f"{'='*60}")
    
    if not os.path.exists(".env"):
        print("❌ .env file not found!")
        print("\nPlease create a .env file with the following variables:")
        print("""
DATABASE_URL="postgresql://user:password@localhost:5432/pc_deals?schema=public"
TELEGRAM_API_ID=your_api_id
TELEGRAM_API_HASH=your_api_hash
TELEGRAM_WATCHED_CHANNELS=@pcagregator
        """)
        return False
    
    # Check for required variables
    required_vars = ["DATABASE_URL", "TELEGRAM_API_ID", "TELEGRAM_API_HASH"]
    missing_vars = []
    
    with open(".env", "r") as f:
        content = f.read()
        for var in required_vars:
            if var not in content:
                missing_vars.append(var)
    
    if missing_vars:
        print(f"❌ Missing required variables: {', '.join(missing_vars)}")
        return False
    
    print("✅ .env file looks good")
    return True


def main():
    """Main setup process"""
    print("""
    ╔═══════════════════════════════════════════════════════════╗
    ║                                                           ║
    ║         PC Deal Aggregator - Setup Script                ║
    ║                                                           ║
    ╚═══════════════════════════════════════════════════════════╝
    """)
    
    # Check Python version
    if sys.version_info < (3, 10):
        print("❌ Python 3.10 or higher is required")
        sys.exit(1)
    
    print(f"✅ Python version: {sys.version}")
    
    # Check .env file
    if not check_env_file():
        sys.exit(1)
    
    # Generate Prisma client
    if not run_command(
        "prisma generate",
        "Generating Prisma client"
    ):
        print("\n⚠️  Prisma generate failed. Make sure Prisma is installed:")
        print("   pip install prisma")
        sys.exit(1)
    
    # Push database schema
    print("\n" + "="*60)
    print("🗄️  Database Setup")
    print("="*60)
    print("\nThis will create/update database tables.")
    response = input("Continue? (y/n): ")
    
    if response.lower() == 'y':
        if not run_command(
            "prisma db push",
            "Pushing database schema"
        ):
            print("\n⚠️  Database push failed. Check your DATABASE_URL in .env")
            sys.exit(1)
    else:
        print("⏭️  Skipped database setup")
    
    # Create directories
    print(f"\n{'='*60}")
    print("📁 Creating directories")
    print(f"{'='*60}")
    
    os.makedirs("downloaded_images", exist_ok=True)
    print("✅ Created downloaded_images/")
    
    # Final message
    print(f"\n{'='*60}")
    print("🎉 Setup Complete!")
    print(f"{'='*60}")
    print("""
Next steps:

1. Start the API server:
   python app/main.py

2. Visit the API docs:
   http://localhost:8000/docs

3. Start the Telegram listener:
   curl -X POST http://localhost:8000/api/v1/telegram/start

4. Or run the standalone listener:
   python start_listener.py

5. Scrape historical data:
   curl -X POST http://localhost:8000/api/v1/telegram/scrape \\
     -H "Content-Type: application/json" \\
     -d '{"channel": "@pcagregator", "limit": 1000, "days_back": 180}'

For more information, see README.md
    """)


if __name__ == "__main__":
    main()
