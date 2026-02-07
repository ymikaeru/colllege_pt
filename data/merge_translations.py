#!/usr/bin/env python3
"""
Script de Merge Completo para Traduções
========================================
Este script executa 4 etapas:
1. Renomeia arquivos "*copy.json" para "*_pt.json"
2. Faz merge das partes traduzidas (_pt) com as partes originais, criando arquivos "_merged"
3. Move os arquivos processados para a pasta bkp
4. Regenera o shin_college_data.json a partir dos arquivos merged
"""

import os
import json
import shutil
import glob
import re
from collections import defaultdict
import sys

BASE_DIR = "/Users/michael/Documents/Ensinamentos/Sites/ShinCollege_Pt/data"
TEMAS_DIR = os.path.join(BASE_DIR, "temasSeparados")
PARTES_DIR = os.path.join(TEMAS_DIR, "partes")
BKP_DIR = os.path.join(TEMAS_DIR, "bkp")
OUTPUT_FILE = os.path.join(BASE_DIR, "shin_college_data.json")

VOLUME_MAP = {
    "1.経綸・霊主体従・夜昼転換・祖霊祭祀編": "1. Plano Divino, Precedência do Espírito sobre a Matéria, Transição da Noite para o Dia e Culto aos Antepassados",
    "3.信仰編": "3. Seção da Fé",
    "4.その他": "4. Outros",
}

def step1_rename_copy_to_pt():
    """Renomeia arquivos 'X copy.json' para 'X_pt.json'"""
    print("\n" + "="*60)
    print("ETAPA 1: Renomeando arquivos ' copy.json' para '_pt.json'")
    print("="*60)
    
    pattern = os.path.join(PARTES_DIR, "* copy.json")
    copy_files = glob.glob(pattern)
    
    if not copy_files:
        print("  Nenhum arquivo ' copy.json' encontrado.")
        return 0
    
    renamed = 0
    for src in copy_files:
        # Remove " copy.json" do final e adiciona "_pt.json"
        base = src.replace(" copy.json", "")
        dst = base + "_pt.json"
        
        print(f"  {os.path.basename(src)} -> {os.path.basename(dst)}")
        shutil.move(src, dst)
        renamed += 1
    
    print(f"  Total renomeado: {renamed}")
    return renamed


