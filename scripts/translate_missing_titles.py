import json
import os
import subprocess

MAIN_JSON = "data/shin_college_data.json"
REGENERATE_SCRIPT = "scripts/regenerate_separated_json.py"

TRANSLATIONS = {
    "御神体の奇瑞": "Milagres do Goshintai",
    "御神体と奇象": "Goshintai e Fenômenos Estranhos",
    "御神体の意義": "Significado do Goshintai",
    "御神体奉斎の意義": "Significado de Entronizar o Goshintai",
    "御神体奉斎と薬毒病": "Entronização do Goshintai e Doenças por Toxinas de Remédios",
    "御神体奉斎と知的障害": "Entronização do Goshintai e Deficiência Intelectual",
    "御神体奉斎と精神病": "Entronização do Goshintai e Doenças Mentais",
    "御神体奉斎と憑霊現象": "Entronização do Goshintai e Fenômenos de Possessão Espiritual",
    "御神体奉斎と祟り": "Entronização do Goshintai e Encosto Espiritual (Tatari)",
    "御神体奉斎と墓地、処刑場、社寺跡地": "Entronização do Goshintai e Cemitérios, Locais de Execução e Ruínas de Templos",
    "御神体奉斎と罪": "Entronização do Goshintai e Pecado",
    "御神体奉斎と墓供養の因縁": "Entronização do Goshintai e Afinidade com Sufrágio aos Túmulos",
    "御神体奉斎と祖霊": "Entronização do Goshintai e Ancestrais",
    "御神体奉斎と仏壇": "Entronização do Goshintai e Oratório Budista",
    "御神体奉斎と神棚": "Entronização do Goshintai e Altar Xintoísta",
    "御神体の取り扱い": "Manuseio do Goshintai",
    "御神体の位置": "Posição do Goshintai",
    "御神体と方位": "Goshintai e Direção",
    "御神体の拝受": "Recebimento do Goshintai",
    "御神体の汚損": "Danos e Sujeira no Goshintai",
    "御神体の仮巻": "Montagem Provisória do Goshintai",
    "御屏風観音様": "Biombo de Kannon",
    "御写真": "Foto Sagrada (Goshashin)",
    "お光": "Ohikari",
    "お光の意義": "Significado do Ohikari",
    "お光と奇瑞": "Ohikari e Milagres",
    "お光と霊的現象": "Ohikari e Fenômenos Espirituais",
    "お光の授与": "Outorga do Ohikari",
    "お光の取り扱い": "Manuseio do Ohikari",
    "お光と紛失": "Perda do Ohikari",
    "お光と紐": "Ohikari e o Cordão",
    "お光と袋": "Ohikari e o Saquinho",
    "お守り": "Omamori (Amuleto)",
    "お屏風観音様": "Biombo de Kannon",
    "御神体奉斎による浄化": "Purificação pela Entronização do Goshintai",
    "御書体": "Goshotai",
    "御書体の作法": "Etiqueta do Goshotai",
    "御書体の奇瑞": "Milagres do Goshotai",
    "明主様の御写真": "Foto Sagrada de Meishu-Sama",
    "お光の奇瑞": "Milagres do Ohikari",
    "お光の作法": "Etiqueta do Ohikari",
    "お光に対する粗相": "Descuido com o Ohikari",
    "お光の企画案": "Projetos sobre o Ohikari",
    "お光の忌避": "Evitar o Ohikari",
    "妊婦の御腹帯": "Cinta para Grávidas (Obi)",
    "御霊紙": "Papel Espiritual (Mitama-gami)"
}

def main():
    print(f"Loading {MAIN_JSON}...")
    try:
        with open(MAIN_JSON, 'r', encoding='utf-8') as f:
            data = json.load(f)
    except Exception as e:
        print(f"Error loading JSON: {e}")
        return

    updated_count = 0
    
    for volume in data:
        for theme in volume.get('themes', []):
            if theme.get('theme') == "御神体とお光":
                for title_group in theme.get('titles', []):
                    jp_title = title_group.get('title', '')
                    # Normalize simple variations if needed, but exact match first
                    clean_title = jp_title.replace("　", " ").strip()
                    # Check mapping
                    # Try exact match first
                    pt_trans = TRANSLATIONS.get(clean_title)
                    
                    # Try partial match (some have numbers like "御神体の奇瑞　１")
                    if not pt_trans:
                        # Remove trailing numbers for lookup
                        import re
                        base_title = re.sub(r'[\s　]+[0-9１-９]+.*$', '', clean_title)
                        pt_trans = TRANSLATIONS.get(base_title)
                    
                    if pt_trans:
                        current_pt = title_group.get('title_ptbr', '')
                        if not current_pt:
                            title_group['title_ptbr'] = pt_trans
                            print(f"Updated: {jp_title} -> {pt_trans}")
                            updated_count += 1
                        else:
                             print(f"Skipping (already has trans): {jp_title} -> {current_pt}")
                    else:
                        print(f"Warning: No translation found for '{jp_title}'")

    if updated_count > 0:
        print(f"Saving {updated_count} updates to {MAIN_JSON}...")
        with open(MAIN_JSON, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=4)
        
        print("Regenerating separated JSONs...")
        subprocess.run(["python3", REGENERATE_SCRIPT], check=True)
    else:
        print("No updates needed.")

if __name__ == "__main__":
    main()
