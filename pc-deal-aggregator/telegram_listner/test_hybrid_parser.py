"""
Test script for the hybrid parser with real sample messages
"""
import sys
import json
from app.parsers.hybrid_parser import HybridParser


# Sample messages from the user
SAMPLE_MESSAGES = [
    """❇️Lenovo Legion 5 Slim❇️🔱GAMING LAPTOP⚜️AMD Ryzen 7 ✅Base Speed 3.8GHZ(16 Logical Processor )❇️Up to 5.4 Ghz Boost Speed💠512 SSD  storage💠16GB DDR5 5600MHZ ram speed💻RTX 3060,6GB nvidia graphics card(plus has AMD radeon dedicated graphics card💻15.6" inch screen🔋BEST BATTERY LIFE🔋#PRICE 158000 birrcall@☎️0913066711     0984738694""",
    
    """....➡️➡️➡️New arrival   Brand new✍High ending gaming  lqptopAcer PREDATOR ➡️ RTX 3070TI 8GB Dedicated Graphics➡️    Intel core i9👈 amazing ➡️ 12th Generation 2024Base speed 2.9GHZ✅    Total Cores 14, Total Threads 20✅    Base speed @2.90Ghz✅   Up to4.90Ghz processor speed ➡️  1TB GB SSD storage➡️  16GB RAM  speed 8 slot expandable ✅    15.6 inch screen✅    2K Resolution ✅    165Hz Refresh rate ✅    RGB keyboard Backlight✅    BEST BATTERY LIFE👉Nividia Geforce RTX 3070Ti 8GB Dedicated GRAPHICS 👈#PRICE  ....168000 birr📞0913066711📞0984738694""",
    
    """...♦️New arrival  2025 product♦️Hp Omen 016🔝 RTX 4070 👈 8GB nvidia Dedicated Graphucs➡️ 32GB Ram DDR5 ➡️ 2TB SSD Storage Super fast ➡️ core i9 ➡️ 13th generation32 logical Processor  and 24 Core✅ Model : Hp OMEN 016✅ condition: Brand New ✅   Screen :2K resolution✅  Refrashing rat   240HZ✅ Screen siz 16 inch✅  :10hr.+ hours battery life ➡️  RGB keyboard backlit ✅  B&O HD Sound systemPrice :..........215000 birrcall@09130667110912206806""",
    
    """...➡️➡️WOW  ➡️WOW➡️WOW👈New arrival  2025 product➡️MSI Vector Gaming 👈🔝  RTX  4060 👈 8GB Dedicated  Graphucs➡️  16GB  Ram DDR5 ➡️ 1TB SSD  Storage   Super fast ➡️ core i9 ➡️ 13th generation32 logical Processor  and 24 Cores✅ Model : MSI vector ✅ condition: Brand New ✅   Screen :2K resolution✅  Refrashing rat   240HZ➡️➡️ Dedicated Graphics  8GB NIVIDA   4060Ti RTX✅ Screen siz 16 inch✅  :10hr.+ hours battery life ➡️  RGB keyboard backlit ✅  B&O HD Sound systemPrice :..........189000 birrcall@09130667110984738694""",
    
    """....♦️arrived again in my stock♦️💻High End gaming laptop💻✅INTEL CORE I7-14900HX(high end gaming and excellent performance GPU)✅ BRAND NEW HP OMEN 16💻Core i9-13th Generation 💻 1TB SSD STORAGE💻 32GB RAM DDR5💻2K RESOLUTION (2560x1440)💻16 inch✅✅ REFRESH RATE 240HZ🎆Nvidia Geforce RTX 40608gb dedicated graphics(VRam)for  PRICE .... 195000 birr 👇👇👇👇👇👇📞0913066711     0984738694inbox me for more:@Samibay2""",
    
    """...🩸hp elitebook new✅ryze5 pro,5600 series(core i5 12th gen)✅6 cores and 12.cpu✅16gb ram✅512 gb ssd✅14.0 inch✅7hrs battery lifeprice...call@09130667110912206806""",
    
    """...NEW ARRIVAL 🔴 BRAND NEW HP NOTEBOOK ❇️13TH GEN Intel®core I5 -1335P❇️Storage : 512gb storage ❇️ram : 16gb❇️12 cores 16 Logical processors ❇️Inch :14.1❇️Intel (R) Iris(R)Xe graphics 💵 price:115000 birrcall@0913066711          0912206806""",
    
    """...✅Dell precision 5560📘work station laptop✅for 3D modelings,CAD,AI and for content creations...📘RTX A2000,4gb nvidia graphics card📘core i7 11th genaration📘8 cores & 16 cpus📘16gb ram✅orginal C type charger📘2k screen resolutions📘15.6" screen size🔋long last battery lifeprice.....138000 birrcall@09130667110912206806""",
    
    """...➡️New arrival ➡️WOW😮   Ultra 7  155H. 15.6 inchBrand  New   hp Notebook   H processor2025Ultra 7   155H➡️  15th generationhigh spec laptop  2025➡️  15.6 inch  screen siz➡️513 GB. SSD Storage➡️16GB Ram   DDR5 5600MHZ➡️Base speed   3.8 GHZ 😮➡️16 core and 22logical processor✅ Model   : HP Notebook  2025✅   Condition: Brand  new  15th generation✅   With intel Arc Graphics card ✅  Best. battery life Price :    @sww2844📞0928442662📞0940141114https://t.me/samcomptech""",
    
    """...➡️New arrival⬅️High ending gaming   Hp Omen 016  Gaming✅  GAMING LAPTOP➡️ core i7👈 amazing ➡️ 12th Generation   2025✅   Up to4.90Ghz processor speed ➡️  512GB SSD storage Super fast➡️➡️ 16GB   DDR5 expandable ✅    15.6  inch screen✅    2K Resolution ✅    165Hz Refresh rate ✅    RGB keyboard Backlight✅    BEST BATTERY LIFE➡️➡️Nividia Geforce RTX 3060 6GB Dedicated GRAPHICS 👈#PRICE  .... @sww2844📞0928442662📞0940141114https://t.me/samcomptech""",
    
    """...➡️New arrival ➡️ With 32GB Ram 👈Brand New  Hp zbook  G8 workstation  laptop👍 Graphics Nividay T500 Dedicated 4GB 👈➡️ core i7➡️11th generation   2025➡️512 GB SSD storage➡️ Ram 32 GB DRR4✅    micro-edge  CorningGorilla, with Eyes detect  ❇️  Edge to edge screen with IPS display❇️  DTS  speakers➡️14.1" inch screen with FULL HD resolution✅ Battery life above 7hrs🎆  Dedicated GTX T500  4GB Graphicsprice     @sww2844📞0940141114📞0928442662https://t.me/samcomptech"""
]