def step2_merge_parts(filter_theme=None):
    """Lê arquivos _pt.json de partes, junta com original, e cria arquivo _merged.json por tema"""
    print("\n" + "="*60)
    print("ETAPA 2: Merge de traduções e originais")
    print("="*60)
    
    # Identificar temas baseados nos arquivos em PARTES_DIR
    themes = set()
    start_files = glob.glob(os.path.join(PARTES_DIR, "*_parte01_pt.json"))
    
    if not start_files:
        print("  Nenhum arquivo _parte01_pt.json encontrado em partes/!")
        # Fallback: talvez não tenhamos parte01? (Raro, mas...)
        # Escanear todos _pt.json
        all_pt = glob.glob(os.path.join(PARTES_DIR, "*_pt.json"))
        for f in all_pt:
            # Tentar adivinhar tema removendo _parteXX_pt.json
            name = os.path.basename(f)
            # Regex seria melhor, mas split serve
            parts = name.split("_parte")
            if len(parts) > 1:
                themes.add(parts[0])
    else:
        for f_path in start_files:
            basename = os.path.basename(f_path)
            theme_key = basename.split("_parte01_pt.json")[0]
            themes.add(theme_key)
    
    full_themes_list = sorted(list(themes))
    print(f"  Temas identificados: {len(full_themes_list)}")
    print(f"  Lista de Temas: {full_themes_list}")
    
    merged_count = 0
    
    for theme_key in full_themes_list:
        print(f"DEBUG: Processing theme_key: {repr(theme_key)}")
        if filter_theme:
             print(f"DEBUG: Checking filter '{filter_theme}' against '{theme_key}'")
             if filter_theme not in theme_key:
                print("DEBUG: Filter mismatch. Skipping.")
                continue

        # Encontrar todas as partes para o tema atual
        pattern_glob = os.path.join(PARTES_DIR, f"{theme_key}_parte*_pt.json")
        print(f"DEBUG: Glob pattern: {pattern_glob}")
        theme_parts_files = glob.glob(pattern_glob)
        
        if not theme_parts_files:
            print(f"  Nenhuma parte '_pt.json' encontrada para o tema '{theme_key}'. Pulando.")
            continue
        
        print(f"DEBUG: Encontrados {len(theme_parts_files)} arquivos para o tema '{theme_key}'")

        # Agrupar por tema (prefixo antes de _parteXX)
        parts_for_theme = []
        pattern = re.compile(r"^(.+?)_parte(\d+)(?:_pt)?\.json$")
        
        for pt_file in theme_parts_files:
            basename = os.path.basename(pt_file)
            match = pattern.match(basename.replace("_pt.json", ".json"))
            if match:
                part_num = int(match.group(2))
                parts_for_theme.append((part_num, pt_file))
            else:
                print(f"DEBUG: Skipping file {basename} - no pattern match")
        
        # Ordenar por número da parte
        parts_for_theme.sort(key=lambda x: x[0])

        print(f"\n  Processando tema: {theme_key}")
        print(f"    {len(parts_for_theme)} partes encontradas")
        # DEBUG: Print all parts found
        print(f"    Parts list: {[p[0] for p in parts_for_theme]}")
        
        # Carregar e mesclar todas as partes
        all_publications = []
        metadata = None
        
        for part_num, pt_path in parts_for_theme:
            try:
                # Carregar arquivo PT (com tradução portuguesa)
                with open(pt_path, 'r', encoding='utf-8') as f:
                    pt_data = json.load(f)
                
                # Buscar arquivo original correspondente (com japonês)
                # Tentar primeiro em partes/, depois em bkp/
                orig_basename = os.path.basename(pt_path).replace("_pt.json", ".json")
                orig_path = os.path.join(PARTES_DIR, orig_basename)
                
                if not os.path.exists(orig_path):
                    # Tentar no backup
                    orig_path = os.path.join(BKP_DIR, orig_basename)
                
                orig_data = None

                if os.path.exists(orig_path):
                    with open(orig_path, 'r', encoding='utf-8') as f_orig:
                        orig_data = json.load(f_orig)
                    
                    if orig_data.get("volume") and orig_data.get("theme_name"):
                        metadata = {
                            "volume": orig_data["volume"],
                            "theme_name": orig_data["theme_name"],
                            "theme_name_ptbr": pt_data.get("theme_name_ptbr", "") # PTBR vem do PT mesmo vazio
                        }
                        print(f"    ✅ Metadados encontrados em (Orig) {orig_basename}")
                        break
            except Exception as e:
                print(f"    ⚠️ Erro ao ler {pt_path} para metadados: {e}")
                continue

        # 2. Tentativa via Nome do Arquivo / Theme Key (Fallback)
        if metadata is None or not metadata.get("volume") or not metadata.get("theme_name"):
            print(f"    ⚠️  Metadados ausentes nos JSONs. Tentando extrair do key: '{theme_key}'")
            try:
                key_parts = theme_key.split('_')
                # Espera-se: IndexVol, VolName, IndexTheme, ThemeName
                # Ex: ["01", "1.Volume", "03", "Tema"]
                if len(key_parts) >= 4:
                    vol_name = key_parts[1]
                    theme_name = key_parts[3]
                    if len(key_parts) > 4:
                        theme_name = "_".join(key_parts[3:])
                    
                    metadata = {
                        "volume": vol_name,
                        "theme_name": theme_name,
                        "theme_name_ptbr": ""
                    }
                    print(f"    ✅ Metadados recuperados do nome: Volume='{vol_name}', Tema='{theme_name}'")
            except Exception as e:
                print(f"    ❌ Falha ao extrair do nome: {e}")

        # Se falhou tudo, pula
        if not metadata or not metadata.get("volume"):
             print(f"    🛑 ERRO CRÍTICO: Impossível determinar metadados para {theme_key}. Ignorando.")
             continue

        # ESTÁGIO 2: Mesclar Conteúdo
        # Agora iteramos novamente para processar o conteúdo usando o metadata garantido
        for part_num, pt_path in parts_for_theme:
            try:
                with open(pt_path, 'r', encoding='utf-8') as f:
                    pt_data = json.load(f)
                
                # Buscar arquivo original correspondente (com japonês)
                orig_basename = os.path.basename(pt_path).replace("_pt.json", ".json")
                orig_path = os.path.join(PARTES_DIR, orig_basename)
                
                if not os.path.exists(orig_path):
                    orig_path = os.path.join(BKP_DIR, orig_basename)
                
                orig_data = None
                if os.path.exists(orig_path):
                    with open(orig_path, 'r', encoding='utf-8') as f:
                        orig_data = json.load(f)
                else:
                    print(f"    ⚠️  Original não encontrado para parte {part_num}")
                
                pt_pubs = pt_data.get("publications", [])
                orig_pubs = orig_data.get("publications", []) if orig_data else []
                
                # Criar mapa de publicações originais por índice para matching
                orig_map = {pub.get("pub_idx", i): pub for i, pub in enumerate(orig_pubs)}
                
                merged_pubs = []
                for i, pt_pub in enumerate(pt_pubs):
                    # Tentar encontrar publicação original correspondente
                    pub_idx = pt_pub.get("pub_idx", i)
                    orig_pub = orig_map.get(pub_idx, {})
                    
                    # Combinar campos: JP do original, PT do traduzido
                    merged_pub = {
                        "title": orig_pub.get("title") or pt_pub.get("title", ""),
                        "title_ptbr": pt_pub.get("title_ptbr", ""),
                        "publication_title": orig_pub.get("publication_title") or pt_pub.get("publication_title", ""),
                        "publication_title_ptbr": pt_pub.get("publication_title_ptbr", ""),
                        "content": orig_pub.get("content", ""),  # JP do original
                        "content_ptbr": pt_pub.get("content_ptbr", ""),  # PT do traduzido
                        "date": pt_pub.get("date", ""),
                        "has_translation": bool(pt_pub.get("content_ptbr")),
                        "pub_idx": pub_idx
                    }

                    # SEGURANÇA: Verificar se o título original informado pelo LLM bate com o arquivo original
                    # Isso evita merges desalinhados (Ex: Parte 39 PT misturada com Parte 44 JP)
                    llm_orig_title = pt_pub.get("original_title", "").strip()
                    file_orig_title = orig_pub.get("publication_title", "").strip()
                    
                    if llm_orig_title and file_orig_title:
                        # Normalizar (remover espaços e pontuação básica) para comparação segura
                        def simple_norm(t): return t.replace(" ", "").replace("　", "")
                        
                        if simple_norm(llm_orig_title) != simple_norm(file_orig_title):
                            print(f"    ⚠️  ALERTA DE ALINHAMENTO (Parte {part_num}, Pub {pub_idx}):")
                            print(f"       LLM diz ser: '{llm_orig_title}'")
                            print(f"       Arquivo é:   '{file_orig_title}'")
                            # Não abortamos, mas o log avisará sobre o risco.
                    
                    merged_pubs.append(merged_pub)
                
                all_publications.extend(merged_pubs)
                print(f"    Parte {part_num}: {len(merged_pubs)} publicações bilíngues")
                
            except Exception as e:
                print(f"    ERRO ao processar parte {part_num}: {e}")
        
        if metadata and all_publications:
            # Criar arquivo merged
            merged_data = {
                "source_file": f"{theme_key}_merged.json",
                "volume": metadata["volume"],
                "theme_name": metadata["theme_name"],
                "theme_name_ptbr": metadata["theme_name_ptbr"],
                "total_publications": len(all_publications),
                "publications": all_publications
            }
            
            merged_path = os.path.join(TEMAS_DIR, f"{theme_key}_merged.json")
            with open(merged_path, 'w', encoding='utf-8') as f:
                json.dump(merged_data, f, ensure_ascii=False, indent=2)
            
            print(f"    -> Criado: {theme_key}_merged.json ({len(all_publications)} publicações bilíngues)")
            merged_count += 1
    
    print(f"\n  Total de arquivos merged criados: {merged_count}")
    return merged_count


