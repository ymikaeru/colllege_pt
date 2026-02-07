
import json
import os
import glob

MERGED_FILES = [
    "/Users/michael/Documents/Ensinamentos/Sites/ShinCollege_Pt/data/temasSeparados/02_2.浄霊・神示の健康法・自然農法編_02_浄霊の方法_merged.json",
    "/Users/michael/Documents/Ensinamentos/Sites/ShinCollege_Pt/data/temasSeparados/04_4.その他_04_宗教断片集_merged.json"
]

def analyze_missing():
    for fpath in MERGED_FILES:
        if not os.path.exists(fpath): continue
        
        basename = os.path.basename(fpath)
        print(f"\nAnalisando {basename}:")
        
        with open(fpath, 'r', encoding='utf-8') as f:
            data = json.load(f)
            
        pubs = data.get("publications", [])
        for pub in pubs:
            content_jp = pub.get("content", "").strip()
            content_pt = pub.get("content_ptbr", "").strip()
            title = pub.get("title", "").strip()
            
            if content_pt and not content_jp:
                snippet = content_pt[:50].replace("\n", " ")
                print(f"  - Missing JP. Title: '{title}'. PT Snippet: '{snippet}...'")

if __name__ == "__main__":
    analyze_missing()
