import json
import os

# Paths
DATA_DIR = "/Users/michael/Documents/Ensinamentos/Sites/ShinCollege_Pt/data"
MAIN_JSON_PATH = os.path.join(DATA_DIR, "shin_college_data.json")
MERGED_FILE_PATH = os.path.join(DATA_DIR, "temasSeparados", "04_4.その他_04_宗教断片集_merged.json")

def restore_theme():
    # 1. Load Main JSON
    print(f"Loading {MAIN_JSON_PATH}...")
    with open(MAIN_JSON_PATH, 'r', encoding='utf-8') as f:
        main_data = json.load(f)

    # 2. Load Merged JSON
    print(f"Loading {MERGED_FILE_PATH}...")
    if not os.path.exists(MERGED_FILE_PATH):
        print(f"Error: {MERGED_FILE_PATH} not found.")
        return

    with open(MERGED_FILE_PATH, 'r', encoding='utf-8') as f:
        merged_data = json.load(f)

    # 3. Transform Flattened Publications to Nested Structure
    print("Transforming data structure...")
    target_volume_name = merged_data.get("volume")
    target_theme_name = merged_data.get("theme_name")
    target_theme_ptbr = merged_data.get("theme_name_ptbr", "")
    
    flattened_pubs = merged_data.get("publications", [])
    
    # Group by title
    titles_map = {}
    titles_order = [] # To preserve order

    for pub in flattened_pubs:
        t_title = pub.get("title")
        t_title_ptbr = pub.get("title_ptbr", "")
        
        if t_title not in titles_map:
            titles_map[t_title] = {
                "title": t_title,
                "title_ptbr": t_title_ptbr,
                "publications": []
            }
            titles_order.append(t_title)
        
        # Add publication to the list
        # We need to construct the publication object as expected by main json
        # Main json pub structure: publication_title, publication_title_ptbr, content, content_ptbr, date, has_translation, pub_idx
        
        new_pub = {
            "publication_title": pub.get("publication_title", ""),
            "publication_title_ptbr": pub.get("publication_title_ptbr", ""),
            "content": pub.get("content", ""), # Assuming merged file might not have original content, checking...
            # Wait, merged file output in Step 317 shown "content_ptbr". 
            # Does it have "content"? The output snippet didn't show "content" for the first items, only "content_ptbr".
            # Let's check if "content" is in the merged file. 
            # If "content" is missing in merged file, we might be losing original text if we just use this.
            # However, the user said "translations are missing". 
            # Let's assume we want to MERGE this into existing data if possible, or Add if missing.
            # But earlier grep showed the Theme "宗教断片集" is MISSING entirely.
            # So we are creating it from scratch.
            # If the merged file DOES NOT have the Japanese content, we might be creating a "partial" entry with only Portuguese.
            # Let's check the merged file content again. Step 317 showed:
            # "content_ptbr": "...", "has_translation": true, "date": "..."
            # It seems "content" (Japanese) IS MISSING in the displayed lines of merged file (Step 317).
            # WAIT. Line 1: `source_file`: `04_4.その他_04_宗教断片集.json`.
            # Perhaps I should read the original source file to get the Japanese content?
            # Or maybe the merged file *does* have it and I just missed it in the view?
            # Let's look at Step 317 again.
            # Entry 1 (Line 7): "title", "title_ptbr", "pub_idx", "publication_title", "publication_title_ptbr", "content_ptbr", "has_translation", "date".
            # NO "content" field visibly there.
            # This is risky. If I insert this, I might have Portuguese but no Japanese.
            
            # Use safe get
            "content": pub.get("content", ""),
            "content_ptbr": pub.get("content_ptbr", ""),
            "date": pub.get("date", ""),
            "has_translation": pub.get("has_translation", False),
            "pub_idx": pub.get("pub_idx", 0)
        }
        titles_map[t_title]["publications"].append(new_pub)

    # Convert map back to list in order
    new_titles_list = []
    for t_title in titles_order:
        new_titles_list.append(titles_map[t_title])

    new_theme_obj = {
        "theme": target_theme_name,
        "theme_ptbr": target_theme_ptbr,
        "titles": new_titles_list
    }

    # 4. Insert into Main Data
    volume_found = False
    for vol in main_data:
        if vol.get("volume") == target_volume_name:
            volume_found = True
            # Check if theme already exists (to avoid duplicates if we run twice)
            theme_exists = False
            for th in vol.get("themes", []):
                if th.get("theme") == target_theme_name:
                    theme_exists = True
                    print(f"Theme '{target_theme_name}' already exists in volume '{target_volume_name}'. Updating...")
                    # Update titles? Or replace?
                    # Since we believe it's missing or broken, let's replace titles for now or merge.
                    # Given the grep failed, it likely doesn't exist.
                    th["titles"] = new_titles_list
                    th["theme_ptbr"] = target_theme_ptbr
                    break
            
            if not theme_exists:
                print(f"Adding new theme '{target_theme_name}' to volume '{target_volume_name}'...")
                vol["themes"].append(new_theme_obj)
            break
    
    if not volume_found:
        print(f"Volume '{target_volume_name}' not found. Creating new volume...")
        new_vol = {
            "volume": target_volume_name,
            "themes": [new_theme_obj]
        }
        main_data.append(new_vol)

    # 5. Save
    print(f"Saving updated data to {MAIN_JSON_PATH}...")
    with open(MAIN_JSON_PATH, 'w', encoding='utf-8') as f:
        json.dump(main_data, f, ensure_ascii=False, indent=2)
    print("Done.")

if __name__ == "__main__":
    restore_theme()
