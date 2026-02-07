import os
import json
import glob
import re

DATA_DIR = "data"
TEMAS_DIR = os.path.join(DATA_DIR, "temasSeparados")
BKP_DIR = os.path.join(TEMAS_DIR, "bkp") 

# Find all unique themes
all_bkp_files = glob.glob(os.path.join(BKP_DIR, "*_parte*_pt.json"))
themes = set()
for f in all_bkp_files:
    basename = os.path.basename(f)
    # Extract theme key: everything before _parteXX
    # Example: 03_3.信仰編_08_御神業の心得_parte01_pt.json
    parts = basename.split("_parte")
    if len(parts) > 1:
        themes.add(parts[0])

theme_keys = sorted(list(themes))
print(f"Aligning parts for {len(theme_keys)} themes...")

all_renames = []

for theme_key in theme_keys:
    print(f"\nProcessing Theme: {theme_key}")

    # Get all PT files
    # Get all PT files
    pt_pattern = os.path.join(BKP_DIR, f"{theme_key}_parte*_pt.json")
    pt_files = sorted(glob.glob(pt_pattern))

    # Get all Original files
    orig_pattern = os.path.join(BKP_DIR, f"{theme_key}_parte*.json")
    # Filter out _pt.json and _merged.json
    orig_files = [f for f in glob.glob(orig_pattern) if "_pt.json" not in f and "_merged.json" not in f]
    orig_files.sort()

    print(f"Found {len(pt_files)} PT files and {len(orig_files)} Original files.")

    # Load all originals into memory for fast searching
    orig_data_map = {}
    for fpath in orig_files:
        basename = os.path.basename(fpath)
        try:
            with open(fpath, 'r', encoding='utf-8') as f:
                data = json.load(f)
                pubs = data.get("publications", [])
                titles = set()
                for p in pubs:
                    t = p.get("publication_title", "").strip()
                    if t:
                        titles.add(t)
                orig_data_map[basename] = titles
        except Exception as e:
            print(f"Error loading {basename}: {e}")

    # Match PT files to Originals
    matches = []

    for pt_path in pt_files:
        pt_basename = os.path.basename(pt_path)
        
        # Check if we can find a matching original
        best_match = None
        match_count = 0
        matched_titles = []
        
        try:
            with open(pt_path, 'r', encoding='utf-8') as f:
                pt_data = json.load(f)
                pt_pubs = pt_data.get("publications", [])
                
                # Use the first few titles to find a match
                # Some titles might be generic, so check intersection count
                
                pt_titles = [p.get("publication_title", "").strip() for p in pt_pubs if p.get("publication_title")]
                
                max_intersection = 0
                
                for orig_base, orig_titles in orig_data_map.items():
                    # Count how many PT titles contain an Orig title
                    current_intersection = 0
                    for pt_t in pt_titles:
                        # Check if any orig title is substring of pt_t
                        # (Simple check: orig in pt)
                        for orig_t in orig_titles:
                            if orig_t and orig_t in pt_t:
                                current_intersection += 1
                                break # matched one title in this pub
                    
                    if current_intersection > max_intersection:
                        max_intersection = current_intersection
                        best_match = orig_base
                    
                if best_match and max_intersection > 0:
                    matches.append((pt_basename, best_match, max_intersection))
                else:
                    matches.append((pt_basename, "NO_MATCH", 0))

        except Exception as e:
            print(f"Error processing {pt_basename}: {e}")

    print("\nALIGNMENT RESULTS:")
    print(f"{'PT File':<50} | {'Best Match Orig':<50} | {'Score'}")
    print("-" * 110)

    renames = []
    for pt_base, orig_base, score in matches:
        print(f"{pt_base:<50} | {orig_base:<50} | {score}")
        
        if orig_base != "NO_MATCH":
            # Check if numbering is different
            # Extract number from PT
            pt_num = int(pt_base.split("_parte")[1].split("_pt.json")[0])
            # Extract number from Orig
            orig_num = int(orig_base.split("_parte")[1].split(".json")[0])
            
            if pt_num != orig_num:
                print(f"  >>> MISMATCH! Suggest RENAME {pt_base} -> {orig_base.replace('.json', '_pt.json')}")
                renames.append((pt_base, orig_base.replace('.json', '_pt.json')))

    # Execute renames in REVERSE order to avoid overwrites
    if renames:
        print("\nEXECUTING RENAMES (Reverse Order):")
        # Reverse the list
        renames.reverse()
        
        for old, new in renames:
            old_path = os.path.join(BKP_DIR, old)
            new_path = os.path.join(BKP_DIR, new)
            
            print(f"  Renaming {old} -> {new}")
            try:
                 os.rename(old_path, new_path)
            except Exception as e:
                 print(f"  ERROR: {e}")
    else:
        print("No renames needed.")
