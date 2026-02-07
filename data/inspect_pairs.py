
import json
import os

BKP_DIR = "/Users/michael/Documents/Ensinamentos/Sites/ShinCollege_Pt/data/temasSeparados/bkp"

FILES_TO_CHECK = [
    "04_4.その他_04_宗教断片集_parte20",
    "04_4.その他_04_宗教断片集_parte25",
    "02_2.浄霊・神示の健康法・自然農法編_02_浄霊の方法_parte21",
    "02_2.浄霊・神示の健康法・自然農法編_02_浄霊の方法_parte33",
    "02_2.浄霊・神示の健康法・自然農法編_02_浄霊の方法_parte34"
]

def inspect_pairs():
    for fname_base in FILES_TO_CHECK:
        pt_path = os.path.join(BKP_DIR, f"{fname_base}_pt.json")
        orig_path = os.path.join(BKP_DIR, f"{fname_base}.json")
        
        print(f"\n--- Checking {fname_base} ---")
        
        if not os.path.exists(orig_path):
            print(f"❌ Original file missing: {orig_path}")
            continue
            
        with open(pt_path, 'r') as f: pt_data = json.load(f)
        with open(orig_path, 'r') as f: orig_data = json.load(f)
        
        pt_pubs = pt_data.get("publications", [])
        orig_pubs = orig_data.get("publications", [])
        
        print(f"  PT Pubs: {len(pt_pubs)}, Orig Pubs: {len(orig_pubs)}")
        
        # Check specific snippets
        for i, pt_pub in enumerate(pt_pubs):
            pt_content = pt_pub.get("content_ptbr", "")
            pt_title = pt_pub.get("title_ptbr", "")
            pub_idx = pt_pub.get("pub_idx", i)
            
            # Find corresponding orig pub
            orig_match = None
            for op in orig_pubs:
                if op.get("pub_idx") == pub_idx:
                    orig_match = op
                    break
            
            if not orig_match:
                # Fallback to index if pub_idx approach fails (mimic script logic?? No script uses pub_idx map)
                # But wait, script logic: orig_map = {pub.get("pub_idx", i): pub ...}
                pass

            jp_content = ""
            if orig_match:
                jp_content = orig_match.get("content", "")
            
            # Check for our target issues
            if "Em tempos de seca" in pt_content or "Ao ministrar Johrei para" in pt_content:
                print(f"  Found target snippet in PT (Index/PubIdx: {i}/{pub_idx})")
                if not orig_match:
                    print(f"    ❌ No matching Original found for pub_idx {pub_idx}")
                else:
                    print(f"    ✅ Match found. JP Content Length: {len(jp_content)}")
                    if len(jp_content) < 5:
                        print(f"    ❌ JP Content is empty/short: '{jp_content}'")
                        print(f"    Original Title: '{orig_match.get('title', '')}'")

if __name__ == "__main__":
    inspect_pairs()
