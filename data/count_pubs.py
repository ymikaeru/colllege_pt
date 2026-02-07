
import json

DATA_FILE = "/Users/michael/Documents/Ensinamentos/Sites/ShinCollege_Pt/data/shin_college_data.json"

def count_pubs():
    with open(DATA_FILE, 'r') as f:
        data = json.load(f)
        
    total_pubs = 0
    pubs_with_translation = 0
    pubs_without_translation = 0
    
    for volume in data:
        for theme in volume.get("themes", []):
            for title_obj in theme.get("titles", []):
                for pub in title_obj.get("publications", []):
                    total_pubs += 1
                    if pub.get("has_translation") or pub.get("content_ptbr"):
                        pubs_with_translation += 1
                    else:
                        pubs_without_translation += 1
                        
    print(f"Total de Publicações no JSON: {total_pubs}")
    print(f"Publicações COM tradução: {pubs_with_translation}")
    print(f"Publicações SEM tradução: {pubs_without_translation}")

if __name__ == "__main__":
    count_pubs()
