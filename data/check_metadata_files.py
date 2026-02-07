
import json
import glob
import os

PARTES_DIR = "/Users/michael/Documents/Ensinamentos/Sites/ShinCollege_Pt/data/temasSeparados/bkp"

THEME_PATTERNS = [
    "01_1.経綸・霊主体従・夜昼転換・祖霊祭祀編_03_霊主体従",
    "02_2.浄霊・神示の健康法・自然農法編_01_浄霊の原理",
    "02_2.浄霊・神示の健康法・自然農法編_02_浄霊の方法"
]

def check_metadata():
    print("Verificando metadados nos arquivos de tema problemáticos...")
    
    for pattern in THEME_PATTERNS:
        files = glob.glob(os.path.join(PARTES_DIR, f"{pattern}*_pt.json"))
        print(f"\nTema: {pattern} ({len(files)} arquivos)")
        
        found_valid = False
        for fpath in files:
            basename = os.path.basename(fpath)
            try:
                with open(fpath, 'r') as f:
                    data = json.load(f)
                
                vol = data.get("volume", "")
                theme = data.get("theme_name", "")
                
                if vol and theme:
                    print(f"  ✅ {basename}: Volume='{vol}', Theme='{theme}'")
                    found_valid = True
                    break # Found one valid, that's enough to know it's possible
                else:
                    # print(f"  ❌ {basename}: Empty metadata")
                    pass
            except: pass
            
        if not found_valid:
            print("  🛑 NENHUM arquivo com metadados válidos encontrado para este tema!")

if __name__ == "__main__":
    check_metadata()
