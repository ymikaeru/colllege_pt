import os
import json
import glob
import shutil

# Configuration
BASE_DIR = "/Users/michael/Documents/Ensinamentos/Sites/ShinCollege_Pt/data/temasSeparados"
PARTES_DIR = os.path.join(BASE_DIR, "partes")
BKP_DIR = os.path.join(BASE_DIR, "bkp_translations")
# The output filename requested: "adicionar _merge no arquivo"
OUTPUT_FILENAME = "04_4.その他_04_宗教断片集_merge.json"
OUTPUT_FILE = os.path.join(BASE_DIR, OUTPUT_FILENAME)

def task_rename():
    """Step 1: Renaming '* copy.json' to '*_pt.json'"""
    print("--- Step 1: Renaming '* copy.json' to '*_pt.json' ---")
    files = glob.glob(os.path.join(PARTES_DIR, "* copy.json"))
    if not files:
        print("No matches for '* copy.json'. Skipping renaming.")
        return
    
    for fpath in files:
        new_path = fpath.replace(" copy.json", "_pt.json")
        try:
            os.rename(fpath, new_path)
            print(f"Renamed: {os.path.basename(fpath)} -> {os.path.basename(new_path)}")
        except Exception as e:
            print(f"Error renaming {fpath}: {e}")

def task_merge():
    """Step 2 & 3: Merge content and save with '_merge' suffix"""
    print(f"\n--- Step 2 & 3: Merging to '{OUTPUT_FILENAME}' ---")
    
    # Find all _pt.json files
    # We sort them to ensure order (parte01, parte02, etc.)
    pt_files = sorted(glob.glob(os.path.join(PARTES_DIR, "*_pt.json")))
    
    if not pt_files:
        print("No '*_pt.json' files found to merge.")
        return []

    merged_data = None
    all_pubs = []
    
    for fpath in pt_files:
        try:
            with open(fpath, 'r', encoding='utf-8') as f:
                data = json.load(f)
                
            if merged_data is None:
                # Initialize header from the first file found, or default
                merged_data = {
                    "source_file": "04_4.その他_04_宗教断片集.json",
                    "volume": data.get("volume", "4.その他"),
                    "theme_name": data.get("theme_name", "宗教断片集"),
                    "theme_name_ptbr": data.get("theme_name_ptbr", ""),
                    "publications": []
                }
            
            pubs = data.get("publications", [])
            all_pubs.extend(pubs)
            print(f"Merged {len(pubs)} items from {os.path.basename(fpath)}")
            
        except Exception as e:
            print(f"Error reading {fpath}: {e}")

    if merged_data:
        merged_data["publications"] = all_pubs
        # Write to Output
        with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
            json.dump(merged_data, f, ensure_ascii=False, indent=2)
        print(f"Successfully saved merged file to: {OUTPUT_FILE}")
        print(f"Total publications: {len(all_pubs)}")
        return pt_files
    else:
        print("Nothing merged.")
        return []

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
            # print(f"Moved: {fname}") # Optional: verify verbosity
            moved_count += 1
        except Exception as e:
            print(f"Error moving {fname}: {e}")
            
    print(f"Moved {moved_count} files to {BKP_DIR}")

def main():
    print("Starting Auto-Merge Workflow...")
    task_rename()
    processed_files = task_merge()
    if processed_files:
        task_move_backup(processed_files)
    else:
        print("Skipping backup move as no files were merged.")
    print("Workflow Completed.")

if __name__ == "__main__":
    main()
