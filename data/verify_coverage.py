import json
import os
import glob
import re

DATA_DIR = "data"
MAIN_JSON = os.path.join(DATA_DIR, "shin_college_data.json")
BKP_DIR = os.path.join(DATA_DIR, "temasSeparados", "bkp")

def normalize(text):
    return text.strip() if text else ""

def verify():
    print("Carregando shin_college_data.json...")
    try:
        with open(MAIN_JSON, 'r', encoding='utf-8') as f:
            main_data = json.load(f)
    except FileNotFoundError:
        print(f"ERRO: {MAIN_JSON} não encontrado.")
        return

    # Indexar o main data para busca rápida
    # Estrutura: Volume -> Theme -> Title -> PubTitle -> Data
    # Vamos criar um set de assinaturas: (volume, theme, pub_title)
    main_index = {}
    
    total_main_pubs = 0
    missing_jp_in_main = 0
    missing_pt_in_main = 0

    for vol in main_data:
        v_name = normalize(vol.get("volume", ""))
        for theme in vol.get("themes", []):
            t_name = normalize(theme.get("theme", ""))
            for title in theme.get("titles", []):
                for pub in title.get("publications", []):
                    p_title = normalize(pub.get("publication_title", ""))
                    
                    # Chave única (aproximada, já que title wrapper pode variar, mas pub_title deve ser constante)
                    # O merge script usa pub_idx, mas aqui vamos tentar por título para garantir
                    # Se houver duplicatas de título no mesmo tema, isso pode ser um problema, mas vamos contar.
                    key = (v_name, t_name, p_title)
                    
                    if key not in main_index:
                        main_index[key] = []
                    main_index[key].append(pub)
                    
                    total_main_pubs += 1
                    
                    if not pub.get("content"):
                        missing_jp_in_main += 1
                    if not pub.get("content_ptbr"):
                        missing_pt_in_main += 1

    print(f"Total de publicações no main JSON: {total_main_pubs}")
    print(f"  - Sem Japonês: {missing_jp_in_main}")
    print(f"  - Sem Português: {missing_pt_in_main}")

    # DEBUG: Show structure
    print("\n[DEBUG] Estrutura encontrada no main_data:")
    for vol in main_data:
        vol_name = vol.get("volume", "SEM_VOLUME")
        themes = vol.get("themes", [])
        print(f"  Volume: {vol_name} (Temas: {len(themes)})")
        for t in themes:
             t_name = t.get("theme", "SEM_TEMA")
             titles = t.get("titles", [])
             t_pubs = 0
             for tit in titles:
                 t_pubs += len(tit.get("publications", []))
             print(f"    - Tema: {t_name} (Pubs: {t_pubs})")
    
    # Agora varrer os arquivos _pt.json no backup
    print(f"\nVerificando arquivos em {BKP_DIR}...")
    pt_files = glob.glob(os.path.join(BKP_DIR, "*_pt.json"))
    
    if not pt_files:
        print("Nenhum arquivo *_pt.json encontrado no backup.")
        return

    files_checked = 0
    pubs_checked = 0
    pubs_found = 0
    pubs_missing = 0
    
    files_with_missing_content = []

    for pt_file in pt_files:
        files_checked += 1
        with open(pt_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # Tentar extrair metadados do arquivo ou do nome (caso o arquivo tenha sido salvo sem no etapa anterior, mas o merge corrigiu)
        # O arquivo no bkp é o original input, então ele pode NÃO ter o metadata se não foi salvo com ele.
        # Mas o merge usou esse arquivo.
        # Vamos confiar no publication_title.
        
        # O volume e theme no arquivo podem estar vazios se for um dos problematicos.
        # Nesse caso, teríamos que inferir do nome do arquivo para comparar com o main_index corretamente?
        # Ou podemos buscar apenas pelo publication_title em todo o main_index (relaxando a busca globalmente ou por tema)?
        
        # Vamos tentar ser estritos primeiro usando o metadata DO ARQUIVO se existir.
        fname = os.path.basename(pt_file)
        
        # Parse filename para ter o "Theme" esperado caso o JSON não tenha
        # Ex: 01_1.Volume_03_Theme_parte01_pt.json
        # volume -> 1.Volume
        # theme -> Theme
        
        vol_name_file = data.get("volume", "")
        theme_name_file = data.get("theme_name", "")
        
        # Fallback de nome se vazio (simulando o que o merge fez)
        if not vol_name_file or not theme_name_file:
             parts = fname.replace("_pt.json", "").split('_')
             if len(parts) >= 4:
                vol_name_file = parts[1]
                theme_name_file = parts[3]
                if len(parts) > 4:
                    theme_name_file = "_".join(parts[3:-1]) # remove 'parteXX'

        vol_name_file = normalize(vol_name_file)
        theme_name_file = normalize(theme_name_file)

        pt_pubs_set = set()
        for pub_entry in data.get("publications", []):
            p_title = normalize(pub_entry.get("publication_title", ""))
            if p_title:
                pt_pubs_set.add(p_title)

        # Normalização de título para comparação
        # Remover data entre parênteses largos ou normais
        # Ex: 'Title （昭和24年）' -> 'Title'
        def normalize_title(t):
            # Remove （...）
            t = re.sub(r'[\（\(].*?[\）\)]', '', t)
            # Remove espaços extras
            return t.strip()

        for p_title in pt_pubs_set:
            pubs_checked += 1
            norm_p_title = normalize_title(p_title)
            
            found = False
            matched_pub = None
            
            # 1. Match exato
            key = (vol_name_file, theme_name_file, p_title)
            if key in main_index:
                found = True
                matched_pub = main_index[key][0]
            else:
                # 2. Match Fuzzy (Ignorando datas e parênteses)
                # Filtrar candidatos pelo tema
                candidates = [k for k in main_index if k[1] == theme_name_file]
                
                for k in candidates:
                    orig_title = k[2]
                    norm_orig = normalize_title(orig_title)
                    
                    # Comparação normalizada exata
                    if norm_p_title and norm_p_title == norm_orig:
                        found = True
                        matched_pub = main_index[k][0]
                        break
                    
                    # Comparação substring (fallback)
                    # Apenas se string tiver tamanho razoável para evitar falso positivo
                    if len(norm_p_title) > 4 and (norm_p_title in norm_orig or norm_orig in norm_p_title):
                        found = True
                        matched_pub = main_index[k][0]
                        break

            if found:
                pubs_found += 1
                if matched_pub:
                     if not matched_pub.get("content"):
                         pass 
                         # print(f"⚠️  SEM JAPONÊS: '{p_title}' em {fname}")
                     if not matched_pub.get("content_ptbr"):
                         pass
                         # print(f"⚠️  SEM PORTUGUÊS: '{p_title}' em {fname}")
            else:
                pubs_missing += 1
                print(f"❌ NÃO ENCONTRADO: '{p_title}' (Norm: '{norm_p_title}')\n    Arquivo: {fname}\n    (Vol: {vol_name_file}, Tema: {theme_name_file})")

    print("-" * 50)
    print("MÉTRICAS FINAIS:")
    print(f"Arquivos verificados: {files_checked}")
    print(f"Publicações nos arquivos PT: {pubs_checked}")
    print(f"Publicações encontradas no JSON final: {pubs_found}")
    print(f"Publicações NÃO encontradas: {pubs_missing}")
    
    if pubs_missing == 0:
        print("\n✅  SUCESSO: Todos os arquivos traduzidos estão presentes no JSON final.")
    else:
        print(f"\n⚠️  ATENÇÃO: {pubs_missing} publicações parecem estar faltando.")

    if missing_jp_in_main == 0 and missing_pt_in_main == 0:
         print("✅  Integração Bilíngue: Todas as entradas no JSON final possuem conteúdo em JP e PT.")
    else:
         print(f"⚠️  Integração Bilíngue Incompleta:\n    - {missing_jp_in_main} sem Japonês\n    - {missing_pt_in_main} sem Português")

if __name__ == "__main__":
    verify()