def step3_move_to_backup():
    """Move arquivos _pt.json e partes originais para bkp/"""
    print("\n" + "="*60)
    print("ETAPA 3: Movendo arquivos processados para bkp/")
    print("="*60)
    
    os.makedirs(BKP_DIR, exist_ok=True)
    
    # Encontrar temas que foram merged (para saber quais partes mover)
    merged_files = glob.glob(os.path.join(TEMAS_DIR, "*_merged.json"))
    
    total_moved = 0
    
    for merged_path in merged_files:
        basename = os.path.basename(merged_path)
        if not basename.endswith("_merged.json"):
            continue
        
        theme_key = basename[:-12]  # Remove "_merged.json"
        
        # Mover todas as partes deste tema
        pattern = os.path.join(PARTES_DIR, f"{theme_key}_parte*")
        parts = glob.glob(pattern)
        
        for part_path in parts:
            part_basename = os.path.basename(part_path)
            dest_path = os.path.join(BKP_DIR, part_basename)
            
            try:
                shutil.move(part_path, dest_path)
                print(f"  {part_basename} -> bkp/")
                total_moved += 1
            except Exception as e:
                print(f"  ERRO ao mover {part_basename}: {e}")
    
    print(f"\n  Total movido: {total_moved}")
    return total_moved


