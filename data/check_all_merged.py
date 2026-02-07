
import json
import os
import glob

TEMAS_DIR = "/Users/michael/Documents/Ensinamentos/Sites/ShinCollege_Pt/data/temasSeparados"

def check_all_merged():
    merged_files = glob.glob(os.path.join(TEMAS_DIR, "*_merged.json"))
    total_missing = 0
    
    print(f"Encontrados {len(merged_files)} arquivos merged.")
    
    for merged_file in merged_files:
        basename = os.path.basename(merged_file)
        # print(f"Verificando {basename}...")
        
        try:
            with open(merged_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
        except Exception as e:
            print(f"Erro ao ler {basename}: {e}")
            continue
            
        publications = data.get("publications", [])
        file_missing_count = 0
        
        for pub in publications:
            content_jp = pub.get("content", "").strip()
            content_pt = pub.get("content_ptbr", "").strip()
            title = pub.get("title", "Sem Título")
            
            # If we have translation but NO Japanese content
            if content_pt and not content_jp:
                print(f"❌ {basename}: Falta conteúdo japonês em '{title}'")
                file_missing_count += 1
                
        if file_missing_count > 0:
            total_missing += file_missing_count
            print(f"  -> Total faltando neste arquivo: {file_missing_count}")
            
    if total_missing == 0:
        print("\n✅ Nenhum conteúdo japonês faltando em nenhum arquivo merged.")
    else:
        print(f"\nTotal geral de publicações com Japones faltando: {total_missing}")

if __name__ == "__main__":
    check_all_merged()
