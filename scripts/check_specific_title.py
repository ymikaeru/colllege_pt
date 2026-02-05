import json

def main():
    with open('data/shin_college_data.json', 'r', encoding='utf-8') as f:
        data = json.load(f)

    # Looking for Volume 2 (index 1?) data[1]
    # Theme "自然農法" (Nature Farming)
    
    target_vol_idx = 1 # Volume 2
    
    if len(data) <= target_vol_idx:
        print("Volume 2 not found")
        return

    volume = data[target_vol_idx]
    print(f"Volume: {volume.get('volume')}")

    for theme in volume.get('themes', []):
        if "自然農法" in theme.get('theme', ''):
            print(f"Theme: {theme.get('theme')} / {theme.get('theme_ptbr')}")
            for title in theme.get('titles', []):
                pubs = title.get('publications', [])
                if not pubs: continue
                
                translated_count = 0
                for pub in pubs:
                    content = pub.get('content_ptbr', '')
                    if content and len(content.strip()) > 0:
                        translated_count += 1
                
                is_fully_translated = (translated_count == len(pubs))
                print(f"  Title: {title.get('title')} / {title.get('title_ptbr')}")
                print(f"    Total Pubs: {len(pubs)}, Translated: {translated_count}")
                print(f"    Strict Check Pass: {is_fully_translated}")
                if not is_fully_translated and translated_count > 0:
                     print("    -> PARTIALLY TRANSLATED")
                print("-")

if __name__ == "__main__":
    main()
