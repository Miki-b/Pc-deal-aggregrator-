"""Quick test: parse a sample Telegram deal message."""
import json
from app.parsers.hybrid_parser import HybridParser

SAMPLE = """New arrival today

Brand New   Hp pavilion laptop 

16GB Ram  DDR4

 1TB SSD  super storage 

13th Generation  (2025)

   Core i5

  12core and 16 logical processor

   finger printer 

 with keyboard light
      
 Model   : Hp pavilion 

   Condition: Brand  new  13th generation

 Screen :15.6  inch 

 With intel Iris Graphics card 

 10 hours battery life 

Price :  85,500

    @sww2844

   0928442662
0940141114
 
https://t.me/samcomptech"""


def main() -> None:
    result = HybridParser().parse(SAMPLE)
    print(json.dumps(
        {k: v for k, v in result.items() if k not in ("raw_message", "timestamp", "category_scores")},
        indent=2,
        default=str,
    ))


if __name__ == "__main__":
    main()
