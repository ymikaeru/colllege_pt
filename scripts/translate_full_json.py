import json
import os
import time
import argparse
import threading
import concurrent.futures
import google.generativeai as genai
from google.api_core import exceptions

# --- CONFIGURATION ---
API_KEY = os.environ.get("GEMINI_API_KEY")

# --- PROMPT ADAPTATION ---
SYSTEM_INSTRUCTION = """
# PERSONA E PAPEL
Atue como um tradutor sênior e devoto da Sekaikyuseikyou, com foco em fidelidade documental. Sua missão é traduzir textos do japonês para o português do Brasil (PT-BR).

# DIRETRIZES DE TRADUÇÃO (ESTILO E TOM)
* **Fluidez Gramatical:** Abandone a sintaxe japonesa, reescrevendo com a estrutura gramatical natural do português culto.
* **Vocabulário Elevado:** Utilize um vocabulário rico e preciso, condizente com a dignidade de Meishu-Sama.
* **Não-Interferência de Conteúdo:** A fluidez deve se aplicar apenas à forma, jamais ao conteúdo. Não "melhore" ou "atualize" fatos históricos.

# REGRAS DE TERMINOLOGIA
1. **Tradução Prioritária:** Traduza termos para o português, exceto nomes próprios e locais.
2. **Exceções Técnicas:** Termos intraduzíveis seguem o formato: Termo em Romaji (Kanji Original). Ex: Kannon (観音).
3. **Títulos e Publicações:** Nomes de livros/revistas ficam APENAS em Romaji (ex: Tijou Tengoku).
4. **Fidelidade Estrita:** Se o texto citar um nome/termo (ex: "Miroku-kai"), mantenha-o exatamente como está. Traduza o que está escrito.

# FORMATAÇÃO DE SAÍDA
* Retorne APENAS o texto traduzido.
* Não use blocos de código (```) na resposta, apenas o texto cru.
* Não inclua notas ou comentários.
"""

def setup_gemini():
    if not API_KEY:
        print("Erro: GEMINI_API_KEY não encontrada nas variáveis de ambiente.")
        return None
    genai.configure(api_key=API_KEY)
    # Using a model suitable for translation - gemini-1.5-pro or flash usually good. 
    # User's previous script used 'gemini-2.5-pro' (likely a placeholder or typo in previous context, checking available models usually good, but let's stick to standard names or what was in previous file if valid. Previous file had 'gemini-2.5-pro', assumming typo and using 'gemini-1.5-pro' as safe bet, or 'gemini-pro').
    # Actually, let's use 'gemini-2.0-flash-exp' if available, or 'gemini-1.5-flash'. 
    # Valid model found from list_models
    return genai.GenerativeModel('gemini-2.5-pro')

SYSTEM_INSTRUCTION_BASE = """
Atue como um tradutor sênior e devoto da Sekaikyuseikyou.
Objetivo: Traduzir do Japonês para o Português do Brasil (PT-BR).

CRÍTICO:
1. Retorne APENAS o texto traduzido final.
2. NÃO inclua introduções como "Aqui está a tradução", "Com a Luz de Deus", etc.
3. NÃO explique sua tradução.
4. NÃO use aspas ao redor do texto, a menos que o original tenha.
"""

