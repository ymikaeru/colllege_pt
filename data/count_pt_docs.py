
import json
import glob
import os

BKP_DIR = "/Users/michael/Documents/Ensinamentos/Sites/ShinCollege_Pt/data/temasSeparados/bkp"

def count_pt_docs():
    pt_files = glob.glob(os.path.join(BKP_DIR, "*_pt.json"))
    total_pt = 0
    
    print(f"Contando docs em {len(pt_files)} arquivos _pt.json...")
    
    for f in pt_files:
        try:
            with open(f, 'r') as file:
                data = json.load(file)
            total_pt += len(data.get("publications", []))
        except: pass
        
    print(f"Total Documentos em arquivos _pt: {total_pt}")

if __name__ == "__main__":
    count_pt_docs()
