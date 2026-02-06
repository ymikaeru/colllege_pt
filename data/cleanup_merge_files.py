import glob
import os

DATA_DIR = "/Users/michael/Documents/Ensinamentos/Sites/ShinCollege_Pt/data/temasSeparados"

def cleanup_legacy_files():
    # Find all files ending in _merge.json
    legacy_files = glob.glob(os.path.join(DATA_DIR, "*_merge.json"))
    
    print(f"Found {len(legacy_files)} legacy files.")
    
    for legacy_path in legacy_files:
        base_name = legacy_path[:-11] # Remove "_merge.json"
        merged_path = base_name + "_merged.json"
        
        legacy_filename = os.path.basename(legacy_path)
        merged_filename = os.path.basename(merged_path)
        
        if os.path.exists(merged_path):
            print(f"Duplicate found: {legacy_filename} AND {merged_filename} exist.")
            print(f"Removing legacy file: {legacy_filename}")
            os.remove(legacy_path)
        else:
            print(f"Renaming legacy file: {legacy_filename} -> {merged_filename}")
            os.rename(legacy_path, merged_path)
            
    print("Cleanup complete.")

if __name__ == "__main__":
    cleanup_legacy_files()
