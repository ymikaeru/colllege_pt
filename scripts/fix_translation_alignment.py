#!/usr/bin/env python3
"""
Fix misaligned Portuguese translations in shin_college_data_translated.json.
Extracts the original Japanese title from (Orig.: ...) in publication_title_ptbr
and re-maps content to the correct publication.
"""

import json
import re
from pathlib import Path

# Paths
SCRIPT_DIR = Path(__file__).parent
BASE_DIR = SCRIPT_DIR.parent
JSON_PATH = BASE_DIR / "data" / "shin_college_data_translated.json"
OUTPUT_PATH = BASE_DIR / "data" / "shin_college_data_fixed.json"

def normalize_text(text):
    """Normalize text for matching."""
    if not text:
        return ""
    text = re.sub(r'[\s　]+', '', text)
    text = text.translate(str.maketrans('０１２３４５６７８９', '0123456789'))
    return text.strip()

def extract_jp_title(pt_title):
    """Extract Japanese title from (Orig.: 日本語タイトル)."""
    if not pt_title:
        return None
    match = re.search(r'\(Orig\.?:\s*([^)]+)\)', pt_title)
    if match:
        return match.group(1).strip()
    return None

def main():
    print(f"Loading JSON from {JSON_PATH}...")
    with open(JSON_PATH, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    # Step 1: Collect all misaligned translations (those with Orig.: in title)
    print("\n=== Collecting misaligned translations ===")
    translations = {}  # normalized JP title -> {pt_title, content_ptbr}
    
    for vol in data:
        for theme in vol.get('themes', []):
            for title_group in theme.get('titles', []):
                for pub in title_group.get('publications', []):
                    pt_title = pub.get('publication_title_ptbr', '')
                    content_ptbr = pub.get('content_ptbr', '')
                    
                    if content_ptbr and pt_title:
                        jp_orig = extract_jp_title(pt_title)
                        if jp_orig:
                            norm_jp = normalize_text(jp_orig)
                            if norm_jp not in translations:
                                translations[norm_jp] = {
                                    'jp_title': jp_orig,
                                    'pt_title': pt_title.split('(Orig.:')[0].strip(),
                                    'content_ptbr': content_ptbr
                                }
                                print(f"  Found: {jp_orig[:30]}...")
    
    print(f"\nTotal translations with Orig.: {len(translations)}")
    
    # Step 2: Clear all misaligned translations and re-map correctly
    print("\n=== Re-mapping translations ===")
    fixes_count = 0
    cleared_count = 0
    matched_count = 0
    
    for vol in data:
        for theme in vol.get('themes', []):
            for title_group in theme.get('titles', []):
                for pub in title_group.get('publications', []):
                    jp_title = pub.get('publication_title', '')
                    norm_jp = normalize_text(jp_title)
                    
                    # Check if current mapping is wrong (has Orig.: that doesn't match)
                    current_pt_title = pub.get('publication_title_ptbr', '')
                    current_orig = extract_jp_title(current_pt_title)
                    
                    if current_orig:
                        # This publication has a translation meant for another title
                        norm_orig = normalize_text(current_orig)
                        if norm_orig != norm_jp:
                            # Clear misaligned translation
                            pub['publication_title_ptbr'] = ''
                            pub['content_ptbr'] = ''
                            cleared_count += 1
                    
                    # Now check if we have a translation for THIS publication
                    if norm_jp in translations:
                        trans = translations[norm_jp]
                        pub['publication_title_ptbr'] = trans['pt_title']
                        pub['content_ptbr'] = trans['content_ptbr']
                        matched_count += 1
                        print(f"  Matched: {jp_title[:30]}... -> {trans['pt_title'][:30]}...")
                        fixes_count += 1
    
    print(f"\n=== Summary ===")
    print(f"Cleared misaligned: {cleared_count}")
    print(f"Correctly matched: {matched_count}")
    print(f"Total fixes: {fixes_count}")
    
    # Step 3: Count final stats
    total_pubs = 0
    with_ptbr = 0
    for vol in data:
        for theme in vol.get('themes', []):
            for title_group in theme.get('titles', []):
                for pub in title_group.get('publications', []):
                    total_pubs += 1
                    if pub.get('content_ptbr'):
                        with_ptbr += 1
    
    print(f"\nFinal stats: {with_ptbr}/{total_pubs} publications with Portuguese ({with_ptbr/total_pubs*100:.1f}%)")
    
    # Save to new file first for safety
    print(f"\nSaving fixed JSON to {OUTPUT_PATH}...")
    with open(OUTPUT_PATH, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    print("Done! Review the output file before replacing the original.")

if __name__ == "__main__":
    main()
