
import json
import re
import os
import glob
from datetime import datetime

# Configuration
JSON_PATH = "/Users/michael/Documents/Ensinamentos/Sites/ShinCollege_Pt/data/shin_college_data_translated.json"
MARKDOWN_DIR = "/Users/michael/Documents/Ensinamentos/Sites/ShinCollege_Pt/TranslatedMarkdown"


# Regex patterns
HEADER_PATTERN = re.compile(r'^#{2,3}\s+(.*)')
# Pattern for explicit JP title: "JP Title" (PT Title) OR "PT Title" (JP Title)
# Also handles simple Text (Text) where one might be JP
TITLE_PAREN_PATTERN = re.compile(r'(.*?)\s*[\(（](.*?)[\)）]')
# Pattern for Date extraction from line: (Fonte: ..., 5 de setembro de 1948)
DATE_PATTERN = re.compile(r'(\d{1,2}|1º)\s+de\s+([a-zç]+)\s+de\s+(\d{4})', re.IGNORECASE)

MONTH_MAP = {
    'janeiro': 1, 'fevereiro': 2, 'março': 3, 'abril': 4, 'maio': 5, 'junho': 6,
    'julho': 7, 'agosto': 8, 'setembro': 9, 'outubro': 10, 'novembro': 11, 'dezembro': 12
}

def has_japanese_chars(text):
    return any('\u3000' <= char <= '\u9fff' for char in text)

def parse_japanese_date(date_str):
    """
    Parses strings like '昭和10年2月4日発行' to (1935, 2, 4)
    Returns tuple (year, month, day) or None
    """
    if not date_str:
        return None
    
    # Remove '発行' or similar tails
    clean_str = re.sub(r'発行.*', '', date_str).strip()
    
    # Match patterns like 昭和10年2月4日
    match = re.match(r'(昭和|大正|明治|平成|令和)(\d{1,2}|元)年(\d{1,2})月(\d{1,2})日', clean_str)
    if not match:
        return None
        
    era, era_year, month, day = match.groups()
    if era_year == '元':
        year_num = 1
    else:
        year_num = int(era_year)
        
    if era == '昭和':
        year = 1925 + year_num
    elif era == '大正':
        year = 1911 + year_num
    elif era == '明治':
        year = 1867 + year_num
    elif era == '平成':
        year = 1988 + year_num
    elif era == '令和':
        year = 2018 + year_num
    else:
        return None
        
    return (year, int(month), int(day))

def parse_portuguese_date(text):
    """
    Finds date in text like '... 5 de setembro de 1948 ...'
    Returns (1948, 9, 5) or None
    """
    match = DATE_PATTERN.search(text)
    if match:
        day_str, month_name, year = match.groups()
        month = MONTH_MAP.get(month_name.lower())
        day = 1 if day_str == '1º' else int(day_str)
        if month:
            return (int(year), month, day)
    return None

