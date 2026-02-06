import glob
import os
import shutil

BASE_DIR = "/Users/michael/Documents/Ensinamentos/Sites/ShinCollege_Pt/data/temasSeparados"
PARTES_DIR = os.path.join(BASE_DIR, "partes")
BKP_DIR = os.path.join(BASE_DIR, "bkp")

def archive_parts():
    # 1. Find all existing merged files
    merged_files = glob.glob(os.path.join(BASE_DIR, "*_merged.json"))
    
    print(f"Found {len(merged_files)} merged files.")
    
    total_moved = 0
    
    for merged_path in merged_files:
        merged_filename = os.path.basename(merged_path)
        # Assuming filename format is {theme_name}_merged.json
        # We need to extract {theme_name} to find matching parts
        # Careful with underscores in theme names. 
        # Strategy: remove suffix "_merged.json"
        
        if not merged_filename.endswith("_merged.json"):
            continue
            
        theme_base = merged_filename[:-12] # Remove "_merged.json"
        print(f"Processing theme: {theme_base}")
        
        # 2. Find matching parts in 'partes/'
        # Pattern: {theme_base}_parte*
        # This catches _parte01.json, _parte01_pt.json, _parte01 copy.json etc.
        pattern = os.path.join(PARTES_DIR, f"{theme_base}_parte*")
        parts = glob.glob(pattern)
        
        if not parts:
            print(f"  No parts found for {theme_base}")
            continue
            
        print(f"  Found {len(parts)} parts.")
        
        # 3. Move parts to 'bkp/'
        if not os.path.exists(BKP_DIR):
            os.makedirs(BKP_DIR)
            
        for part_path in parts:
            part_filename = os.path.basename(part_path)
            dest_path = os.path.join(BKP_DIR, part_filename)
            
            try:
                shutil.move(part_path, dest_path)
                # print(f"    Moved {part_filename} -> bkp/")
                total_moved += 1
            except Exception as e:
                print(f"    Error moving {part_filename}: {e}")

    print(f"Archive complete. Moved {total_moved} files to {BKP_DIR}")

if __name__ == "__main__":
    archive_parts()