def translate_text(model, text, field_type="generic"):
    if not text or not isinstance(text, str) or len(text.strip()) == 0:
        return text

    elif field_type == "theme":
        prompt = f"""
{SYSTEM_INSTRUCTION_BASE}
**Tarefa:** Traduza o Tema.
Regra Específica: '御神体とお光' DEVE ser 'Imagem Sagrada e Luz Divina'.
Retorne APENAS a tradução.

Texto Original:
{text}
"""
    elif field_type == "title":
        prompt = f"""
{SYSTEM_INSTRUCTION_BASE}
**Tarefa:** Traduza o Título do Grupo.
Regra Específica: '御神体' DEVE ser 'Imagem Sagrada'.
Retorne APENAS a tradução.

Texto Original:
{text}
"""
    elif field_type == "date":
        prompt = f"""
{SYSTEM_INSTRUCTION_BASE}
**Tarefa:** Converta a data japonesa para o formato ocidental (Dia de Mês de Ano).
Exemplo: '昭和10年5月21日' -> '21 de Maio de 1935'.
Se não for uma data clara, traduza normalmente.
Retorne APENAS a data convertida.

Texto Original:
{text}
"""
    elif field_type == "publication_title": # This is the ARTICLE title in the JSON structure
        prompt = f"""
{SYSTEM_INSTRUCTION_BASE}
**Tarefa:** Traduza o Título do Artigo/Ensinamento.
Regra: Mantenha o título original japonês (EM KANJI/KANA) entre parênteses ao final.
NÃO use Romaji nos parênteses.
Formato: Título em Português (Título Original)
Exemplo: A Atividade da Luz (光の活動)
NÃO coloque introduções.

Texto Original:
{text}
"""
    elif field_type == "source": # This is the BOOK/MAGAZINE name
        prompt = f"""
{SYSTEM_INSTRUCTION_BASE}
**Tarefa:** Converter o nome da Publicação/Fonte para Romaji.
NÃO traduza o significado. Transcreva para o alfabeto latino (Romaji).
Exemplo: '地上天国' -> 'Tijou Tengoku'.
Regra Específica: '明主様御教え' DEVE ser 'Meishu-sama Mioshie'.
Retorne APENAS o Romaji.

Texto Original:
{text}
"""
    elif field_type == "content":
        prompt = f"""
{SYSTEM_INSTRUCTION_BASE}
**Diretrizes:**
1. Fluidez gramatical natural em PT-BR (culto).
2. Vocabulário elevado.
3. Fidelidade ao conteúdo (não altere fatos).
4. Termos técnicos: Traduza, exceto 'Kannon' (観音) e nomes próprios.
5. Formatação: Retorne apenas o texto traduzido. SEM COMENTÁRIOS EXTRAS.

Texto Original:
{text}
"""
    else: # Generic
        prompt = f"""
{SYSTEM_INSTRUCTION_BASE}
Traduza o seguinte termo/frase para PT-BR.
Retorne APENAS a tradução.

Texto Original:
{text}
"""

    try:
        response = model.generate_content(
            contents=[prompt],
            generation_config=genai.types.GenerationConfig(
                temperature=0.3, 
            )
        )
        return response.text.strip()
    except Exception as e:
        print(f"Error translating text: {e}")
        return None

def process_item(item, model, stats_lock, stats):
    # Translate fields relevant to the structure
    # Volume, Theme, Title, Publication content
    
    # Note: Structure is nested. 
    # This function processes a single node. 
    # Since the JSON is hierarchical, we might need a recursive approach outside or inside.
    # However, to parallelize, we usually collect all "leaf" nodes (Publications) and translate them.
    # But Volume/Theme/Title titles also need translation.
    
    changed = False

    # Helper to translate a specific key
    def translate_field(key):
        val = item.get(key)
        # Check if it needs translation (contains Japanese characters?)
        # For now, just translate if present and strictly string
        if val and isinstance(val, str) and not item.get(f"{key}_ptbr"):
             # Heuristic: Check for Japanese characters to avoid re-translating English/PT
             # For 'source' or 'date', we might want to process even if no Japanese chars are obvious?
             # But 'date' usually has japanese chars. 'source' definitely.
             if any(ord(char) > 0x2E80 for char in val):
                translated = translate_text(model, val, field_type=key)
                if translated:
                    item[f"{key}_ptbr"] = translated
                    return True
        return False

    # Translate specific metadata fields if they exist at this level
    if translate_field("volume"): changed = True
    if translate_field("theme"): changed = True
    if translate_field("title"): changed = True
    if translate_field("publication_title"): changed = True
    if translate_field("source"): changed = True
    if translate_field("date"): changed = True # date was missing in previous list
    
    # Translate Main Content
    if "content" in item:
        if translate_field("content"): changed = True

    if changed:
        # Reorder keys to keep translations adjacent to source
        # This is purely for JSON readability
        try:
             order = list(item.keys())
             # Filter out _ptbr keys from the iteration list to avoid duplication if we construct new dict
             # Actually, simpler way: create new dict, iterate known order or current keys
             new_map = {}
             # We want to preserve original insertion order roughly, but pull _ptbr up
             # The keys in 'item' might be unordered effectively depending on python version history, 
             # but usually insertion order.
             # 'item' keys: 'title', 'publications', 'title_ptbr' ...
             
             # Collect base keys (excluding _ptbr)
             base_keys = [k for k in item.keys() if not k.endswith("_ptbr")]
             
             for k in base_keys:
                 new_map[k] = item[k]
                 if f"{k}_ptbr" in item:
                     new_map[f"{k}_ptbr"] = item[f"{k}_ptbr"]
             
             # If there were any _ptbr keys whose base key wasn't found (orphan?), add them?
             # Unlikely in this script.
             
             item.clear()
             item.update(new_map)
        except Exception as e:
            print(f"Error reordering keys: {e}")

        with stats_lock:
            stats["count"] += 1
            if stats["count"] % 10 == 0:
                print(f"Translated {stats['count']} items...", flush=True)

    return changed

