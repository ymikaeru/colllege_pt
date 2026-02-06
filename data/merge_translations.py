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

import json
import glob
import os
import shutil
import re
from collections import defaultdict

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


def step2_merge_parts():
    """Faz merge das partes (_pt) com as originais, criando _merged.json"""
    print("\n" + "="*60)
    print("ETAPA 2: Fazendo merge das partes por tema")
    print("="*60)
    
    # Encontrar todos os arquivos _pt.json
    pt_files = glob.glob(os.path.join(PARTES_DIR, "*_pt.json"))
    
    if not pt_files:
        print("  Nenhum arquivo '_pt.json' encontrado.")
        return 0
    
    # Agrupar por tema (prefixo antes de _parteXX)
    theme_groups = defaultdict(list)
    pattern = re.compile(r"^(.+?)_parte(\d+)(?:_pt)?\.json$")
    
    for pt_file in pt_files:
        basename = os.path.basename(pt_file)
        match = pattern.match(basename.replace("_pt.json", ".json"))
        if match:
            theme_key = match.group(1)
            part_num = int(match.group(2))
            theme_groups[theme_key].append((part_num, pt_file))
    
    merged_count = 0
    
    for theme_key, parts in theme_groups.items():
        # Ordenar por número da parte
        parts.sort(key=lambda x: x[0])
        
        print(f"\n  Processando tema: {theme_key}")
        print(f"    {len(parts)} partes encontradas")
        
        # Carregar e mesclar todas as partes
        all_publications = []
        metadata = None
        
        for part_num, pt_path in parts:
            try:
                with open(pt_path, 'r', encoding='utf-8') as f:
                    pt_data = json.load(f)
                
                # Guardar metadados do primeiro arquivo
                if metadata is None:
                    metadata = {
                        "volume": pt_data.get("volume", ""),
                        "theme_name": pt_data.get("theme_name", ""),
                        "theme_name_ptbr": pt_data.get("theme_name_ptbr", ""),
                    }
                
                # Adicionar publicações
                pubs = pt_data.get("publications", [])
                all_publications.extend(pubs)
                print(f"    Parte {part_num}: {len(pubs)} publicações")
                
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
            
            print(f"    -> Criado: {theme_key}_merged.json ({len(all_publications)} publicações)")
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
            
            if not vol_name or not theme_name:
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
    step2_merge_parts()
    
    # Etapa 3
    step3_move_to_backup()
    
    # Etapa 4
    step4_regenerate_main_json()
    
    print("\n" + "#"*60)
    print("# MERGE CONCLUÍDO!")
    print("#"*60 + "\n")


if __name__ == "__main__":
    main()
