"""
High-quality hybrid parser combining regex patterns and spaCy EntityRuler
for extracting laptop deal information from Telegram messages.
"""
import re
import spacy
from spacy.pipeline import EntityRuler
from typing import Dict, List, Optional, Any
from datetime import datetime
from app.parsers.base_parser import BaseParser
from app.services.catagorizer import categorize_deal
from app.services.scorer import score_deal


class HybridParser(BaseParser):
    def __init__(self):
        # Load spaCy with blank English model (lightweight)
        self.nlp = spacy.blank("en")
        
        # Add EntityRuler to the pipeline
        ruler = self.nlp.add_pipe("entity_ruler", config={"overwrite_ents": True})
        
        # Define patterns for entity recognition
        patterns = self._build_entity_patterns()
        ruler.add_patterns(patterns)
        
        # Compile regex patterns for structured fields
        self.regex_patterns = self._build_regex_patterns()
    
    def parse(self, message_text: str) -> dict:
        """Main parsing method combining regex and spaCy NER"""
        if not message_text or not message_text.strip():
            return self._empty_result(message_text)
        
        # Clean the message for better parsing
        cleaned_text = self._clean_text(message_text)
        
        # Extract using regex (fast, structured fields)
        result = self._extract_with_regex(cleaned_text, message_text)
        
        # Extract using spaCy NER (context-aware, fuzzy fields)
        spacy_result = self._extract_with_spacy(cleaned_text)
        
        # Merge results (spaCy fills gaps left by regex)
        result = self._merge_results(result, spacy_result)
        
        # Post-processing and normalization
        result = self._normalize_result(result, message_text)
        
        return result
    
    def _clean_text(self, text: str) -> str:
        """Clean text while preserving important information"""
        # Remove excessive emojis but keep text
        cleaned = re.sub(r'[➡️⬅️✅❇️🔱⚜️💠💻🔋💵📘🔴🩸♦️🎆👈👉👇🔝💻📞☎️@]', ' ', text)
        # Normalize whitespace
        cleaned = re.sub(r'\s+', ' ', cleaned)
        # Remove excessive dots
        cleaned = re.sub(r'\.{3,}', ' ', cleaned)
        return cleaned.strip()
    
    def _build_regex_patterns(self) -> Dict[str, re.Pattern]:
        """Build compiled regex patterns for structured fields"""
        return {
            # Price patterns - handles various formats
            'price': re.compile(
                r'(?:price|PRICE|Price)?\s*[:\-.]?\s*'
                r'([\d,]+)\s*'
                r'(?:birr|Birr|BIRR|ETB|etb)',
                re.IGNORECASE
            ),
            
            # Alternative price pattern (just numbers + birr)
            'price_simple': re.compile(r'([\d,]+)\s*(?:birr|Birr|BIRR)', re.IGNORECASE),

            # Price: 85,500 or Price : 85,500 (birr optional — common in Telegram posts)
            'price_labeled': re.compile(
                r'(?:price|PRICE|Price)\s*[:\-.]\s*([\d,]+)(?:\s*(?:birr|Birr|BIRR|ETB|etb))?',
                re.IGNORECASE,
            ),
            
            # Phone numbers - Ethiopian format
            'phone': re.compile(
                r'(?:call@|call|phone|contact|📞|☎️)?\s*'
                r'(\+?251|0)?([79]\d{8})',
                re.IGNORECASE
            ),
            
            # RAM - various formats (more specific to avoid false matches)
            'ram': re.compile(
                r'(?:^|[^\d])(\d+)\s*(?:GB|gb|Gb)\s*'
                r'(?:RAM|ram|Ram|DDR[345]|ddr[345])\s*'
                r'(?:DDR[345]|ddr[345])?\s*'
                r'(?:(\d+)\s*(?:MHZ|mhz|MHz))?',
                re.IGNORECASE
            ),
            
            # Storage - SSD/HDD with size (more specific)
            'storage': re.compile(
                r'(?:^|[^\d])(\d+)\s*(?:TB|GB|tb|gb)\s*'
                r'(?:SSD|ssd|HDD|hdd|NVMe|nvme|PCIe|pcie|storage|Storage|STORAGE)',
                re.IGNORECASE
            ),
            
            # Screen size
            'screen_size': re.compile(
                r'(\d+\.?\d*)\s*(?:inch|"|Inch|INCH)',
                re.IGNORECASE
            ),
            
            # Resolution
            'resolution': re.compile(
                r'(?:(\d+)\s*[xX*×]\s*(\d+))|'  # 1920x1080 format
                r'(?:(FHD|fhd|Full HD|FULL HD|full hd))|'  # FHD
                r'(?:(2K|2k|QHD|qhd))|'  # 2K
                r'(?:(4K|4k|UHD|uhd))',  # 4K
                re.IGNORECASE
            ),
            
            # Refresh rate
            'refresh_rate': re.compile(
                r'(\d+)\s*(?:Hz|hz|HZ)\s*(?:refresh|Refresh)?',
                re.IGNORECASE
            ),
            
            # Generation - processor generation
            'generation': re.compile(
                r'(\d+)(?:st|nd|rd|th)?\s*(?:gen|Gen|GEN|generation|Generation)',
                re.IGNORECASE
            ),
            
            # Processor - Intel/AMD patterns
            'processor_intel': re.compile(
                r'(?:Intel|intel|INTEL)?\s*'
                r'(?:Core|core|CORE)?\s*'
                r'(i[3579]|Ultra\s*[579])\s*'
                r'(?:-?\s*(\d{4,5}[A-Z]{0,3}))?',  # Model number like 13650H
                re.IGNORECASE
            ),
            
            'processor_amd': re.compile(
                r'(?:AMD|amd)?\s*'
                r'(?:Ryzen|ryzen|RYZEN)\s*'
                r'([3579])\s*'
                r'(?:Pro|pro|PRO)?\s*'
                r'(?:(\d{4}))?',  # Model number
                re.IGNORECASE
            ),
            
            # Graphics card - NVIDIA
            'gpu_nvidia': re.compile(
                r'(?:NVIDIA|nvidia|Nvidia|Nividia|NIVIDA)?\s*'
                r'(?:GeForce|Geforce|geforce)?\s*'
                r'(RTX|GTX|MX)\s*'
                r'([A-Z]?\d{4})\s*'
                r'(?:Ti|TI|ti)?',
                re.IGNORECASE
            ),
            
            # Graphics card - AMD
            'gpu_amd': re.compile(
                r'(?:AMD|amd)?\s*'
                r'(?:Radeon|radeon|RADEON)\s*'
                r'(RX)?\s*'
                r'(\d{4})',
                re.IGNORECASE
            ),

            # Intel integrated graphics (Iris, UHD, Arc)
            'gpu_intel': re.compile(
                r'(?:Intel|intel)\s*'
                r'(?:Iris|iris|UHD|uhd|Arc|arc)\s*'
                r'(?:Xe|xe)?\s*'
                r'(?:Graphics|graphics)?',
                re.IGNORECASE,
            ),
            
            # Graphics memory
            'gpu_memory': re.compile(
                r'(\d+)\s*(?:GB|gb)\s*'
                r'(?:GDDR[56]|gddr[56]|GDDR|gddr|VRAM|vram|VRam)?\s*'
                r'(?:dedicated|Dedicated|DEDICATED)?\s*'
                r'(?:graphics|Graphics|GRAPHICS)?',
                re.IGNORECASE
            ),
            
            # Battery life (10 hours battery / 10 hours battery life)
            'battery': re.compile(
                r'(\d+)\s*(?:\+)?\s*'
                r'(?:hr|hrs|hour|hours)\s*'
                r'(?:battery|Battery|BATTERY)(?:\s*life)?',
                re.IGNORECASE
            ),
            
            # Condition keywords
            'condition': re.compile(
                r'(?:Brand\s*New|brand\s*new|BRAND\s*NEW|'
                r'New\s*arrival|new\s*arrival|NEW\s*ARRIVAL|'
                r'PACKED|packed|Packed|'
                r'Used|used|USED|'
                r'Like\s*new|like\s*new)',
                re.IGNORECASE
            ),
            
            # Telegram URLs
            'telegram_url': re.compile(
                r'(?:https?://)?t\.me/[\w]+',
                re.IGNORECASE
            ),
            
            # Telegram handles
            'telegram_handle': re.compile(
                r'@[\w]+',
                re.IGNORECASE
            ),
        }
    
    def _build_entity_patterns(self) -> List[Dict[str, Any]]:
        """Build spaCy EntityRuler patterns for context-aware extraction"""
        patterns = []
        
        # Brand patterns (case-insensitive matching)
        brands = ["HP", "Dell", "Lenovo", "Acer", "Asus", "MSI", "Apple", "Microsoft", "Razer"]
        for brand in brands:
            patterns.append({
                "label": "BRAND",
                "pattern": [{"LOWER": brand.lower()}]
            })
        
        # Model series patterns
        model_series = [
            # HP models
            (["omen"], "MODEL"),
            (["pavilion"], "MODEL"),
            (["spectre"], "MODEL"),
            (["envy"], "MODEL"),
            (["elitebook"], "MODEL"),
            (["probook"], "MODEL"),
            (["zbook"], "MODEL"),
            (["notebook"], "MODEL"),
            
            # Dell models
            (["xps"], "MODEL"),
            (["inspiron"], "MODEL"),
            (["latitude"], "MODEL"),
            (["precision"], "MODEL"),
            (["alienware"], "MODEL"),
            
            # Lenovo models
            (["legion"], "MODEL"),
            (["thinkpad"], "MODEL"),
            (["ideapad"], "MODEL"),
            (["yoga"], "MODEL"),
            
            # Acer models
            (["predator"], "MODEL"),
            (["aspire"], "MODEL"),
            (["swift"], "MODEL"),
            (["nitro"], "MODEL"),
            
            # Asus models
            (["rog"], "MODEL"),
            (["zenbook"], "MODEL"),
            (["vivobook"], "MODEL"),
            (["tuf"], "MODEL"),
            
            # MSI models
            (["vector"], "MODEL"),
            (["katana"], "MODEL"),
            (["stealth"], "MODEL"),
            (["raider"], "MODEL"),
        ]
        
        for words, label in model_series:
            patterns.append({
                "label": label,
                "pattern": [{"LOWER": word} for word in words]
            })
        
        # Processor patterns with context
        patterns.extend([
            {
                "label": "PROCESSOR",
                "pattern": [
                    {"LOWER": {"IN": ["core", "intel"]}},
                    {"TEXT": {"REGEX": r"i[3579]"}},
                ]
            },
            {
                "label": "PROCESSOR",
                "pattern": [
                    {"LOWER": "ultra"},
                    {"TEXT": {"REGEX": r"[579]"}},
                ]
            },
            {
                "label": "PROCESSOR",
                "pattern": [
                    {"LOWER": {"IN": ["amd", "ryzen"]}},
                    {"TEXT": {"REGEX": r"[3579]"}},
                ]
            },
        ])
        
        # GPU patterns with context
        patterns.extend([
            {
                "label": "GPU",
                "pattern": [
                    {"TEXT": {"REGEX": r"(?i)rtx|gtx"}},
                    {"TEXT": {"REGEX": r"\d{4}"}},
                ]
            },
            {
                "label": "GPU",
                "pattern": [
                    {"LOWER": "radeon"},
                    {"TEXT": {"REGEX": r"\d{4}"}},
                ]
            },
        ])
        
        # Workstation indicator
        patterns.append({
            "label": "CATEGORY",
            "pattern": [{"LOWER": "workstation"}]
        })
        
        # Gaming indicator
        patterns.append({
            "label": "CATEGORY",
            "pattern": [{"LOWER": "gaming"}]
        })
        
        return patterns
    
    def _extract_with_regex(self, cleaned_text: str, original_text: str) -> Dict:
        """Extract structured fields using regex patterns"""
        result = {}
        
        # Price extraction
        price_match = self.regex_patterns['price_labeled'].search(cleaned_text)
        if not price_match:
            price_match = self.regex_patterns['price'].search(cleaned_text)
        if not price_match:
            price_match = self.regex_patterns['price_simple'].search(cleaned_text)

        if price_match:
            price_str = price_match.group(1).replace(',', '')
            try:
                result['price'] = int(price_str)
                result['currency'] = 'Birr'
            except ValueError:
                result['price'] = None
                result['currency'] = None
        else:
            result['price'] = None
            result['currency'] = None
        
        # Phone numbers extraction (find all)
        phone_matches = self.regex_patterns['phone'].findall(original_text)
        phones = []
        for match in phone_matches:
            # match is tuple (prefix, number)
            prefix = match[0] if match[0] else '0'
            number = match[1]
            # Normalize to Ethiopian format
            if prefix.startswith('+251'):
                phones.append(f'+251{number}')
            elif prefix == '0':
                phones.append(f'0{number}')
            else:
                phones.append(f'0{number}')
        result['contact_numbers'] = list(set(phones))  # Remove duplicates
        
        # RAM extraction - look for explicit RAM mentions
        ram_match = self.regex_patterns['ram'].search(cleaned_text)
        if ram_match:
            ram_size = ram_match.group(1)
            ram_speed = ram_match.group(2) if ram_match.lastindex >= 2 else None
            
            # Try to find DDR type in surrounding context (within 20 chars)
            match_pos = ram_match.start()
            context_start = max(0, match_pos - 10)
            context_end = min(len(cleaned_text), match_pos + 50)
            context = cleaned_text[context_start:context_end]
            
            ddr_match = re.search(r'(DDR[345])', context, re.IGNORECASE)
            ddr_type = ddr_match.group(1).upper() if ddr_match else None
            
            # Look for speed if not already found
            if not ram_speed:
                speed_match = re.search(rf'{ram_size}\s*GB.*?(\d{{4}})\s*(?:MHZ|mhz|MHz)', context, re.IGNORECASE)
                ram_speed = speed_match.group(1) if speed_match else None
            
            # Build RAM string
            ram_parts = [f"{ram_size}GB"]
            if ddr_type:
                ram_parts.append(ddr_type)
            if ram_speed:
                ram_parts.append(f"{ram_speed}MHz")
            
            result['ram'] = ' '.join(ram_parts)
        else:
            result['ram'] = None
        
        # Storage extraction - prioritize explicit storage mentions
        storage_matches = list(self.regex_patterns['storage'].finditer(cleaned_text))
        if storage_matches:
            # Take the first match that looks like storage (not RAM or GPU memory)
            storage_match = None
            for match in storage_matches:
                match_text = match.group(0).upper()
                # Explicit SSD/HDD/NVMe in the match is always storage
                if any(k in match_text for k in ("SSD", "HDD", "NVME", "PCIE")):
                    storage_match = match
                    break
                # Otherwise skip if RAM/VRAM appears in the immediate match text
                if re.search(r'\b(ram|vram|graphics)\b', match.group(0), re.IGNORECASE):
                    continue
                storage_match = match
                break
            
            if storage_match:
                storage_size = storage_match.group(1)
                # Determine if TB or GB
                if 'TB' in storage_match.group(0).upper():
                    storage_unit = 'TB'
                else:
                    storage_unit = 'GB'
                
                # Check for SSD/HDD/NVMe
                storage_type = None
                if 'NVME' in storage_match.group(0).upper():
                    storage_type = 'NVMe SSD'
                elif 'SSD' in storage_match.group(0).upper():
                    storage_type = 'SSD'
                elif 'HDD' in storage_match.group(0).upper():
                    storage_type = 'HDD'
                
                storage_parts = [f"{storage_size}{storage_unit}"]
                if storage_type:
                    storage_parts.append(storage_type)
                
                result['storage'] = ' '.join(storage_parts)
            else:
                result['storage'] = None
        else:
            result['storage'] = None
        
        # Screen size extraction
        screen_match = self.regex_patterns['screen_size'].search(cleaned_text)
        result['screen_size'] = f"{screen_match.group(1)} inch" if screen_match else None
        
        # Resolution extraction
        resolution_match = self.regex_patterns['resolution'].search(cleaned_text)
        if resolution_match:
            groups = resolution_match.groups()
            if groups[0] and groups[1]:  # Numeric format
                result['resolution'] = f"{groups[0]}x{groups[1]}"
            elif groups[2]:  # FHD
                result['resolution'] = "FHD (1920x1080)"
            elif groups[3]:  # 2K
                result['resolution'] = "2K (2560x1440)"
            elif groups[4]:  # 4K
                result['resolution'] = "4K (3840x2160)"
            else:
                result['resolution'] = None
        else:
            result['resolution'] = None
        
        # Refresh rate extraction
        refresh_match = self.regex_patterns['refresh_rate'].search(cleaned_text)
        result['refresh_rate'] = f"{refresh_match.group(1)}Hz" if refresh_match else None
        
        # Generation extraction
        gen_match = self.regex_patterns['generation'].search(cleaned_text)
        if gen_match:
            gen_num = gen_match.group(1)
            result['generation'] = f"{gen_num}th Gen"
        else:
            result['generation'] = None
        
        # Processor extraction
        processor = None
        intel_match = self.regex_patterns['processor_intel'].search(cleaned_text)
        if intel_match:
            proc_type = intel_match.group(1)  # i5, i7, i9, Ultra 7, etc.
            proc_model = intel_match.group(2) if intel_match.lastindex >= 2 else None
            
            if 'ultra' in proc_type.lower():
                processor = f"Intel Core {proc_type}"
            else:
                processor = f"Intel Core {proc_type}"
            
            if proc_model:
                processor += f"-{proc_model}"
        else:
            amd_match = self.regex_patterns['processor_amd'].search(cleaned_text)
            if amd_match:
                proc_series = amd_match.group(1)  # 5, 7, 9
                proc_model = amd_match.group(2) if amd_match.lastindex >= 2 else None
                
                processor = f"AMD Ryzen {proc_series}"
                if proc_model:
                    processor += f" {proc_model}"
        
        result['processor'] = processor
        
        # Graphics card extraction
        gpu = None
        gpu_memory = None
        
        nvidia_match = self.regex_patterns['gpu_nvidia'].search(cleaned_text)
        if nvidia_match:
            gpu_series = nvidia_match.group(1).upper()  # RTX, GTX, MX
            gpu_model = nvidia_match.group(2)
            
            # Check for Ti variant
            ti_match = re.search(rf'{gpu_series}\s*{gpu_model}\s*Ti', cleaned_text, re.IGNORECASE)
            
            gpu = f"NVIDIA GeForce {gpu_series} {gpu_model}"
            if ti_match:
                gpu += " Ti"
            
            # Try to find GPU memory near the GPU mention (within 100 chars)
            gpu_pos = nvidia_match.start()
            context_start = max(0, gpu_pos - 50)
            context_end = min(len(cleaned_text), gpu_pos + 100)
            gpu_context = cleaned_text[context_start:context_end]
            
            gpu_mem_match = self.regex_patterns['gpu_memory'].search(gpu_context)
            if gpu_mem_match:
                mem_size = gpu_mem_match.group(1)
                # Only accept reasonable GPU memory sizes (2-24GB typically)
                if int(mem_size) <= 24:
                    gpu_memory = f"{mem_size}GB"
                    # Check for GDDR type
                    if 'GDDR6' in gpu_mem_match.group(0).upper():
                        gpu_memory += " GDDR6"
                    elif 'GDDR5' in gpu_mem_match.group(0).upper():
                        gpu_memory += " GDDR5"
        else:
            amd_gpu_match = self.regex_patterns['gpu_amd'].search(cleaned_text)
            if amd_gpu_match:
                gpu_model = amd_gpu_match.group(2)
                gpu = f"AMD Radeon RX {gpu_model}"
            else:
                intel_gpu_match = self.regex_patterns['gpu_intel'].search(cleaned_text)
                if intel_gpu_match:
                    gpu = intel_gpu_match.group(0).strip()
                    gpu = re.sub(r'\s+', ' ', gpu, flags=re.IGNORECASE)
                    if not gpu.lower().startswith('intel'):
                        gpu = f"Intel {gpu}"

        result['graphics_card'] = gpu
        result['graphics_memory'] = gpu_memory
        
        # Battery life extraction
        battery_match = self.regex_patterns['battery'].search(cleaned_text)
        result['battery_life'] = f"{battery_match.group(1)} hours" if battery_match else None
        
        # Condition extraction
        condition_match = self.regex_patterns['condition'].search(original_text)
        result['condition'] = condition_match.group(0) if condition_match else None
        
        # URLs extraction
        urls = []
        telegram_urls = self.regex_patterns['telegram_url'].findall(original_text)
        urls.extend(telegram_urls)
        
        telegram_handles = self.regex_patterns['telegram_handle'].findall(original_text)
        urls.extend([f"https://t.me/{handle[1:]}" for handle in telegram_handles])
        
        result['urls'] = list(set(urls))  # Remove duplicates
        
        return result
    
    def _extract_with_spacy(self, cleaned_text: str) -> Dict:
        """Extract entities using spaCy NER"""
        doc = self.nlp(cleaned_text)
        
        result = {
            'brands': [],
            'models': [],
            'processors': [],
            'gpus': [],
            'categories': []
        }
        
        for ent in doc.ents:
            if ent.label_ == "BRAND":
                result['brands'].append(ent.text)
            elif ent.label_ == "MODEL":
                result['models'].append(ent.text)
            elif ent.label_ == "PROCESSOR":
                result['processors'].append(ent.text)
            elif ent.label_ == "GPU":
                result['gpus'].append(ent.text)
            elif ent.label_ == "CATEGORY":
                result['categories'].append(ent.text)
        
        return result
    
    def _merge_results(self, regex_result: Dict, spacy_result: Dict) -> Dict:
        """Merge regex and spaCy results intelligently"""
        merged = regex_result.copy()
        
        # Build title from brand + model
        title_parts = []
        if spacy_result['brands']:
            title_parts.append(spacy_result['brands'][0].title())
        if spacy_result['models']:
            title_parts.append(spacy_result['models'][0].title())
        
        # If we have processor info, add it to title
        if merged.get('processor'):
            # Extract just the core part (i5, i7, Ryzen 7, etc.)
            proc_short = re.search(r'(i[3579]|Ryzen\s*[3579]|Ultra\s*[579])', 
                                   merged['processor'], re.IGNORECASE)
            if proc_short and proc_short.group(1) not in ' '.join(title_parts):
                title_parts.append(proc_short.group(1))
        
        merged['title'] = ' '.join(title_parts) if title_parts else None
        
        # Model field
        merged['model'] = spacy_result['models'][0] if spacy_result['models'] else None
        
        # If title is still empty, create a fallback
        if not merged['title']:
            if merged.get('processor'):
                merged['title'] = f"Laptop with {merged['processor']}"
            elif merged.get('graphics_card'):
                merged['title'] = f"Laptop with {merged['graphics_card']}"
            else:
                merged['title'] = "Laptop Deal"
        
        return merged
    
    def _normalize_result(self, result: Dict, original_text: str) -> Dict:
        """Final normalization and addition of computed fields"""
        # Ensure all expected fields exist
        fields = [
            'title', 'model', 'processor', 'generation', 'ram', 'storage',
            'screen_size', 'resolution', 'graphics_card', 'graphics_memory',
            'battery_life', 'condition', 'price', 'currency', 'contact_numbers',
            'urls', 'raw_message', 'timestamp'
        ]
        
        normalized = {field: result.get(field) for field in fields}
        
        # Add raw message and timestamp
        normalized['raw_message'] = original_text
        normalized['timestamp'] = datetime.utcnow()
        
        # Add image_path placeholder (will be filled by listener)
        normalized['image_path'] = None
        
        # Add categories using existing categorizer
        normalized['categories'] = categorize_deal(normalized)
        
        # Add scores using existing scorer
        general_score, category_scores = score_deal(normalized)
        normalized['general_score'] = general_score
        normalized['category_scores'] = category_scores
        
        return normalized
    
    def _empty_result(self, raw_text: str) -> Dict:
        """Return empty result structure"""
        return {
            'title': None,
            'model': None,
            'processor': None,
            'generation': None,
            'ram': None,
            'storage': None,
            'screen_size': None,
            'resolution': None,
            'graphics_card': None,
            'graphics_memory': None,
            'battery_life': None,
            'condition': None,
            'price': None,
            'currency': None,
            'contact_numbers': [],
            'urls': [],
            'raw_message': raw_text,
            'timestamp': datetime.utcnow(),
            'image_path': None,
            'categories': [],
            'general_score': 0,
            'category_scores': {}
        }
