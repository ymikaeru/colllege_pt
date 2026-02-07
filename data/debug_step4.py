
import json
import glob
import os

TEMAS_DIR = "/Users/michael/Documents/Ensinamentos/Sites/ShinCollege_Pt/data/temasSeparados"
VOLUME_MAP = {
    "1.経綸・霊主体従・夜昼転換・祖霊祭祀編": "1. Plano Divino...",
    "3.信仰編": "3. Seção da Fé",
    "4.その他": "4. Outros",
}

def debug_step4():
    merged_files = sorted(glob.glob(os.path.join(TEMAS_DIR, "*_merged.json")))
    volumes_map = {}
    
    total_input_pubs = 0
    total_output_pubs = 0
    
    print(f"Processando {len(merged_files)} arquivos merged...")
    
    for file_path in merged_files:
        basename = os.path.basename(file_path)
        with open(file_path, 'r', encoding='utf-8') as f:
            merged_data = json.load(f)
            
        flattened_pubs = merged_data.get("publications", [])
        input_count = len(flattened_pubs)
        total_input_pubs += input_count
        
        print(f"\nArquivo: {basename} (Docs: {input_count})")
        
        raw_vol_name = merged_data.get("volume", "")
        theme_name = merged_data.get("theme_name")
        
        if not raw_vol_name or not theme_name:
            print("  ❌ SKIPPING: Missing volume or theme name")
            continue
            
        titles_map = {}
        processed_count = 0
        
        for pub in flattened_pubs:
            t_title = pub.get("title")
            
            # The logic in merge_translations.py:
            if t_title not in titles_map:
                titles_map[t_title] = [] # simplified for debug
            
            titles_map[t_title].append(pub)
            processed_count += 1
            
        print(f"  Processed into titles map: {processed_count}")
        
        # Simulating the volume structure
        if raw_vol_name not in volumes_map:
            volumes_map[raw_vol_name] = []
        
        volumes_map[raw_vol_name].append(processed_count)
        
    print(f"\nTotal Input: {total_input_pubs}")
    
    # Calculate total output in structure
    final_count = sum([sum(counts) for counts in volumes_map.values()])
    print(f"Total Output (Simulated): {final_count}")

if __name__ == "__main__":
    debug_step4()
