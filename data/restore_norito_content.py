import json
import os

def restore_content():
    source_path = 'data/temasSeparados/bkp/04_4.その他_04_宗教断片集_parte01.json'
    target_path = 'data/shin_college_data.json'

    print(f"Loading source: {source_path}")
    with open(source_path, 'r', encoding='utf-8') as f:
        source_data = json.load(f)

    print(f"Loading target: {target_path}")
    with open(target_path, 'r', encoding='utf-8') as f:
        target_data = json.load(f)

    # Source structure: { ..., "publications": [ { "title": "...", "content": "...", ... } ] }
    # Target structure: [ { "volume": "...", "themes": [ { "theme": "...", "titles": [ { "title": "...", "publications": [...] } ] } ] } ]

    # Locate the theme in target
    target_theme = None
    target_vol = None
    
    # We look for Volume 4, Theme '宗教断片集'
    for vol in target_data:
        if "4.その他" in vol['volume'] or "Outros" in vol['volume']: # Check both just in case
            for theme in vol['themes']:
                if theme['theme'] == '宗教断片集':
                    target_theme = theme
                    target_vol = vol
                    break
        if target_theme: break
    
    if not target_theme:
        print("Target theme '宗教断片集' not found!")
        return

    print("Found target theme.")
    
    updates_count = 0
    
    # Iterate through source publications
    for src_pub in source_data['publications']:
        src_title_text = src_pub['title']
        src_content = src_pub.get('content', '')
        src_pub_title = src_pub.get('publication_title', '')
        
        if not src_content:
            continue

        # Find matching Title group in target theme
        # We match by 'title' string
        
        target_title_group = None
        for t_group in target_theme['titles']:
            if t_group['title'] == src_title_text:
                target_title_group = t_group
                break
        
        if not target_title_group:
            print(f"Warning: Title group '{src_title_text}' not found in target. Skipping.")
            continue
            
        # Find matching Publication in target title group
        # We can match by publication_title OR by relative index if unique?
        # Let's try matching by publication_title first.
        
        found_target_pub = None
        for tgt_pub in target_title_group['publications']:
            # Normalize titles (strip) just in case
            if tgt_pub.get('publication_title', '').strip() == src_pub_title.strip():
                found_target_pub = tgt_pub
                break
        
        if found_target_pub:
            # Check if target content is empty
            if not found_target_pub.get('content') or found_target_pub.get('content').strip() == "":
                found_target_pub['content'] = src_content
                # print(f"Restored content for: {src_title_text} - {src_pub_title[:20]}...")
                updates_count += 1
            else:
                # print(f"Target already has content for: {src_title_text} - {src_pub_title[:20]}...")
                pass
        else:
             print(f"Warning: Publication '{src_pub_title}' not found in target group '{src_title_text}'.")

    print(f"Total entries updated: {updates_count}")

    if updates_count > 0:
        with open(target_path, 'w', encoding='utf-8') as f:
            json.dump(target_data, f, ensure_ascii=False, indent=2)
        print("Saved updated shin_college_data.json")
    else:
        print("No updates needed.")

if __name__ == "__main__":
    restore_content()
