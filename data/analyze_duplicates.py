
import json
import glob
import os

BKP_DIR = "/Users/michael/Documents/Ensinamentos/Sites/ShinCollege_Pt/data/temasSeparados/bkp"

def analyze_structure():
    all_files = glob.glob(os.path.join(BKP_DIR, "*.json"))
    
    # Filter out _pt.json
    originals = [f for f in all_files if not f.endswith("_pt.json")]
    
    # Check for "copy" duplicates
    clean_originals = set()
    duplicates = []
    
    for f in originals:
        basename = os.path.basename(f)
        if " copy" in basename:
            # Check if non-copy version exists
            clean_name = basename.replace(" copy", "")
            if os.path.join(BKP_DIR, clean_name) in all_files:
                duplicates.append(f)
            else:
                clean_originals.add(f) # It's a copy but the "original" original is missing? Treat as unique for now.
        else:
            clean_originals.add(f)
            
    print(f"Total Arquivos Originais (Raw): {len(originals)}")
    print(f"Total Duplicatas (copy): {len(duplicates)}")
    print(f"Total Originais Únicos (Estimado): {len(originals) - len(duplicates)}")
    
    # Count docs in duplicates to see if it explains the gap (~1100 docs)
    dup_docs = 0
    for d in duplicates:
        try:
            with open(d, 'r') as f:
                data = json.load(f)
            dup_docs += len(data.get("publications", []))
        except: pass
        
    print(f"Documentos em arquivos duplicados: {dup_docs}")

if __name__ == "__main__":
    analyze_structure()
