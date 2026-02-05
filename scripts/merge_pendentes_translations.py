#!/usr/bin/env python3
"""
Script to merge translated pending publications into the main database.
Reads from pendentes_translated.json and updates shin_college_data_translated.json
"""

import json
from pathlib import Path

DATA_DIR = Path("/Users/michael/Documents/Ensinamentos/Sites/ShinCollege_Pt/data")
MAIN_FILE = DATA_DIR / "shin_college_data_translated.json"
PENDENTES_FILE = DATA_DIR / "temasSeparados/partes/03_3.信仰編_09_御神体とお光_pendentes_translated.json"

def load_json(filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        return json.load(f)

def save_json(filepath, data):
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def main():
    print(f"Loading main database: {MAIN_FILE}")
    main_data = load_json(MAIN_FILE)
    
    print(f"Loading pending translations: {PENDENTES_FILE}")
    pendentes = load_json(PENDENTES_FILE)
    
    # Build translation lookup by (title_idx, pub_idx)
    translations = {}
    for pub in pendentes.get('publications', []):
        key = (pub['title_idx'], pub['pub_idx'])
        translations[key] = pub
    
    print(f"Found {len(translations)} translations to merge")
    
    # Find the theme in main data
    updated_count = 0
    for vol in main_data:
        if '信仰' in vol.get('volume', ''):
            for theme in vol.get('themes', []):
                if theme.get('theme') == '御神体とお光':
                    print(f"Found theme '御神体とお光' in volume '{vol.get('volume')}'")
                    
                    for title_idx, title in enumerate(theme.get('titles', [])):
                        for pub_idx, pub in enumerate(title.get('publications', [])):
                            key = (title_idx, pub_idx)
                            if key in translations:
                                trans = translations[key]
                                # Update publication with translation
                                pub['has_translation'] = True
                                if 'title_ptbr' in trans:
                                    pub['title_ptbr'] = trans['title_ptbr']
                                if 'publication_title_ptbr' in trans:
                                    pub['publication_title_ptbr'] = trans['publication_title_ptbr']
                                if 'content_ptbr' in trans:
                                    pub['content_ptbr'] = trans['content_ptbr']
                                updated_count += 1
    
    print(f"Updated {updated_count} publications")
    
    # Count total translations now
    total_pubs = 0
    translated_pubs = 0
    for vol in main_data:
        if '信仰' in vol.get('volume', ''):
            for theme in vol.get('themes', []):
                if theme.get('theme') == '御神体とお光':
                    for title in theme.get('titles', []):
                        for pub in title.get('publications', []):
                            total_pubs += 1
                            if pub.get('has_translation'):
                                translated_pubs += 1
    
    print(f"\nFinal status for '御神体とお光':")
    print(f"  Total publications: {total_pubs}")
    print(f"  Translated: {translated_pubs}")
    print(f"  Missing: {total_pubs - translated_pubs}")
    print(f"  Coverage: {translated_pubs/total_pubs*100:.1f}%")
    
    # Save
    print(f"\nSaving to {MAIN_FILE}...")
    save_json(MAIN_FILE, main_data)
    print("Done!")

if __name__ == "__main__":
    main()
