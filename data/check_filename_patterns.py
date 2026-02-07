
import glob
import os
import re

BKP_DIR = "/Users/michael/Documents/Ensinamentos/Sites/ShinCollege_Pt/data/temasSeparados/bkp"

def check_patterns():
    pt_files = glob.glob(os.path.join(BKP_DIR, "*_pt.json"))
    pattern = re.compile(r"^(.+?)_parte(\d+)(?:_pt)?\.json$")
    
    matched = 0
    unmatched = 0
    
    print(f"Verificando padrões em {len(pt_files)} arquivos...")
    
    for f in pt_files:
        basename = os.path.basename(f)
        match = pattern.match(basename.replace("_pt.json", ".json")) # The script does this replacement before matching? 
        # Wait, script line 77: match = pattern.match(basename.replace("_pt.json", ".json"))
        # No, line 77: match = pattern.match(basename.replace("_pt.json", ".json")) 
        # Actually line 77: match = pattern.match(basename.replace("_pt.json", ".json"))
        # My previous `view_file` showed:
        # 77:         match = pattern.match(basename.replace("_pt.json", ".json"))
        
        # Testing the exact logic
        test_str = basename.replace("_pt.json", ".json")
        match = pattern.match(test_str)
        
        if match:
            matched += 1
        else:
            unmatched += 1
            print(f"  ❌ NÃO CORRESPONDE: {basename} (Test str: {test_str})")

    print(f"Matched: {matched}")
    print(f"Unmatched: {unmatched}")

if __name__ == "__main__":
    check_patterns()
