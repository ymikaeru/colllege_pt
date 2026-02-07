
import json
import os

MERGED_FILE = "/Users/michael/Documents/Ensinamentos/Sites/ShinCollege_Pt/data/temasSeparados/01_1.経綸・霊主体従・夜昼転換・祖霊祭祀編_03_霊主体従_merged.json"

def check_empty_content():
    if not os.path.exists(MERGED_FILE):
        print(f"Arquivo merged não encontrado: {MERGED_FILE}")
        return

    with open(MERGED_FILE, 'r', encoding='utf-8') as f:
        data = json.load(f)
        
    publications = data.get("publications", [])
    missing_content_count = 0
    
    print(f"Verificando {len(publications)} publicações no arquivo merged...")
    
    for pub in publications:
        title = pub.get("title", "Sem Título")
        content_jp = pub.get("content", "").strip()
        content_pt = pub.get("content_ptbr", "").strip()
        pub_idx = pub.get("pub_idx", -1)
        
        if not content_jp and content_pt:
            print(f"❌ Conteúdo Japonês faltando para: {title} (Index: {pub_idx})")
            missing_content_count += 1
            
    if missing_content_count == 0:
        print("✅ Nenhuma publicação encontrada com Japonês faltando (onde existe tradução).")
    else:
        print(f"\nTotal de publicações com Japonês faltando: {missing_content_count}")

if __name__ == "__main__":
    check_empty_content()
