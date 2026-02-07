
import glob
import os

BKP_DIR = "/Users/michael/Documents/Ensinamentos/Sites/ShinCollege_Pt/data/temasSeparados/bkp"

def check_missing_in_bkp():
    pt_files = glob.glob(os.path.join(BKP_DIR, "*_pt.json"))
    missing_originals = []
    
    print(f"Verificando {len(pt_files)} arquivos em bkp...")
    
    for pt_path in pt_files:
        basename = os.path.basename(pt_path)
        orig_basename = basename.replace("_pt.json", ".json")
        orig_path = os.path.join(BKP_DIR, orig_basename)
        
        if not os.path.exists(orig_path):
            missing_originals.append(orig_basename)
            # print(f"❌ Original faltando em bkp para: {basename}")
            
    return missing_originals

if __name__ == "__main__":
    missing = check_missing_in_bkp()
    if missing:
        print("\nArquivos originais (Japanese) que faltaram durante o merge (não estão em bkp):")
        for f in sorted(missing):
            print(f"- {f}")
    else:
        print("\nNenhum arquivo original faltando encontrado em bkp.")
