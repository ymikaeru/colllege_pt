import json
import os
import glob

def restore_all_missing_jp():
    # Configuration
    # We focus on the theme "宗教断片集" based on the analysis
    bkp_dir = 'data/temasSeparados/bkp'
    target_path = 'data/shin_college_data.json'
    
    # Pattern to match the source part files for this theme
    # Analysis showed missing items in "宗教断片集" which matches these files
    source_pattern = os.path.join(bkp_dir, '04_4.その他_04_宗教断片集_parte*.json')
    source_files = glob.glob(source_pattern)
    
    if not source_files:
        print("No backup files found matching the pattern!")
        return

    print(f"Found {len(source_files)} backup files.")
    
    print(f"Loading target: {target_path}")
    with open(target_path, 'r', encoding='utf-8') as f:
        target_data = json.load(f)

    # Helper to find target theme
    target_theme = None
    
    # We look for Volume 4, Theme '宗教断片集'
    # Note: Volume name in JSON is "4.その他" usually.
    for vol in target_data:
        if "4.その他" in vol['volume'] or "Outros" in vol['volume']:
            for theme in vol['themes']:
                if theme['theme'] == '宗教断片集':
                    target_theme = theme
                    break
        if target_theme: break
    
    if not target_theme:
        print("Target theme '宗教断片集' not found in database!")
        return

    total_updates = 0

    # Process each source file
    for source_file in sorted(source_files):
        # Skip files that end in _pt.json or merged.json just in case glob is loose (though pattern is specific)
        if '_pt.json' in source_file or '_merged.json' in source_file: 
            continue
            
        # print(f"Processing {os.path.basename(source_file)}...")
        
        with open(source_file, 'r', encoding='utf-8') as f:
            source_data = json.load(f)
            
        # Iterate through publications in source
        for src_pub in source_data.get('publications', []):
            src_content = src_pub.get('content', '')
            if not src_content or src_content.strip() == "":
                continue # Nothing to restore from here
            
            src_title_string = src_pub.get('title', '')
            src_pub_title = src_pub.get('publication_title', '')

            # Find matching Title in Target
            target_title_group = None
            for t_group in target_theme['titles']:
                if t_group['title'] == src_title_string:
                    target_title_group = t_group
                    break
            
            if not target_title_group:
                # print(f"  [Skipped] Title '{src_title_string}' not found in target.")
                continue

            # Find matching Publication in Target
            found_target_pub = None
            for tgt_pub in target_title_group['publications']:
                 if tgt_pub.get('publication_title', '').strip() == src_pub_title.strip():
                    found_target_pub = tgt_pub
                    break
            
            if found_target_pub:
                # Check if target is missing content
                current_content = found_target_pub.get('content', '')
                if not current_content or current_content.strip() == "":
                    found_target_pub['content'] = src_content
                    # print(f"  [Restored] {src_pub_title[:30]}...")
                    total_updates += 1
                elif len(current_content) < len(src_content) * 0.5:
                     # Heuristic: If existing content is drastically shorter, maybe it's broken? 
                     # For now, let's strictly trust "empty" check to be safe.
                     pass

    print("-" * 50)
    print(f"Restoration complete. Total entries updated: {total_updates}")
    
    if total_updates > 0:
        with open(target_path, 'w', encoding='utf-8') as f:
            json.dump(target_data, f, ensure_ascii=False, indent=2)
        print("Saved updated shin_college_data.json")

if __name__ == "__main__":
    restore_all_missing_jp()
