import os
import json
import glob
import re
import shutil

# Configuration
BASE_DIR = "/Users/michael/Documents/Ensinamentos/Sites/ShinCollege_Pt/data/temasSeparados"
PARTES_DIR = os.path.join(BASE_DIR, "partes")
BKP_DIR = os.path.join(BASE_DIR, "bkp_translations")

def task_rename():
    """Step 1: Renaming '* copy.json' to '*_pt.json'"""
    print("--- Step 1: Renaming '* copy.json' to '*_pt.json' ---")
    files = glob.glob(os.path.join(PARTES_DIR, "* copy.json"))
    if not files:
        print("No matches for '* copy.json'. Checking for existing *_pt.json files...")
    else:
        for fpath in files:
            new_path = fpath.replace(" copy.json", "_pt.json")
            try:
                os.rename(fpath, new_path)
                print(f"Renamed: {os.path.basename(fpath)} -> {os.path.basename(new_path)}")
            except Exception as e:
                print(f"Error renaming {fpath}: {e}")

def task_group_and_merge():
    """Step 2 & 3: Group by base name and merge"""
    print(f"\n--- Step 2 & 3: Grouping and Merging ---")
    
    # regex to capture base name from *_pt.json
    # Format: {BASE_NAME}_parte{NUMBER}_pt.json
    # Example: 04_4.その他_04_宗教断片集_parte20_pt.json
    regex = re.compile(r"^(.*)_parte\d+_pt\.json$")
    
    pt_files = sorted(glob.glob(os.path.join(PARTES_DIR, "*_pt.json")))
    if not pt_files:
        print("No '*_pt.json' files found to merge.")
        return []

    groups = {}
    
    for fpath in pt_files:
        fname = os.path.basename(fpath)
        match = regex.match(fname)
        if match:
            base_name = match.group(1)
            if base_name not in groups:
                groups[base_name] = []
            groups[base_name].append(fpath)
        else:
            print(f"Skipping file (no match for pattern): {fname}")

    print(f"Found {len(groups)} themes to merge: {list(groups.keys())}")

    merged_files = []
    
    for base_name, files in groups.items():
        print(f"\nProcessing group: {base_name} ({len(files)} parts)")
        output_filename = f"{base_name}_merged.json"
        output_file = os.path.join(BASE_DIR, output_filename)
        
        merged_data = None
        all_pubs = []
        
        # Sort files to ensure order
        files.sort()
        
        for fpath in files:
            try:
                with open(fpath, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                
                if merged_data is None:
                    merged_data = {
                        "source_file": data.get("source_file", f"{base_name}.json"),
                        "volume": data.get("volume", ""),
                        "theme_name": data.get("theme_name", ""),
                        "theme_name_ptbr": data.get("theme_name_ptbr", ""),
                        "publications": []
                    }
                
                pubs = data.get("publications", [])
                all_pubs.extend(pubs)
                
            except Exception as e:
                print(f"Error reading {fpath}: {e}")
        
        if merged_data:
            merged_data["publications"] = all_pubs
            try:
                with open(output_file, 'w', encoding='utf-8') as f:
                    json.dump(merged_data, f, ensure_ascii=False, indent=2)
                print(f"  -> Created: {output_filename} ({len(all_pubs)} publications)")
                merged_files.extend(files)
            except Exception as e:
                print(f"Error writing to {output_file}: {e}")
        
    return merged_files

def task_move_backup(processed_files):
    """Step 4: Move processed files to backup"""
    print("\n--- Step 4: Moving files to 'bkp_translations' ---")
    if not os.path.exists(BKP_DIR):
        try:
            os.makedirs(BKP_DIR)
            print(f"Created backup directory: {BKP_DIR}")
        except Exception as e:
            print(f"Error creating backup directory: {e}")
            return

    moved_count = 0
    for fpath in processed_files:
        fname = os.path.basename(fpath)
        dest = os.path.join(BKP_DIR, fname)
        try:
            shutil.move(fpath, dest)
            moved_count += 1
        except Exception as e:
            print(f"Error moving {fname}: {e}")
            
    print(f"Moved {moved_count} files to {BKP_DIR}")

def main():
    print("Starting Corrected Merge Workflow...")
    task_rename()
    processed_files = task_group_and_merge()
    if processed_files:
        task_move_backup(processed_files)
    else:
        print("No files were processed/merged.")
    print("Workflow Completed.")

if __name__ == "__main__":
    main()
