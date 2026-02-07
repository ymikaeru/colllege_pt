
import json
import glob
import os

BKP_DIR = "/Users/michael/Documents/Ensinamentos/Sites/ShinCollege_Pt/data/temasSeparados/bkp"
DATA_FILE = "/Users/michael/Documents/Ensinamentos/Sites/ShinCollege_Pt/data/shin_college_data.json"

def count_bkp_originals():
    # Get all .json files, exclude _pt.json
    all_files = glob.glob(os.path.join(BKP_DIR, "*.json"))
    original_files = [f for f in all_files if not f.endswith("_pt.json")]
    
    total_pubs = 0
    print(f"Analisando {len(original_files)} arquivos originais em bkp/ ...")
    
    for fpath in original_files:
        try:
            with open(fpath, 'r', encoding='utf-8') as f:
                data = json.load(f)
            pubs = data.get("publications", [])
            total_pubs += len(pubs)
        except Exception as e:
            print(f"Erro ao ler {os.path.basename(fpath)}: {e}")
            
    print(f"Total de documentos nos arquivos originais (bkp): {total_pubs}")
    return total_pubs

def simulate_app_count_logic():
    print("\nSimulando a contagem do App (conteúdo único)...")
    if not os.path.exists(DATA_FILE):
        print("Arquivo shin_college_data.json não encontrado.")
        return

    with open(DATA_FILE, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    unique_content = set()
    total_entries = 0
    
    for volume in data:
        for theme in volume.get("themes", []):
            for title_obj in theme.get("titles", []):
                for pub in title_obj.get("publications", []):
                    total_entries += 1
                    
                    content_jp = pub.get("content", "").strip()
                    content_pt = pub.get("content_ptbr", "").strip()
                    
                    if content_jp or content_pt:
                        # Logic from app.js: use JP if available, else PT
                        key = content_jp if content_jp else content_pt
                        unique_content.add(key)
                        
    print(f"Total de entradas (bruto): {total_entries}")
    print(f"Total de documentos ÚNICOS (lógica do App): {len(unique_content)}")

if __name__ == "__main__":
    count_bkp_originals()
    simulate_app_count_logic()
