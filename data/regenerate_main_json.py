import json
import glob
import os

DATA_DIR = "/Users/michael/Documents/Ensinamentos/Sites/ShinCollege_Pt/data"
TEMAS_DIR = os.path.join(DATA_DIR, "temasSeparados")
OUTPUT_FILE = os.path.join(DATA_DIR, "shin_college_data.json")

# Volume Translation Map
VOLUME_MAP = {
    "3.信仰編": "3. Seção da Fé",
    "4.その他": "4. Outros",
    "4.その他_04_宗教断片集.json": "4. Outros"
}

def regenerate_main_json():
    print("Regenerating shin_college_data.json from merged files (Bilingual Mode)...")
    
    merged_files = sorted(glob.glob(os.path.join(TEMAS_DIR, "*_merged.json")))
    
    if not merged_files:
        print("No merged files found! Aborting.")
        return

    print(f"Found {len(merged_files)} merged files.")
    
    volumes_map = {}
    
    for file_path in merged_files:
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                merged_data = json.load(f)
            
            raw_vol_name = merged_data.get("volume", "")
            vol_name = VOLUME_MAP.get(raw_vol_name, raw_vol_name)
            
            theme_name = merged_data.get("theme_name")
            theme_name_ptbr = merged_data.get("theme_name_ptbr", "")
            
            if not vol_name or not theme_name:
                continue

            flattened_pubs = merged_data.get("publications", [])
            titles_map = {}
            titles_order = []
            
            for pub in flattened_pubs:
                t_title = pub.get("title")
                
                if t_title not in titles_map:
                    titles_map[t_title] = {
                        "title": t_title, # JP Title
                        "title_ptbr": pub.get("title_ptbr", ""), # PT Title
                        "publications": []
                    }
                    titles_order.append(t_title)
                
                # Keep both languages
                content_jp = pub.get("content", "")
                content_pt = pub.get("content_ptbr", "")
                
                new_pub = {
                    "publication_title": pub.get("publication_title", ""),
                    "publication_title_ptbr": pub.get("publication_title_ptbr", ""),
                    "content": content_jp,        # Japanese
                    "content_ptbr": content_pt,   # Portuguese
                    "date": pub.get("date", ""),
                    "has_translation": bool(content_pt), 
                    "pub_idx": pub.get("pub_idx", 0)
                }
                titles_map[t_title]["publications"].append(new_pub)

            new_titles_list = [titles_map[t] for t in titles_order]
            
            new_theme_obj = {
                "theme": theme_name,
                "theme_ptbr": theme_name_ptbr,
                "titles": new_titles_list
            }

            if vol_name not in volumes_map:
                volumes_map[vol_name] = {
                    "volume": vol_name,
                    "themes": []
                }
            
            volumes_map[vol_name]["themes"].append(new_theme_obj)

        except Exception as e:
            print(f"Error processing {file_path}: {e}")

    final_volumes_list = sorted(volumes_map.values(), key=lambda x: x["volume"])
    
    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
        json.dump(final_volumes_list, f, ensure_ascii=False, indent=2)

    print(f"Successfully regenerated {OUTPUT_FILE} with {len(final_volumes_list)} volumes.")
    
    # Debug stats
    total_pubs = sum(len(t["publications"]) for v in final_volumes_list for th in v["themes"] for t in th["titles"])
    print(f"Total publications: {total_pubs}")


if __name__ == "__main__":
    regenerate_main_json()
