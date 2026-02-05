#!/usr/bin/env python3
"""
Script to merge Portuguese translations from part files into shin_college_data_translated.json.
Specifically for the theme 御神体とお光 (Goshintai to Ohikari).
"""

import json
import os
from pathlib import Path

# Paths
DATA_DIR = Path(__file__).parent.parent / "data"
PARTS_DIR = DATA_DIR / "temasSeparados" / "partes"
TARGET_FILE = DATA_DIR / "shin_college_data_translated.json"

def load_json(filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        return json.load(f)

def save_json(filepath, data):
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def main():
    # Load the main translated data
    print(f"Loading {TARGET_FILE}...")
    main_data = load_json(TARGET_FILE)
    
    # Find all part files for 御神体とお光 in the Translated folder
    theme_prefix = "03_3.信仰編_09_御神体とお光"
    translated_dir = PARTS_DIR / "Translated"
    part_files = sorted([
        f for f in translated_dir.iterdir()
        if f.name.startswith(theme_prefix) and f.name.endswith("_pt.json")
    ], key=lambda x: int(x.stem.split("parte")[1].split("_")[0]))
    
    print(f"Found {len(part_files)} translation part files")
    
    # Build a mapping of translations from part files
    # Key: (title_idx, pub_idx) -> translation data
    translations = {}
    
    for part_file in part_files:
        print(f"Processing {part_file.name}...")
        part_data = load_json(part_file)
        
        for pub in part_data.get("publications", []):
            title_idx = pub.get("title_idx")
            pub_idx = pub.get("pub_idx", 0)
            
            if title_idx is not None and pub.get("has_translation"):
                key = (title_idx, pub_idx)
                translations[key] = {
                    "title_ptbr": pub.get("title_ptbr"),
                    "publication_title_ptbr": pub.get("publication_title_ptbr"),
                    "content_ptbr": pub.get("content_ptbr"),
                    "has_translation": True
                }
    
    print(f"Collected {len(translations)} translations")
    
    # Find the theme in main_data and update
    # Structure: main_data is a list of volumes: [{"volume": "...", "themes": [...]}]
    updated_count = 0
    
    for volume in main_data:
        for theme in volume.get("themes", []):
            if theme.get("theme") == "御神体とお光":
                print(f"Found theme '御神体とお光' in volume '{volume.get('volume')}'")
                
                for title_idx, title in enumerate(theme.get("titles", [])):
                    for pub_idx, pub in enumerate(title.get("publications", [])):
                        key = (title_idx, pub_idx)
                        if key in translations:
                            trans = translations[key]
                            pub["has_translation"] = True
                            pub["title_ptbr"] = trans["title_ptbr"]
                            pub["publication_title_ptbr"] = trans["publication_title_ptbr"]
                            pub["content_ptbr"] = trans["content_ptbr"]
                            updated_count += 1
    
    print(f"Updated {updated_count} publications with translations")
    
    # Save the updated data
    print(f"Saving to {TARGET_FILE}...")
    save_json(TARGET_FILE, main_data)
    print("Done!")

if __name__ == "__main__":
    main()
