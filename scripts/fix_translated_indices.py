#!/usr/bin/env python3
"""
Script to fix translated JSON files by restoring the pub_idx field.
Uses publication_title_ptbr content matching to correlate with original publication_title.
"""

import json
import os
from pathlib import Path

PARTS_DIR = Path("/Users/michael/Documents/Ensinamentos/Sites/ShinCollege_Pt/data/temasSeparados/partes")
TRANSLATED_DIR = PARTS_DIR / "Translated"

def load_json(filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        return json.load(f)

def save_json(filepath, data):
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def fix_translated_file(translated_file):
    """Restore pub_idx from original file to translated file using title matching."""
    
    # Get corresponding original filename
    original_name = translated_file.name.replace('_pt.json', '.json')
    original_path = PARTS_DIR / original_name
    
    if not original_path.exists():
        print(f"  ⚠ Original not found: {original_name}")
        return 0, 0
    
    original = load_json(original_path)
    translated = load_json(translated_file)
    
    orig_pubs = original.get('publications', [])
    trans_pubs = translated.get('publications', [])
    
    # Build lookup by position (original order)
    # The key insight: translations should be in the same order as originals
    fixed_count = 0
    skipped_count = 0
    
    # Strategy 1: If counts match, use position-based matching
    if len(orig_pubs) == len(trans_pubs):
        for i, (orig_pub, trans_pub) in enumerate(zip(orig_pubs, trans_pubs)):
            if 'pub_idx' not in trans_pub:
                trans_pub['pub_idx'] = orig_pub.get('pub_idx', i)
                trans_pub['title_idx'] = orig_pub.get('title_idx')
                fixed_count += 1
    else:
        # Strategy 2: If counts don't match, translate what we can by position
        # and mark which ones are missing
        print(f"  ℹ Counts differ: {len(orig_pubs)} original vs {len(trans_pubs)} translated")
        
        # Assume translations are in order but may be incomplete
        # Match by position up to the translated count
        trans_idx = 0
        for orig_idx, orig_pub in enumerate(orig_pubs):
            if trans_idx >= len(trans_pubs):
                break
            
            trans_pub = trans_pubs[trans_idx]
            
            # Check if this translation seems to match (same title_idx at least)
            if trans_pub.get('title_idx') == orig_pub.get('title_idx') or trans_pub.get('title_idx') is None:
                if 'pub_idx' not in trans_pub:
                    trans_pub['pub_idx'] = orig_pub.get('pub_idx', orig_idx)
                    trans_pub['title_idx'] = orig_pub.get('title_idx')
                    fixed_count += 1
                trans_idx += 1
            else:
                # title_idx mismatch - the original was likely skipped
                skipped_count += 1
        
        # Mark remaining as skipped
        skipped_count += len(orig_pubs) - (trans_idx + skipped_count)
    
    # Save fixed translation
    save_json(translated_file, translated)
    return fixed_count, skipped_count

def main():
    theme_prefix = "03_3.信仰編_09_御神体とお光"
    
    translated_files = sorted([
        f for f in TRANSLATED_DIR.iterdir()
        if f.name.startswith(theme_prefix) and f.name.endswith('_pt.json')
    ])
    
    print(f"Found {len(translated_files)} translated files to process")
    print()
    
    total_fixed = 0
    total_skipped = 0
    
    for trans_file in translated_files:
        print(f"Processing {trans_file.name}...")
        fixed, skipped = fix_translated_file(trans_file)
        total_fixed += fixed
        total_skipped += skipped
        if fixed > 0:
            print(f"  ✓ Fixed {fixed} publications")
        if skipped > 0:
            print(f"  ⚠ Skipped {skipped} publications (not translated)")
    
    print()
    print(f"=== Summary ===")
    print(f"Total publications fixed: {total_fixed}")
    print(f"Total publications skipped/missing: {total_skipped}")

if __name__ == "__main__":
    main()
