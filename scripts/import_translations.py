#!/usr/bin/env python3
"""
Import Portuguese translations from TranslatedMarkdown folder to JSON.
Matches content based on Japanese titles extracted from (Orig.: ...) metadata.
"""

import json
import re
import os
from pathlib import Path

# Paths
SCRIPT_DIR = Path(__file__).parent
BASE_DIR = SCRIPT_DIR.parent
JSON_PATH = BASE_DIR / "data" / "shin_college_data_translated.json"
TRANSLATED_MD_DIR = BASE_DIR / "TranslatedMarkdown"

# Mapping from filename to theme
FILE_THEME_MAP = {
    "Deus e o Plano Divino(神と経綸).md": "神と経綸",
    "Verdade_06 (真理_06).md": "真理",
}

def normalize_text(text):
    """Normalize text for matching by removing whitespace and special chars."""
    if not text:
        return ""
    # Remove whitespace, full-width spaces and numbers
    text = re.sub(r'[\s　]+', '', text)
    text = text.translate(str.maketrans('０１２３４５６７８９', '0123456789'))
    # Remove parentheses and their contents for comparison
    text = re.sub(r'（[^）]*）', '', text)
    text = re.sub(r'\([^)]*\)', '', text)
    return text.strip()

def extract_jp_title_from_header(header):
    """Extract Japanese title from header like '# N. PT Title (Orig.: 日本語タイトル)'"""
    # Pattern for "(Orig.: ...)"
    match = re.search(r'\(Orig\.?:\s*([^)]+)\)', header)
    if match:
        return match.group(1).strip()
    
    # Pattern for Japanese characters in parentheses like "(日本語)"
    # Only match if it contains Japanese characters
    match = re.search(r'\(([^\)]*[\u3040-\u309f\u30a0-\u30ff\u4e00-\u9fff][^\)]*)\)', header)
    if match:
        return match.group(1).strip()
    
    return None

def extract_pt_title_from_header(header):
    """Extract Portuguese title from header."""
    pt_title = re.sub(r'^# \d+[\.\s\\]*', '', header).strip()
    # Remove (Orig.: ...) part
    pt_title = re.sub(r'\s*\(Orig\.?:[^)]+\)\s*', '', pt_title).strip()
    # Remove Japanese text in parentheses
    pt_title = re.sub(r'\s*\([^\)]*[\u3040-\u309f\u30a0-\u30ff\u4e00-\u9fff][^\)]*\)\s*', '', pt_title).strip()
    # Remove backslashes
    pt_title = pt_title.replace('\\', '').strip()
    return pt_title

def parse_translated_markdown(filepath):
    """Parse translated markdown file and extract sections with their content."""
    sections = {}  # keyed by normalized Japanese title
    
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Find all H1 headers with full text
    header_pattern = re.compile(r'^(# \d+[\.\s\\]*[^\n]+)', re.MULTILINE)
    header_matches = list(header_pattern.finditer(content))
    
    print(f"  Found {len(header_matches)} H1 headers")
    
    for i, match in enumerate(header_matches):
        header = match.group(1)
        
        # Extract Japanese title if present
        jp_title = extract_jp_title_from_header(header)
        pt_title = extract_pt_title_from_header(header)
        
        if not jp_title:
            print(f"    No JP title found in: {header[:60]}...")
            continue
        
        # Get content between this header and next
        start_idx = match.end()
        if i + 1 < len(header_matches):
            end_idx = header_matches[i + 1].start()
        else:
            end_idx = len(content)
        
        section_content = content[start_idx:end_idx].strip()
        
        # Normalize the Japanese title for matching
        norm_jp = normalize_text(jp_title)
        
        sections[norm_jp] = {
            'jp_title': jp_title,
            'pt_title': pt_title,
            'content': section_content
        }
        print(f"    Parsed: {jp_title[:30]}... -> {pt_title[:30]}...")
    
    return sections