def test_parser():
    """Test the hybrid parser with sample messages"""
    import sys
    import io
    
    # Fix Windows encoding issues
    if sys.platform == 'win32':
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    
    print("=" * 80)
    print("HYBRID PARSER TEST - Sample Telegram Messages")
    print("=" * 80)
    print()
    
    parser = HybridParser()
    
    for i, message in enumerate(SAMPLE_MESSAGES, 1):
        print(f"\n{'=' * 80}")
        print(f"MESSAGE {i}")
        print(f"{'=' * 80}")
        print(f"\nOriginal (first 150 chars):")
        print(message[:150] + "..." if len(message) > 150 else message)
        print()
        
        # Parse the message
        result = parser.parse(message)
        
        # Display key extracted fields
        print("EXTRACTED DATA:")
        print("-" * 80)
        
        key_fields = [
            ('Title', 'title'),
            ('Model', 'model'),
            ('Processor', 'processor'),
            ('Generation', 'generation'),
            ('RAM', 'ram'),
            ('Storage', 'storage'),
            ('Screen Size', 'screen_size'),
            ('Resolution', 'resolution'),
            ('Graphics Card', 'graphics_card'),
            ('Graphics Memory', 'graphics_memory'),
            ('Battery Life', 'battery_life'),
            ('Condition', 'condition'),
            ('Price', 'price'),
            ('Currency', 'currency'),
            ('Contact Numbers', 'contact_numbers'),
            ('URLs', 'urls'),
            ('Categories', 'categories'),
            ('General Score', 'general_score'),
        ]
        
        for label, field in key_fields:
            value = result.get(field)
            if value is not None and value != [] and value != '':
                if isinstance(value, list):
                    print(f"{label:20}: {', '.join(map(str, value))}")
                else:
                    print(f"{label:20}: {value}")
        
        print()
    
    print("\n" + "=" * 80)
    print("TEST COMPLETE")
    print("=" * 80)


def test_single_message(message: str):
    """Test a single message and output full JSON"""
    parser = HybridParser()
    result = parser.parse(message)
    
    # Remove raw_message for cleaner output
    result_clean = {k: v for k, v in result.items() if k != 'raw_message'}
    
    print(json.dumps(result_clean, indent=2, default=str))


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--json":
        # Test first message and output JSON
        test_single_message(SAMPLE_MESSAGES[0])
    else:
        # Run full test suite
        test_parser()
