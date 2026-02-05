import json
import os
import shutil
import math

# Configuration
MAIN_JSON = "data/shin_college_data_translated.json"
OUT_DIR = "data/temasSeparados"
PARTES_DIR = os.path.join(OUT_DIR, "partes")
ITEMS_PER_PART = 20

def main():
    print(f"Loading {MAIN_JSON}...")
    try:
        with open(MAIN_JSON, 'r', encoding='utf-8') as f:
            data = json.load(f)
    except Exception as e:
        print(f"Error loading main JSON: {e}")
        return

    # Clean Output Directory
    if os.path.exists(OUT_DIR):
        print(f"Cleaning {OUT_DIR}...")
        shutil.rmtree(OUT_DIR)
    
    os.makedirs(PARTES_DIR, exist_ok=True)
    print(f"Created {PARTES_DIR}")

    total_themes = 0
    total_parts = 0

    # Process each Volume
    for vol_idx, volume in enumerate(data):
        vol_title_raw = volume.get('volume', '')
        # Simple sanitization if needed, but assuming structure is consistent
        
        # Determine Volume Prefix (01, 02...)
        # We assume the order in JSON is the intended order.
        vol_prefix = f"{vol_idx + 1:02d}"
        
        themes = volume.get('themes', [])
        for theme_idx, theme in enumerate(themes):
            theme_title_raw = theme.get('theme', '')
            theme_title_ptbr_raw = theme.get('theme_ptbr', '')
            
            theme_prefix = f"{theme_idx + 1:02d}"
            
            # Construct Filename: 01_1.Volume..._01_Theme...
            base_filename = f"{vol_prefix}_{vol_title_raw}_{theme_prefix}_{theme_title_raw}"
            # Remove potential bad chars for filename if necessary (slashes etc)
            base_filename = base_filename.replace("/", "_").replace("\\", "_")
            
            json_filename = f"{base_filename}.json"
            json_path = os.path.join(OUT_DIR, json_filename)
            
            # Flatten Publications
            flat_items = []
            
            titles = theme.get('titles', [])
            for t_idx, title_group in enumerate(titles):
                t_jp = title_group.get('title', '')
                t_pt = title_group.get('title_ptbr', '')
                
                pubs = title_group.get('publications', [])
                for p_idx, pub in enumerate(pubs):
                    
                    content_jp = pub.get('content', '')
                    content_pt = pub.get('content_ptbr', '')
                    
                    has_trans = False
                    if content_pt and len(content_pt.strip()) > 0:
                        has_trans = True
                    
                    item = {
                        "title_idx": t_idx,
                        "title": t_jp,
                        "title_ptbr": t_pt,
                        "pub_idx": p_idx,
                        "publication_title": pub.get('publication_title', ''),
                        "publication_title_ptbr": pub.get('publication_title_ptbr', ''),
                        "content": content_jp,
                        "content_ptbr": content_pt,
                        "has_translation": has_trans
                    }
                    flat_items.append(item)
            
            # Save Full Theme JSON
            theme_data = {
                "source_file": "shin_college_data_translated.json",
                "volume": vol_title_raw,
                "theme_name": theme_title_raw,
                "theme_name_ptbr": theme_title_ptbr_raw,
                "publications": flat_items
            }
            
            with open(json_path, 'w', encoding='utf-8') as f:
                json.dump(theme_data, f, ensure_ascii=False, indent=2)
            
            total_themes += 1
            
            # Split into Parts
            count_items = len(flat_items)
            if count_items > 0:
                num_parts = math.ceil(count_items / ITEMS_PER_PART)
                
                for i in range(num_parts):
                    start = i * ITEMS_PER_PART
                    end = start + ITEMS_PER_PART
                    chunk = flat_items[start:end]
                    
                    part_num = i + 1
                    part_filename = f"{base_filename}_parte{part_num:02d}.json"
                    part_path = os.path.join(PARTES_DIR, part_filename)
                    
                    part_data = {
                        "source_file": json_filename,
                        "part": part_num,
                        "total_parts": num_parts,
                        "volume": vol_title_raw,
                        "theme_name": theme_title_raw,
                        "theme_name_ptbr": theme_title_ptbr_raw,
                        "publications": chunk
                    }
                    
                    with open(part_path, 'w', encoding='utf-8') as f:
                        json.dump(part_data, f, ensure_ascii=False, indent=2)
                    
                    total_parts += 1

    print(f"Regeneration Complete.")
    print(f"Themes: {total_themes}")
    print(f"Parts: {total_parts}")

if __name__ == "__main__":
    main()
