import json
import re
import os

TARGET_FILE = "/Users/michael/Documents/Ensinamentos/Sites/ShinCollege_Pt/data/temasSeparados/03_3.信仰編_09_御神体とお光_merged.json"

def clean_title(text):
    if not text:
        return text
    # Remove content inside parenthesis including the parenthesis, if it contains Japanese characters or looks like the pattern " (JP_TITLE)"
    # The pattern seems to be "PT Text (JP Text)"
    # We can try to simply remove the last set of parentheses if it looks like a translation/original pair.
    # Or more aggressively, remove any (...) at the end.
    
    # Pattern: Space + ( + anything + ) at the end of string
    # We want to be careful not to remove legitimate parentheses in PT text, though typically these auto-generated ones are at the end.
    # Let's verify if they correspond to the JP title? 
    # Actually, simpler is: matches " (...)" at the end. 
    
    cleaned = re.sub(r'\s*\([^)]+\)$', '', text)
    return cleaned

def main():
    if not os.path.exists(TARGET_FILE):
        print(f"File not found: {TARGET_FILE}")
        return

    with open(TARGET_FILE, 'r', encoding='utf-8') as f:
        data = json.load(f)

    print(f"Processing {len(data.get('publications', []))} publications...")
    
    count = 0
    for pub in data.get('publications', []):
        old_title_pt = pub.get('title_ptbr', '')
        old_pub_title_pt = pub.get('publication_title_ptbr', '')
        
        new_title_pt = clean_title(old_title_pt)
        new_pub_title_pt = clean_title(old_pub_title_pt)
        
        if old_title_pt != new_title_pt or old_pub_title_pt != new_pub_title_pt:
            pub['title_ptbr'] = new_title_pt
            pub['publication_title_ptbr'] = new_pub_title_pt
            count += 1
            # print(f"Cleaned:\n  {old_title_pt} -> {new_title_pt}\n  {old_pub_title_pt} -> {new_pub_title_pt}")

    data['theme_name_ptbr'] = "Goshintai e Ohikari" # Ensure this is set securely

    with open(TARGET_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    print(f"Updated {count} publications in {TARGET_FILE}")

if __name__ == "__main__":
    main()
