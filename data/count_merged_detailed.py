
import json
import glob
import os

TEMAS_DIR = "/Users/michael/Documents/Ensinamentos/Sites/ShinCollege_Pt/data/temasSeparados"

def count_merged_detailed():
    merged_files = sorted(glob.glob(os.path.join(TEMAS_DIR, "*_merged.json")))
    
    total_merged = 0
    print(f"Encontrados {len(merged_files)} arquivos merged.")
    
    for f in merged_files:
        basename = os.path.basename(f)
        try:
            with open(f, 'r') as file:
                data = json.load(file)
            pubs = data.get("publications", [])
            count = len(pubs)
            total_merged += count
            print(f"- {basename}: {count} docs")
            
            # Check unique parts source
            # Wait, merged file doesn't store source part info in metadata, but we can guess?
            # Or maybe we just trust the count.
            
        except Exception as e:
            print(f"Erro ler {basename}: {e}")
            
    print(f"\nTotal Geral Merged: {total_merged}")

if __name__ == "__main__":
    count_merged_detailed()