def step4_regenerate_main_json():
    """Regenera shin_college_data.json a partir dos arquivos merged"""
    print("\n" + "="*60)
    print("ETAPA 4: Regenerando shin_college_data.json")
    print("="*60)
    
    merged_files = sorted(glob.glob(os.path.join(TEMAS_DIR, "*_merged.json")))
    
    if not merged_files:
        print("  Nenhum arquivo merged encontrado!")
        return False
    
    print(f"  Encontrados {len(merged_files)} arquivos merged.")
    
    volumes_map = {}
    
    for file_path in merged_files:
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                merged_data = json.load(f)
            
            raw_vol_name = merged_data.get("volume", "")
            vol_ptbr = VOLUME_MAP.get(raw_vol_name, raw_vol_name)
            
            theme_name = merged_data.get("theme_name")
            theme_name_ptbr = merged_data.get("theme_name_ptbr", "")
            
            if not raw_vol_name or not theme_name:
                continue
            
            flattened_pubs = merged_data.get("publications", [])
            titles_map = {}
            titles_order = []
            
            for pub in flattened_pubs:
                t_title = pub.get("title")
                
                if t_title not in titles_map:
                    titles_map[t_title] = {
                        "title": t_title,
                        "title_ptbr": pub.get("title_ptbr", ""),
                        "publications": []
                    }
                    titles_order.append(t_title)
                
                new_pub = {
                    "publication_title": pub.get("publication_title", ""),
                    "publication_title_ptbr": pub.get("publication_title_ptbr", ""),
                    "content": pub.get("content", ""),
                    "content_ptbr": pub.get("content_ptbr", ""),
                    "date": pub.get("date", ""),
                    "has_translation": pub.get("has_translation", bool(pub.get("content_ptbr"))),
                    "pub_idx": pub.get("pub_idx", 0)
                }
                titles_map[t_title]["publications"].append(new_pub)
            
            new_titles_list = [titles_map[t] for t in titles_order]
            
            new_theme_obj = {
                "theme": theme_name,
                "theme_ptbr": theme_name_ptbr,
                "titles": new_titles_list
            }
            
            if raw_vol_name not in volumes_map:
                volumes_map[raw_vol_name] = {
                    "volume": raw_vol_name,
                    "volume_ptbr": vol_ptbr,
                    "themes": []
                }
            
            volumes_map[raw_vol_name]["themes"].append(new_theme_obj)
        
        except Exception as e:
            print(f"  ERRO ao processar {os.path.basename(file_path)}: {e}")
    
    final_volumes_list = sorted(volumes_map.values(), key=lambda x: x["volume"])
    
    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
        json.dump(final_volumes_list, f, ensure_ascii=False, indent=2)
    
    total_themes = sum(len(v["themes"]) for v in final_volumes_list)
    total_pubs = sum(
        len(t["publications"]) 
        for v in final_volumes_list 
        for th in v["themes"] 
        for t in th["titles"]
    )
    
    print(f"  Regenerado com sucesso!")
    print(f"    Volumes: {len(final_volumes_list)}")
    print(f"    Temas: {total_themes}")
    print(f"    Publicações: {total_pubs}")
    return True


def main():
    """Executa todas as 4 etapas em sequência"""
    print("\n" + "#"*60)
    print("# SCRIPT DE MERGE DE TRADUÇÕES")
    print("#"*60)
    
    # Etapa 1
    step1_rename_copy_to_pt()
    
    # Etapa 2
    # Etapa 2
    # Etapa 2
    import argparse
    parser = argparse.ArgumentParser(description='Merge de traduções e originais.')
    parser.add_argument('--filter', type=str, help='Filtrar por nome do tema (ex: "御神体とお光")')
    args = parser.parse_args()
    
    filter_arg = args.filter
    
    if filter_arg:
        print(f"!!! FILTRO ATIVO: Processando apenas temas contendo '{filter_arg}' !!!")
    
    step2_merge_parts(filter_theme=filter_arg)
    
    # Etapa 3
    step3_move_to_backup()
    
    # Etapa 4
    step4_regenerate_main_json()
    
    print("\n" + "#"*60)
    print("# MERGE CONCLUÍDO!")
    print("#"*60 + "\n")


if __name__ == "__main__":
    main()