def extract_markdown_entries(file_path):
    with open(file_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()

    entries = []
    current_entry = None
    
    for i, line in enumerate(lines):
        line = line.strip()
        
        # Check for Header
        header_match = HEADER_PATTERN.match(line)
        if header_match:
            # Save previous entry if exists and has content
            if current_entry:
                entries.append(current_entry)
            
            raw_header = header_match.group(1)
            
            # Initialize new entry
            current_entry = {
                'jp_title': None,
                'pt_title': None,
                'date_tuple': None,
                'content_lines': [],
                'file_source': os.path.basename(file_path)
            }

            # Parse Metadata from Header
            # Format: Title (JP) | Source | Date
            parts = [p.strip() for p in raw_header.split('|')]
            title_part = parts[0]
            
            # Extract Date only from the last part if pipe exists
            if len(parts) > 1:
                last_part = parts[-1]
                # Regex for date: DD/MM/YYYY or similar
                date_match = re.search(r"(\d{1,2})[/\.-](\d{1,2})[/\.-](\d{2,4})", last_part)
                if date_match:
                     try:
                        day, month, year = int(date_match.group(1)), int(date_match.group(2)), int(date_match.group(3))
                        if year < 100: year += 1900 
                        current_entry['date_tuple'] = (year, month, day)
                     except ValueError:
                         pass

            # Analyze Title Part
            title_match = TITLE_PAREN_PATTERN.search(title_part)
            if title_match:
                part1 = title_match.group(1).strip('"“').strip()
                part2 = title_match.group(2).strip('"“').strip()
                
                if has_japanese_chars(part1):
                    current_entry['jp_title'] = part1
                    current_entry['pt_title'] = part2
                elif has_japanese_chars(part2):
                    current_entry['jp_title'] = part2
                    current_entry['pt_title'] = part1
                else:
                    current_entry['pt_title'] = part1 
            else:
                clean_title = re.sub(r'^(Palestra de Meishu-Sama|Ensinamento|Poema)[:：]?\s*', '', title_part, flags=re.IGNORECASE)
                current_entry['pt_title'] = clean_title.strip('"“').strip()

            # Fallback Date Parsing from Body will happen in loop
            
        # Check for Date in lines (Source line usually follows header)
        if current_entry and not current_entry['date_tuple']:
            date_tuple = parse_portuguese_date(line)
            if date_tuple:
                current_entry['date_tuple'] = date_tuple

        # Append content
        if current_entry and not header_match:
            if line.startswith('*(Fonte:') or line.startswith('(Fonte:') or line.startswith('Fonte:'):
                continue
            # Skip separator lines
            if line == '---' or line == '***':
                continue
                
            current_entry['content_lines'].append(line)

    if current_entry:
        entries.append(current_entry)
        
    # Post-process content
    for entry in entries:
        entry['content'] = '\n'.join(entry['content_lines']).strip()
        
    return entries

def main():
    # 1. Load JSON
    print(f"Loading JSON from {JSON_PATH}...")
    with open(JSON_PATH, 'r', encoding='utf-8') as f:
        data = json.load(f)

    # 2. Parse Markdowns
    markdown_files = glob.glob(os.path.join(MARKDOWN_DIR, "*.md"))
    all_entries = []
    print(f"Found {len(markdown_files)} markdown files.")
    
    seen_files = set()
    
    for md_file in markdown_files:
        basename = os.path.basename(md_file)
        # Skip duplicate files like '... (1).md'
        if re.search(r'\(\d+\)\.md$', basename):
            print(f"Skipping duplicate file: {basename}")
            continue
            
        print(f"Parsing {basename}...")
        entries = extract_markdown_entries(md_file)
        # Filter out empty entries (sometimes H2 followed immediately by H3 creates an empty H2 entry)
        valid_entries = [e for e in entries if e['content'] or e['jp_title']]
        all_entries.extend(valid_entries)
        print(f"  Found {len(valid_entries)} entries.")

    matches_count = 0
    
    # 3. Match and Update
    for entry in all_entries:
        match_found = False
        
        # Strategy 1: Match by Japanese Title (Exact)
        if entry['jp_title']:
            for volume in data:
                for theme in volume.get('themes', []):
                    for title_group in theme.get('titles', []):
                        for pub in title_group.get('publications', []):
                            if pub.get('publication_title') == entry['jp_title']:
                                print(f"MATCH (Title): {entry['jp_title']}")
                                pub['publication_title_ptbr'] = entry['pt_title']
                                pub['content_ptbr'] = entry['content']
                                match_found = True
        
        # Strategy 2: Match by Date (if no match yet)
        if not match_found and entry['date_tuple']:
            md_date = entry['date_tuple']
            for volume in data:
                for theme in volume.get('themes', []):
                    for title_group in theme.get('titles', []):
                        for pub in title_group.get('publications', []):
                            # Skip if already translated
                            if 'content_ptbr' in pub:
                                continue
                                
                            json_date_str = pub.get('date')
                            json_date = parse_japanese_date(json_date_str)
                            
                            if json_date == md_date:
                                print(f"MATCH (Date): {json_date} -> {entry['pt_title']}")
                                pub['publication_title_ptbr'] = entry['pt_title']
                                pub['content_ptbr'] = entry['content']
                                match_found = True
                                break # Stop searching for this entry
        
        if match_found:
            matches_count += 1
        else:
            print(f"NO MATCH: {entry['pt_title']} (JP: {entry['jp_title']}, Date: {entry['date_tuple']})")

    # 4. Save JSON
    print(f"Total Matches: {matches_count}")
    print(f"Saving updated JSON to {JSON_PATH}...")
    with open(JSON_PATH, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

if __name__ == "__main__":
    main()
