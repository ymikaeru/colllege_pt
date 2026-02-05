import json
import re
import os
import glob

# Configuration
JSON_PATH = "/Users/michael/Documents/Ensinamentos/Sites/ShinCollege_Pt/data/shin_college_data_translated.json"
MARKDOWN_DIR = "/Users/michael/Documents/Ensinamentos/Sites/ShinCollege_Pt/TranslatedMarkdown"

# Regex Patterns
# Filename: "Deus e o Plano Divino(神と経綸).md" -> Group 1: PT, Group 2: JP
FILENAME_PATTERN = re.compile(r'^(.*)\((.*)\)\.md$')

# Header: "# 15.Sobre Kanzeon... (Orig.: 観世音...)"
# Group 2: PT Title (approx), Group 3: JP Title
HEADER_PATTERN = re.compile(r'^#+\s*(\d+[\.\s]*)?(.*?)\s*\(Orig\.:\s*(.*?)\)\s*$', re.IGNORECASE)

# Manual Theme Map for common sections that might not have matching filenames
MANUAL_THEME_MAP = {
    "序文": "Introdução",
    "神と経綸": "Deus e o Plano Divino",
    "霊主体従": "Espírito Precede a Matéria",
    "霊界の構成": "Constituição do Mundo Espiritual",
    "諸霊の活動": "Atuação dos Espíritos",
    "夜昼転換と最後の審判": "Transição Noite-Dia e o Juízo Final",
    "御神格": "Divindade",
    "正神と邪神": "Deus Verdadeiro e Deus Maligno",
    "祖霊祭祀": "Culto aos Antepassados", 
    "浄霊の原理": "Princípio do Johrei",
    "浄霊の方法": "Método de Johrei",
    "浄化作用": "Ação de Purificação",
    "三　毒": "Três Toxinas",
    "病気の体的分析": "Análise Física da Doença",
    "病気の霊的分析": "Análise Espiritual da Doença",
    "現代医学批判": "Crítica à Medicina Moderna",
    "神示の健康法": "Método de Saúde Revelado por Deus",
    "自然農法": "Agricultura Natural",
    "真理": "Verdade",
    "幸福を生む宗教": "Religião que Gera Felicidade",
    "信仰地獄": "Inferno da Fé",
    "信仰生活の道標": "Guia da Vida de Fé",
    "信仰と社会生活": "Fé e Vida Social",
    "信仰と家庭生活": "Fé e Vida Familiar",
    "罪と徳": "Pecado e Virtude",
    "御神業の心得": "Atitude na Obra Divina",
    "御神体とお光": "Imagem Divina e Ohikari",
    "明主様の御事跡": "Feitos de Meishu-Sama",
    "地上天国の雛形建設": "Construção do Modelo do Paraíso Terrestre",
    "外野の無理解": "Incompreensão de Terceiros", 
    "宗教断片集": "Fragmentos Religiosos",
    "森羅万象の解析": "Análise de Todas as Coisas",
    "芸術について": "Sobre a Arte",
    "時局について": "Sobre a Situação Atual",
    "その他": "Outros"
}

MANUAL_TITLE_MAP = {
    "御神体の奇瑞１": "Milagres da Imagem Divina 1",
    "御神体の奇瑞２": "Milagres da Imagem Divina 2",
    "御神体の奇瑞について１": "Milagres da Imagem Divina 1",
    "御神体の奇瑞について２": "Milagres da Imagem Divina 2"
}

def normalize_text(text):
    if not text: return ""
    return re.sub(r'\s+', '', text).strip()