def update_json_with_translations(data, theme_name, sections):
    """Update JSON data with translations for a specific theme."""
    updates_count = 0
    
    for volume in data:
        for theme in volume.get('themes', []):
            if theme.get('theme') != theme_name:
                continue
            
            print(f"\n  Updating theme: {theme_name}")
            
            titles = theme.get('titles', [])
            
            for title_group in titles:
                jp_title = title_group.get('title', '')
                norm_jp = normalize_text(jp_title)
                
                # Try to find matching section
                if norm_jp not in sections:
                    # Try partial matching
                    matched = False
                    for section_key in sections:
                        if section_key in norm_jp or norm_jp in section_key:
                            matched_section = sections[section_key]
                            matched = True
                            break
                    if not matched:
                        continue
                else:
                    matched_section = sections[norm_jp]
                
                pt_title = matched_section.get('pt_title', '')
                section_content = matched_section.get('content', '')
                
                # Update title translation
                if pt_title:
                    old_title = title_group.get('title_ptbr', '')
                    if old_title != pt_title:
                        title_group['title_ptbr'] = pt_title
                        print(f"    Title: {jp_title} -> {pt_title}")
                
                # Update publication content
                publications = title_group.get('publications', [])
                
                if section_content and publications:
                    # If only one publication, give it all the content
                    if len(publications) == 1:
                        if not publications[0].get('content_ptbr'):
                            publications[0]['content_ptbr'] = section_content
                            updates_count += 1
                    else:
                        # Try to match publications by their headers in the content
                        # Look for ## or ### headers
                        pub_headers = re.findall(r'^#{2,3}\s+[^\n]+', section_content, re.MULTILINE)
                        
                        for pub in publications:
                            if pub.get('content_ptbr'):
                                continue  # Already has translation
                            
                            pub_title_jp = pub.get('publication_title', '')
                            
                            # Try to find matching content block
                            for header in pub_headers:
                                header_jp = extract_jp_title_from_header(header)
                                if header_jp and normalize_text(header_jp) == normalize_text(pub_title_jp):
                                    # Found matching header, extract content after it
                                    header_idx = section_content.find(header)
                                    next_header_idx = len(section_content)
                                    
                                    for next_h in pub_headers:
                                        next_idx = section_content.find(next_h, header_idx + len(header))
                                        if next_idx > header_idx and next_idx < next_header_idx:
                                            next_header_idx = next_idx
                                    
                                    pub_content = section_content[header_idx + len(header):next_header_idx].strip()
                                    
                                    # Extract Portuguese title from header
                                    pt_pub_title = extract_pt_title_from_header(header.replace('##', '#'))
                                    if pt_pub_title:
                                        pub['publication_title_ptbr'] = pt_pub_title
                                    
                                    if pub_content:
                                        pub['content_ptbr'] = pub_content
                                        updates_count += 1
                                    break
    
    return updates_count

def main():
    print(f"Loading JSON from {JSON_PATH}...")
    with open(JSON_PATH, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    total_updates = 0
    
    # Count existing translations
    before_count = sum(
        1 for v in data 
        for t in v.get('themes', []) 
        for ti in t.get('titles', []) 
        for p in ti.get('publications', []) 
        if p.get('content_ptbr')
    )
    print(f"Existing translations: {before_count}")
    
    # Process each translated markdown file
    for filename, theme_name in FILE_THEME_MAP.items():
        filepath = TRANSLATED_MD_DIR / filename
        if not filepath.exists():
            print(f"File not found: {filepath}")
            continue
        
        print(f"\nParsing {filename}...")
        sections = parse_translated_markdown(filepath)
        print(f"  Parsed {len(sections)} sections with JP titles")
        
        updates = update_json_with_translations(data, theme_name, sections)
        total_updates += updates
        print(f"  Updates from this file: {updates}")
    
    # Count after
    after_count = sum(
        1 for v in data 
        for t in v.get('themes', []) 
        for ti in t.get('titles', []) 
        for p in ti.get('publications', []) 
        if p.get('content_ptbr')
    )
    
    print(f"\n=== Summary ===")
    print(f"Before: {before_count} publications with translations")
    print(f"After: {after_count} publications with translations")
    print(f"New translations: {after_count - before_count}")
    
    if total_updates > 0:
        print(f"\nSaving updated JSON to {JSON_PATH}...")
        with open(JSON_PATH, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        print("Done!")
    else:
        print("\nNo updates made.")

if __name__ == "__main__":
    main()