def traverse_and_collect(data, collector):
    if isinstance(data, list):
        for item in data:
            traverse_and_collect(item, collector)
    elif isinstance(data, dict):
        collector.append(data)
        # Recurse into known children lists
        if "themes" in data:
            traverse_and_collect(data["themes"], collector)
        if "titles" in data:
            traverse_and_collect(data["titles"], collector)
        if "publications" in data:
            traverse_and_collect(data["publications"], collector)

def main():
    parser = argparse.ArgumentParser(description="Translate JSON content using Gemini.")
    parser.add_argument("--input", default="data/shin_college_data.json", help="Input JSON file")
    parser.add_argument("--output", default="data/shin_college_data_translated.json", help="Output JSON file")
    parser.add_argument("--limit", type=int, default=0, help="Limit number of items to translate (for testing)")
    parser.add_argument("--workers", type=int, default=5, help="Number of concurrent workers")
    parser.add_argument("--filter-theme", type=str, default=None, help="Process only specific theme")
    parser.add_argument("--filter-volume", type=str, default=None, help="Process only specific volume")
    args = parser.parse_args()

    model = setup_gemini()
    if not model:
        return

    print(f"Loading {args.input}...")
    try:
        with open(args.input, "r", encoding="utf-8") as f:
            data = json.load(f)
    except FileNotFoundError:
        print("Input file not found.")
        return

    # Collect all dict objects that might need translation
    all_dicts = []
    
    # Custom traversal to respect theme/volume filter
    def collect_with_filter(node, current_volume=None, current_theme=None):
        if isinstance(node, list):
            for item in node:
                collect_with_filter(item, current_volume, current_theme)
        elif isinstance(node, dict):
            # Update current volume if we are at a volume node
            if "volume" in node and isinstance(node["volume"], str):
                current_volume = node["volume"]

            # Update current theme if we are at a theme node
            if "theme" in node and isinstance(node["theme"], str):
                current_theme = node["theme"]
            
            # --- FILTERING LOGIC ---
            passed_filter = True
            
            # Volume Filter
            if args.filter_volume:
                if current_volume != args.filter_volume:
                    passed_filter = False
                    # Optimization: If at volume level and mismatch, stop recursion
                    if "volume" in node and node["volume"] != args.filter_volume:
                        return 

            # Theme Filter (only if passed volume filter)
            if passed_filter and args.filter_theme:
                # If specifically filtered by theme, we need to match it
                # Note: Theme filter applies globally or within volume if both set
                if current_theme != args.filter_theme:
                     passed_filter = False
                     if "theme" in node and node["theme"] != args.filter_theme:
                         return

            if passed_filter:
                 all_dicts.append(node)

            if "themes" in node:
                collect_with_filter(node["themes"], current_volume, current_theme)
            if "titles" in node:
                collect_with_filter(node["titles"], current_volume, current_theme)
            if "publications" in node:
                collect_with_filter(node["publications"], current_volume, current_theme)

    collect_with_filter(data)
    
    print(f"Found {len(all_dicts)} recursive nodes in JSON.")

    # Filter dicts that actually have content to translate and haven't been translated
    targets = []
    for d in all_dicts:
        needs_translation = False
        possible_keys = ["volume", "theme", "title", "publication_title", "source", "content"]
        for k in possible_keys:
            if k in d and isinstance(d[k], str) and any(ord(c) > 0x2E80 for c in d[k]):
                # Check if already translated
                if f"{k}_ptbr" not in d:
                    needs_translation = True
                    break
        if needs_translation:
            targets.append(d)

    print(f"Targets needing translation: {len(targets)}")

    if args.limit > 0:
        targets = targets[:args.limit]
        print(f"Limiting to first {args.limit} targets.")

    stats = {"count": 0}
    stats_lock = threading.Lock()

    print("Starting translation...")
    with concurrent.futures.ThreadPoolExecutor(max_workers=args.workers) as executor:
        # Process futures and save periodically
        futures = [executor.submit(process_item, item, model, stats_lock, stats) for item in targets]
        
        last_save_count = 0
        total_targets = len(targets)
        
        while True:
            # Check status every 5 seconds
            time.sleep(5)
            
            # Check if all tasks are done
            all_done = all(f.done() for f in futures)
            
            with stats_lock:
                current_count = stats["count"]
            
            # Save if enough items processed or if finished
            if (current_count - last_save_count >= 5) or (all_done and current_count > last_save_count):
                print(f"Saving progress ({current_count}/{total_targets} translated)...")
                with open(args.output, "w", encoding="utf-8") as f:
                    json.dump(data, f, ensure_ascii=False, indent=2)
                last_save_count = current_count
            
            if all_done:
                break

    print(f"Translation finished. Saving to {args.output}...")
    with open(args.output, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    print("Done.")

if __name__ == "__main__":
    main()
