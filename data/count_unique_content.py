import json

data = json.load(open('data/shin_college_data.json', 'r', encoding='utf-8'))

unique_content = set()
total_pubs = 0
empty_content = 0

for vol in data:
    for theme in vol.get('themes', []):
        for title in theme.get('titles', []):
            for pub in title.get('publications', []):
                total_pubs += 1
                
                content_jp = pub.get('content', '').strip()
                content_pt = pub.get('content_ptbr', '').strip()
                
                key = content_jp if content_jp else content_pt
                
                if key:
                    unique_content.add(key)
                else:
                    empty_content += 1

print(f"Total Publications: {total_pubs}")
print(f"Empty Content: {empty_content}")
print(f"Unique Content Count: {len(unique_content)}")
