import json
import glob
import os

DATA_DIR = "/Users/michael/Documents/Ensinamentos/Sites/ShinCollege_Pt/data/temasSeparados"

def cleanup_empty_merged():
    merged_files = glob.glob(os.path.join(DATA_DIR, "*_merged.json"))
    
    print(f"Checking {len(merged_files)} merged files...")
    
    deleted_count = 0
    
    for file_path in merged_files:
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # Check if it has any translation
            has_translation = False
            
            # Handle list of publications (the structure in merged files)
            if isinstance(data, dict) and "publications" in data:
                for pub in data["publications"]:
                    if pub.get("content_ptbr") and pub.get("content_ptbr").strip():
                        has_translation = True
                        break
            
            if not has_translation:
                print(f"File {os.path.basename(file_path)} has NO translations. Deleting.")
                os.remove(file_path)
                deleted_count += 1
            else:
                # print(f"File {os.path.basename(file_path)} has translations. Keeping.")
                pass
                
        except Exception as e:
            print(f"Error processing {file_path}: {e}")

    print(f"Cleanup complete. Deleted {deleted_count} files.")

if __name__ == "__main__":
    cleanup_empty_merged()
