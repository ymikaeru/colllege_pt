
import glob
import os
import re
import shutil
import json

# Configuration
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(PROJECT_ROOT, "data")
PARTES_DIR = os.path.join(DATA_DIR, "temasSeparados", "partes")
BKP_DIR = os.path.join(DATA_DIR, "temasSeparados", "bkp_translations")
MAIN_JSON_OUTPUT = os.path.join(DATA_DIR, "shin_college_data.json")

def natural_sort_key(s):
    return [int(text) if text.isdigit() else text.lower()
            for text in re.split('([0-9]+)', s)]

def sync_merged_status():
    """
    Scans all part files. If a file has translations (has_translation=True) 
    and isn't named *_merged.json, rename it.
    """
    print("--- Syncing Merged Status ---")
    part_files = glob.glob(os.path.join(PARTES_DIR, "*.json"))
    
    count = 0
    for p_file in part_files:
        # Skip _pt.json files
        if p_file.endswith("_pt.json"):
            continue
            
        # Skip already merged files
        if p_file.endswith("_merged.json"):
            continue
            
        try:
            with open(p_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # Check if has translation
            has_translation = False
            
            # Check flag or content
            if "publications" in data:
                for pub in data["publications"]:
                    if pub.get("has_translation") or (pub.get("content_ptbr") and len(pub["content_ptbr"].strip()) > 0):
                        has_translation = True
                        break
            
            if has_translation:
                new_name = p_file.replace(".json", "_merged.json")
                os.rename(p_file, new_name)
                # print(f"Renamed {os.path.basename(p_file)} -> {os.path.basename(new_name)}")
                count += 1
                
        except Exception as e:
            print(f"Error checking {os.path.basename(p_file)}: {e}")
            
    print(f"Marked {count} existing files as merged.")

def merge_local_translations():
    """
    Step 1: Merge content from *_pt.json files into their corresponding part files.
    """
    print("--- Step 1: Merging Local Translations ---")
    pt_files = glob.glob(os.path.join(PARTES_DIR, "*_pt.json"))
    
    if not pt_files:
        print("No new translation files (*_pt.json) found.")
    
    merged_count = 0
    for pt_file in pt_files:
        # Target could be .json or _merged.json
        base_name = pt_file.replace("_pt.json", "")
        
        target_file = f"{base_name}_merged.json"
        if not os.path.exists(target_file):
            target_file = f"{base_name}.json"
        
        if not os.path.exists(target_file):
            print(f"Warning: Main file not found for {os.path.basename(pt_file)}")
            continue
            
        try:
            with open(pt_file, 'r', encoding='utf-8') as f:
                pt_data = json.load(f)
                
            with open(target_file, 'r', encoding='utf-8') as f:
                main_data = json.load(f)
                
            updated = False
            
            # Merge theme level data
            if "theme_name_ptbr" in pt_data and main_data.get("theme_name_ptbr") != pt_data["theme_name_ptbr"]:
                main_data["theme_name_ptbr"] = pt_data["theme_name_ptbr"]
                updated = True
                
            # Merge publication level data
            if "publications" in pt_data and "publications" in main_data:
                for i, pt_pub in enumerate(pt_data["publications"]):
                    if i < len(main_data["publications"]):
                        main_pub = main_data["publications"][i]
                        
                        # Update fields and check for changes
                        for field in ["title_ptbr", "publication_title_ptbr", "content_ptbr"]:
                            if field in pt_pub and main_pub.get(field) != pt_pub[field]:
                                main_pub[field] = pt_pub[field]
                                updated = True
                        
                        # Force has_translation if content exists
                        if main_pub.get("content_ptbr"):
                            if not main_pub.get("has_translation"):
                                main_pub["has_translation"] = True
                                updated = True
                            
            # Save updates
            if updated:
                with open(target_file, 'w', encoding='utf-8') as f:
                    json.dump(main_data, f, ensure_ascii=False, indent=2)
                merged_count += 1
            
            # If target wasn't merged yet (didn't have suffix), rename it now
            if not target_file.endswith("_merged.json"):
                new_target = target_file.replace(".json", "_merged.json")
                os.rename(target_file, new_target)
            
            # Move source _pt.json to backup directory
            if not os.path.exists(BKP_DIR):
                os.makedirs(BKP_DIR)
                
            shutil.move(pt_file, os.path.join(BKP_DIR, os.path.basename(pt_file)))
            
        except Exception as e:
            print(f"Error processing {os.path.basename(pt_file)}: {e}")
            
    print(f"Merged translations into {merged_count} files.")


def publish_to_main_json():
    """
    Step 2: Aggregate all part files into shin_college_data.json
    """
    print("\n--- Step 2: Publishing to Main JSON ---")
    part_files = glob.glob(os.path.join(PARTES_DIR, "*.json"))
    
    if not part_files:
        print("No part files found to aggregation.")
        return

    # Structure: volumes_map[vol_name] = { "themes": { theme_name: [list of publications] } }
    files_by_group = {} 
    
    # Filter out _pt.json files from aggregation source (we merged them into main files already)
    # merged files end in _merged.json, original files end in .json. Both are valid content sources.
    valid_parts = [
        p for p in part_files 
        if not p.endswith("_pt.json")
    ]
    
    print(f"Aggregating {len(valid_parts)} files...")

    for p_file in sorted(valid_parts, key=lambda x: natural_sort_key(os.path.basename(x))):
        try:
            with open(p_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                
            vol_name = data.get("volume", "")
            theme_name = data.get("theme_name", "")
            theme_name_ptbr = data.get("theme_name_ptbr", "")
            
            group_key = (vol_name, theme_name)
            
            if group_key not in files_by_group:
                files_by_group[group_key] = {
                    "vol_name": vol_name,
                    "theme_name": theme_name,
                    "theme_name_ptbr": theme_name_ptbr,
                    "parts": []
                }
            
            files_by_group[group_key]["parts"].append(data)
            
        except Exception as e:
            print(f"Error reading {os.path.basename(p_file)}: {e}")

    # Reconstruct
    final_data = []
    
    # Sort groups by volume/theme name natural order
    sorted_groups = sorted(files_by_group.keys(), key=lambda x: natural_sort_key(x[0] + x[1]))
    
    volume_construction = {} 
    
    for vol_name, theme_name in sorted_groups:
        group_data = files_by_group[(vol_name, theme_name)]
        
        if vol_name not in volume_construction:
            volume_construction[vol_name] = {
                "volume": vol_name,
                "themes": []
            }
            
        # Sort parts by 'part' number
        parts = sorted(group_data["parts"], key=lambda x: x.get("part", 0))
        
        merged_publications = []
        for p in parts:
            merged_publications.extend(p.get("publications", []))
            
        # Regroup by title
        grouped_titles = []
        current_title_group = None
        last_title_jp = None
        
        for pub in merged_publications:
            this_title_jp = pub.get("title", "")
            this_title_pt = pub.get("title_ptbr", "")
            
            if this_title_jp != last_title_jp:
                if current_title_group:
                    grouped_titles.append(current_title_group)
                
                current_title_group = {
                    "title": this_title_jp,
                    "title_ptbr": this_title_pt,
                    "publications": []
                }
                last_title_jp = this_title_jp
            
            # Minimal necessary fields for main JSON
            pub_entry = {
                "publication_title": pub.get("publication_title", ""),
                "publication_title_ptbr": pub.get("publication_title_ptbr", ""),
                "content": pub.get("content", ""),
                "content_ptbr": pub.get("content_ptbr", ""),
                "date": pub.get("date", ""),
                "has_translation": pub.get("has_translation", False)
            }
            # Optional fields
            for k in ["pub_idx", "source", "header", "type"]:
                if k in pub: pub_entry[k] = pub[k]
            
            current_title_group["publications"].append(pub_entry)

        if current_title_group:
            grouped_titles.append(current_title_group)

        theme_entry = {
            "theme": theme_name,
            "theme_ptbr": group_data["theme_name_ptbr"],
            "titles": grouped_titles
        }
        
        volume_construction[vol_name]["themes"].append(theme_entry)

    # Final list sorted by volume
    sorted_vols = sorted(volume_construction.keys(), key=natural_sort_key)
    for v_key in sorted_vols:
        final_data.append(volume_construction[v_key])

    print(f"Writing {len(final_data)} volumes to {MAIN_JSON_OUTPUT}...")
    with open(MAIN_JSON_OUTPUT, 'w', encoding='utf-8') as f:
        json.dump(final_data, f, ensure_ascii=False, indent=2)


def main():
    print("Starting Translation Deployment Pipeline...")
    sync_merged_status() # Check existing files first
    merge_local_translations()
    publish_to_main_json()
    print("\nDeployment Complete! Site data updated.")

if __name__ == "__main__":
    main()
