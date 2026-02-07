
import json
import glob
import os
from collections import defaultdict

BKP_DIR = "/Users/michael/Documents/Ensinamentos/Sites/ShinCollege_Pt/data/temasSeparados/bkp"

def analyze_ignored():
    all_files = glob.glob(os.path.join(BKP_DIR, "*.json"))
    
    # Identify translated files
    pt_files = {f for f in all_files if f.endswith("_pt.json")}
    
    # Identify original files that HAVE a translation
    originals_with_translation = set()
    for ptf in pt_files:
        orig = ptf.replace("_pt.json", ".json")
        if orig in all_files:
            originals_with_translation.add(orig)
            
    # Identify ignored originals (those WITHOUT translation)
    ignored_originals = []
    for f in all_files:
        if f.endswith("_pt.json"): continue
        if f not in originals_with_translation:
            ignored_originals.append(f)
            
    print(f"Total Arquivos: {len(all_files)}")
    print(f"Arquivos Traduzidos (_pt): {len(pt_files)}")
    print(f"Originais com Tradução: {len(originals_with_translation)}")
    print(f"Originais IGNORADOS (sem tradução): {len(ignored_originals)}")
    
    # Count docs in ignored files
    ignored_docs_count = 0
    ignored_by_volume = defaultdict(int)
    
    print("\nContando documentos ignorados...")
    for fpath in ignored_originals:
        try:
            with open(fpath, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            pubs = data.get("publications", [])
            count = len(pubs)
            ignored_docs_count += count
            
            # Try to guess volume/theme from filename
            basename = os.path.basename(fpath)
            # Example: 01_1.VolumeName_02_ThemeName_parteXX.json
            parts = basename.split('_')
            if len(parts) >= 2:
                vol_name = parts[1]
                ignored_by_volume[vol_name] += count
                
        except Exception as e:
            print(f"Erro ler {os.path.basename(fpath)}: {e}")
            
    print(f"\nTotal de Documentos 'Perdidos' (não mergeados): {ignored_docs_count}")
    
    print("\n--- Detalhe por Volume (Top 10) ---")
    sorted_vols = sorted(ignored_by_volume.items(), key=lambda x: x[1], reverse=True)
    for vol, count in sorted_vols[:10]:
        print(f"{vol}: {count} docs")

if __name__ == "__main__":
    analyze_ignored()
