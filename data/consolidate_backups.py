import glob
import os
import shutil

SOURCE_DIR = "/Users/michael/Documents/Ensinamentos/Sites/ShinCollege_Pt/data/temasSeparados/bkp_translations"
DEST_DIR = "/Users/michael/Documents/Ensinamentos/Sites/ShinCollege_Pt/data/temasSeparados/bkp"

def consolidate_backups():
    if not os.path.exists(SOURCE_DIR):
        print("Source directory does not exist.")
        return

    files = glob.glob(os.path.join(SOURCE_DIR, "*"))
    print(f"Found {len(files)} file(s) in {SOURCE_DIR}")

    if not os.path.exists(DEST_DIR):
        os.makedirs(DEST_DIR)

    for file_path in files:
        filename = os.path.basename(file_path)
        dest_path = os.path.join(DEST_DIR, filename)
        
        try:
            shutil.move(file_path, dest_path)
            # print(f"Moved {filename}")
        except Exception as e:
            print(f"Error moving {filename}: {e}")

    print(f"Moved all files to {DEST_DIR}")
    
    # Optional: remove empty source dir
    try:
        os.rmdir(SOURCE_DIR)
        print("Removed empty source directory.")
    except Exception:
        pass

if __name__ == "__main__":
    consolidate_backups()
