
import glob
import os

BASE_DIR = "/Users/michael/Documents/Ensinamentos/Sites/ShinCollege_Pt/data"
TEMAS_DIR = os.path.join(BASE_DIR, "temasSeparados")
PARTES_DIR = os.path.join(TEMAS_DIR, "partes")
BKP_DIR = os.path.join(TEMAS_DIR, "bkp")

def check_missing_originals():
    # Find all translation files (both "copy.json" and "_pt.json")
    copy_files = glob.glob(os.path.join(PARTES_DIR, "* copy.json"))
    pt_files = glob.glob(os.path.join(PARTES_DIR, "*_pt.json"))
    
    all_trans_files = copy_files + pt_files
    
    missing_originals = []
    
    print(f"Verificando {len(all_trans_files)} arquivos de tradução...")
    
    for path in all_trans_files:
        basename = os.path.basename(path)
        
        # Determine expected original filename
        if " copy.json" in basename:
            orig_basename = basename.replace(" copy.json", ".json")
        elif "_pt.json" in basename:
            orig_basename = basename.replace("_pt.json", ".json")
        else:
            continue
            
        # Check if original exists in PARTES_DIR or BKP_DIR
        orig_path_partes = os.path.join(PARTES_DIR, orig_basename)
        orig_path_bkp = os.path.join(BKP_DIR, orig_basename)
        
        if not os.path.exists(orig_path_partes) and not os.path.exists(orig_path_bkp):
            missing_originals.append(orig_basename)
            print(f"❌ Faltando original para: {basename}")
        else:
            # print(f"✅ Encontrado original para: {basename}")
            pass
            
    return missing_originals

if __name__ == "__main__":
    missing = check_missing_originals()
    print("\nResumo dos arquivos originais faltando:")
    for f in missing:
        print(f"- {f}")
