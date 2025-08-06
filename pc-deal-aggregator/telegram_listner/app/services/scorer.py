from typing import Dict, Tuple
import re

# -----------------------------
# Brand and Model Scoring Tiers
# -----------------------------
BRAND_TIERS = {
    "hp": {
        "omen": 3,
        "spectre": 3,
        "pavilion plus": 2,
        "envy": 2,
        "pavilion": 1.5,
        "probook": 1,
    },
    "dell": {
        "alienware": 3,
        "xps": 3,
        "latitude": 2,
        "inspiron": 1,
        "vostro": 1,
    },
    "lenovo": {
        "legion": 3,
        "thinkpad": 2,
        "ideapad": 1,
    },
    "asus": {
        "rog": 3,
        "zenbook": 2,
        "vivobook": 1,
    },
    "acer": {
        "predator": 3,
        "swift": 2,
        "aspire": 1,
    },
    "apple": {
        "macbook pro": 3,
        "macbook air": 2,
    },
}

def get_brand_model_score(title: str, model: str) -> Tuple[str, int]:
    title = (title or "").lower()
    model = (model or "").lower()

    for brand, models in BRAND_TIERS.items():
        if brand in title or brand in model:
            for m, score in sorted(models.items(), key=lambda x: -len(x[0])):  # Longest first
                if m in title or m in model:
                    return f"{brand.title()} {m.title()}", score
            return brand.title(), 1
    return "Unknown", 0

def extract_gpu_family(gpu_text: str) -> str:
    gpu_text = (gpu_text or "").lower()
    if "rtx" in gpu_text: return "RTX"
    if "gtx" in gpu_text: return "GTX"
    if "mx" in gpu_text: return "MX"
    if "iris" in gpu_text: return "Intel Iris"
    if "uhd" in gpu_text: return "Intel UHD"
    return "Unknown"

# -----------------------------
# Main Deal Scoring Function
# -----------------------------
def score_deal(deal: Dict) -> Tuple[int, Dict[str, int]]:
    general_score = 0
    category_scores = {}

    processor = (deal.get("processor") or "").lower()
    ram = (deal.get("ram") or "").lower()
    storage = (deal.get("storage") or "").lower()
    graphics = (deal.get("graphics") or "").lower()
    screen = (deal.get("screen_size") or "").lower()
    price = deal.get("price") or 0
    categories = [c.lower() for c in deal.get("categories", [])]

    CPU_TIERS = {
        "high": ["i9", "ryzen 9", "apple m2 max", "apple m1 max"],
        "mid": ["i7", "ryzen 7", "apple m1", "apple m2", "m3"],
        "standard": ["i5", "ryzen 5"],
        "low": ["i3", "ryzen 3", "celeron", "pentium"]
    }

    GPU_TIERS = {
        "high": ["rtx 4080", "rtx 4090", "radeon 7900", "intel arc a770"],
        "mid": ["rtx 3060", "rtx 3070", "radeon 6700", "gtx 1660", "intel arc a370"],
        "low": ["mx450", "intel uhd", "intel iris", "vega 8"]
    }

    def match_tier(text: str, tier_map: Dict[str, list]) -> str:
        for tier, keywords in tier_map.items():
            if any(k in text for k in keywords):
                return tier
        return "unknown"

    def extract_gb(text: str) -> int:
        match = re.search(r'(\d+)\s*gb', text)
        return int(match.group(1)) if match else 0

    def extract_tb_gb_storage(text: str) -> int:
        tb = re.search(r'(\d+)\s*tb', text)
        gb = re.search(r'(\d+)\s*gb', text)
        size = 0
        if tb:
            size += int(tb.group(1)) * 1024
        if gb:
            size += int(gb.group(1))
        return size

    # CPU
    cpu_tier = match_tier(processor, CPU_TIERS)
    general_score += {"high": 4, "mid": 3, "standard": 2, "low": 1}.get(cpu_tier, 0)

    # RAM
    ram_gb = extract_gb(ram)
    if ram_gb >= 32: general_score += 4
    elif ram_gb >= 16: general_score += 3
    elif ram_gb >= 8: general_score += 2
    elif ram_gb >= 4: general_score += 1

    # Storage
    storage_gb = extract_tb_gb_storage(storage)
    if storage_gb >= 2000: general_score += 3
    elif storage_gb >= 1000: general_score += 2
    elif storage_gb >= 512: general_score += 1

    # GPU
    gpu_tier = match_tier(graphics, GPU_TIERS)
    general_score += {"high": 3, "mid": 2, "low": 1}.get(gpu_tier, 0)

    # Screen size
    if "15" in screen or "16" in screen:
        general_score += 1

    # Price-performance ratio
    if price > 0:
        value_score = (general_score / price) * 100000
        if value_score > 0.2:
            general_score += 1
        elif value_score < 0.08:
            general_score -= 1

    # -----------------------------
    # Category-specific adjustments
    # -----------------------------
    def add_score(category: str, points: int):
        category_scores[category] = category_scores.get(category, 0) + points

    for category in categories:
        if category == "gaming":
            if gpu_tier == "high": add_score("Gaming", 5)
            if ram_gb >= 16: add_score("Gaming", 3)
            if cpu_tier in ["high", "mid"]: add_score("Gaming", 2)

        elif category == "programming":
            if cpu_tier in ["standard", "mid"]: add_score("Programming", 2)
            if ram_gb >= 16: add_score("Programming", 2)
            if "14" in screen or "15" in screen: add_score("Programming", 1)

        elif category == "graphic design":
            if gpu_tier in ["high", "mid"]: add_score("Graphic Design", 3)
            if ram_gb >= 16: add_score("Graphic Design", 2)

        elif category == "student laptop":
            if price < 30000: add_score("Student Laptop", 3)
            if ram_gb >= 8: add_score("Student Laptop", 2)
            if weight := deal.get("weight", "").lower():
                try:
                    if "light" in weight or float(weight.replace("kg", "").strip()) < 1.6:
                        add_score("Student Laptop", 1)
                except ValueError:
                    pass

        elif category == "budget":
            if price < 25000: add_score("Budget", 3)
            if cpu_tier == "low": add_score("Budget", 2)

        elif category == "workstation":
            if ram_gb >= 32: add_score("Workstation", 4)
            if cpu_tier == "high": add_score("Workstation", 3)
            if storage_gb >= 2000: add_score("Workstation", 2)

        elif category == "video editing":
            if gpu_tier == "high": add_score("Video Editing", 3)
            if ram_gb >= 16: add_score("Video Editing", 2)

        elif category in BRAND_TIERS:
            add_score(f"Brand_{category.title()}", 1)

        elif category in ["touchscreen", "2-in-1", "ultrabook"]:
            add_score("Features", 1)

    # Brand + model contribution
    title = deal.get("title", "")
    model = deal.get("model", "")
    brand_key, brand_score = get_brand_model_score(title, model)
    general_score += brand_score
    category_scores[f"Brand_{brand_key}"] = brand_score

    return general_score, category_scores
