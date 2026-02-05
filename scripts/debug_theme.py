import json
import re

MANUAL_THEME_MAP = {
    "御神体とお光": "Imagem Divina e Ohikari",
}

def normalize_text(text):
    if not text: return ""
    return re.sub(r'\s+', '', text).strip()

def main():
    path = "/Users/michael/Documents/Ensinamentos/Sites/ShinCollege_Pt/data/shin_college_data_translated.json"
    with open(path, 'r', encoding='utf-8') as f:
        data = json.load(f)

    found = False
    for volume in data:
        for theme in volume.get('themes', []):
            jp = theme.get('theme')
            if jp == "御神体とお光":
                found = True
                norm = normalize_text(jp)
                print(f"Original: '{jp}'")
                print(f"Normalized: '{norm}'")
                print(f"In Map? {norm in MANUAL_THEME_MAP}")
                if norm in MANUAL_THEME_MAP:
                    print(f"Map Value: '{MANUAL_THEME_MAP[norm]}'")
                
                # Check bytes just in case
                print(f"Bytes: {jp.encode('utf-8')}")
                
                # Check against manual key bytes
                man_key = list(MANUAL_THEME_MAP.keys())[0]
                print(f"Map Key Bytes: {man_key.encode('utf-8')}")
                
    if not found:
        print("Theme not found in JSON iteration!")

if __name__ == "__main__":
    main()