def main():
    print(f"Loading JSON from {JSON_PATH}...")
    with open(JSON_PATH, 'r', encoding='utf-8') as f:
        data = json.load(f)

    # 1. Build Translation Map from Markdown Files
    markdown_files = glob.glob(os.path.join(MARKDOWN_DIR, "*.md"))
    
    theme_map = {} # { JP_Theme_Normalized: PT_Theme }
    title_map = {} # { JP_Title_Normalized: PT_Title }
    
    # Pre-populate with Manual Map
    for jp, pt in MANUAL_THEME_MAP.items():
        theme_map[normalize_text(jp)] = pt

    print(f"Scanning {len(markdown_files)} markdown files...")

    for md_path in markdown_files:
        basename = os.path.basename(md_path)
        
        # A. Theme Translation from Filename
        match_filename = FILENAME_PATTERN.match(basename)
        if match_filename:
            pt_theme = match_filename.group(1).strip()
            jp_theme = match_filename.group(2).strip()
            theme_map[normalize_text(jp_theme)] = pt_theme
            print(f"Found Theme: {jp_theme} -> {pt_theme}")

        # B. Title Translation from Headers
        with open(md_path, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if not line.startswith('#'): continue
                
                match_header = HEADER_PATTERN.match(line)
                if match_header:
                    # group(1) is number (optional), group(2) is PT title, group(3) is JP title
                    pt_title_raw = match_header.group(2).strip()
                    jp_title_raw = match_header.group(3).strip()
                    
                    # Clean up parens in JP title if any remain (though regex shouldn't catch them ideally)
                    jp_clean = jp_title_raw.strip('()')
                    
                    title_map[normalize_text(jp_clean)] = pt_title_raw
                    # print(f"  Found Title: {jp_clean} -> {pt_title_raw}")

    print(f"Built map with {len(theme_map)} themes and {len(title_map)} titles.")

    # 2. Update JSON
    updates_count = 0
    
    for volume in data:
        # Check Themes
        for theme in volume.get('themes', []):
            jp_theme = theme.get('theme')
            if jp_theme:
                norm_theme = normalize_text(jp_theme)
                if "御神体とお光" in jp_theme:
                     print(f"DEBUG: Found theme '{jp_theme}', Norm: '{norm_theme}', In Map: {norm_theme in theme_map}")
                     if norm_theme in theme_map:
                         print(f"DEBUG: Map Value: '{theme_map[norm_theme]}', Current JSON Value: '{theme.get('theme_ptbr')}'")

                if norm_theme in theme_map:
                    if theme.get('theme_ptbr') != theme_map[norm_theme]:
                        theme['theme_ptbr'] = theme_map[norm_theme]
                        updates_count += 1
                        print(f"Updated Theme: {jp_theme} -> {theme['theme_ptbr']}")

            # Check Titles
            for title_group in theme.get('titles', []):
                jp_title = title_group.get('title')
                if jp_title:
                    norm_title = normalize_text(jp_title)
                    
                    # 1. Try Manual Title Map
                    if norm_title in MANUAL_TITLE_MAP:
                         if title_group.get('title_ptbr') != MANUAL_TITLE_MAP[norm_title]:
                            title_group['title_ptbr'] = MANUAL_TITLE_MAP[norm_title]
                            updates_count += 1
                            print(f"Updated Title (Manual Map): {jp_title} -> {title_group['title_ptbr']}")

                    # 2. Try Markdown Map
                    elif norm_title in title_map:
                         if title_group.get('title_ptbr') != title_map[norm_title]:
                            title_group['title_ptbr'] = title_map[norm_title]
                            updates_count += 1
                            print(f"Updated Title (Markdown Map): {jp_title} -> {title_group['title_ptbr']}")
                    else:
                        # 3. Heuristic: If Title starts with Theme Name (JP), replace with Theme Name (PT)
                        # e.g. JP Theme: "神と経綸", PT Theme: "Deus e o Plano Divino"
                        # JP Title: "神と経綸　１" -> PT Title: "Deus e o Plano Divino 1"
                        
                        if jp_theme and jp_theme in theme_map:
                            pt_theme_base = theme_map[normalize_text(jp_theme)]
                             # Check if title strictly starts with JP theme
                            if jp_title.startswith(jp_theme):
                                suffix = jp_title[len(jp_theme):]
                                # Clean suffix (full width space -> space, etc)
                                suffix = suffix.replace('　', ' ').strip()
                                # Normalize full-width numbers
                                suffix = suffix.translate(str.maketrans('０１２３４５６７８９', '0123456789'))
                                
                                new_pt_title = f"{pt_theme_base} {suffix}".strip()
                                
                                # Only apply if it looks like a numbered suffix or empty
                                # Avoid replacing "God and Plan" in "God and Plan Overview" if "Overview" wasn't translated?
                                # Actually, usually it's just numbers " 1", " 2".
                                
                                title_group['title_ptbr'] = new_pt_title
                                updates_count += 1
                                print(f"Updated Title (Heuristic): {jp_title} -> {new_pt_title}")

    print(f"Total Updates: {updates_count}")
    
    # 3. Save
    if updates_count > 0:
        print(f"Saving updated JSON to {JSON_PATH}...")
        with open(JSON_PATH, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    else:
        print("No updates needed.")

if __name__ == "__main__":
    main()
