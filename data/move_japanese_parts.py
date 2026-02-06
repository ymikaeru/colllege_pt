import glob
import os
import shutil

# Correct paths
SOURCE_DIR = "/Users/michael/Documents/Ensinamentos/Sites/ShinCollege_Pt/data/temasSeparados/partes"
DEST_DIR = "/Users/michael/Documents/Ensinamentos/Sites/ShinCollege_Pt/data/temasSeparados/bkp_translations"

def move_japanese_parts():
    # Pattern for the specific theme parts: 04_4.その他_04_宗教断片集_parte*.json
    # We want to exclude "*_pt.json" and "* copy.json". 
    # glob pattern keys on the prefix.
    
    pattern = os.path.join(SOURCE_DIR, "04_4.その他_04_宗教断片集_parte*.json")
    candidates = glob.glob(pattern)
    
    print(f"Checking {len(candidates)} candidates...")
    
    count_moved = 0
    for file_path in candidates:
        filename = os.path.basename(file_path)
        
        # Filter out translations and copies if they match the glob (glob catches everything starting with pattern)
        if filename.endswith("_pt.json") or " copy" in filename:
            continue
            
        dest_path = os.path.join(DEST_DIR, filename)
        
        # Check if file already exists in destination
        if os.path.exists(dest_path):
             print(f"File {filename} already exists in destination. Skipping (or replacing?). Skipping for safety.")
             continue
             
        print(f"Moving {filename} -> {DEST_DIR}")
        shutil.move(file_path, dest_path)
        count_moved += 1

    print(f"Moved {count_moved} files.")

if __name__ == "__main__":
    if not os.path.exists(DEST_DIR):
        print(f"Creating destination directory: {DEST_DIR}")
        os.makedirs(DEST_DIR)
    move_japanese_parts()
