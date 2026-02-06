import json

def analyze_missing_jp():
    data_path = 'data/shin_college_data.json'
    
    try:
        with open(data_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
    except FileNotFoundError:
        print(f"Error: File not found at {data_path}")
        return

    missing_count = 0
    details = []

    print("Analyzing for missing Japanese content (where Portuguese content exists)...")
    print("-" * 60)

    for vol in data:
        vol_name = vol.get('volume', 'Unknown Volume')
        for theme in vol.get('themes', []):
            theme_name = theme.get('theme', 'Unknown Theme')
            for title in theme.get('titles', []):
                title_name = title.get('title', 'Unknown Title')
                for pub in title.get('publications', []):
                    # Check if JP content is empty/missing BUT PT content exists
                    jp_content = pub.get('content', '')
                    pt_content = pub.get('content_ptbr', '')
                    
                    if (not jp_content or not jp_content.strip()) and (pt_content and pt_content.strip()):
                        missing_count += 1
                        pub_name = pub.get('publication_title', 'Unknown Publication')
                        details.append(f"Vol: {vol_name} | Theme: {theme_name} | Title: {title_name} | Pub: {pub_name}")

    if missing_count == 0:
        print("No missing Japanese text found! All entries with Portuguese text have Japanese text.")
    else:
        print(f"Found {missing_count} entries with missing Japanese text:")
        for detail in details:
            print(f" - {detail}")
    
    print("-" * 60)
    print(f"Total missing occurrences: {missing_count}")

if __name__ == "__main__":
    analyze_missing_jp()
