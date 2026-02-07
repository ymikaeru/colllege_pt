import os
import json

DATA_DIR = "data"
TEMAS_DIR = os.path.join(DATA_DIR, "temasSeparados")
BKP_DIR = os.path.join(TEMAS_DIR, "bkp")
PARTES_DIR = os.path.join(TEMAS_DIR, "partes")

theme_key = "03_3.信仰編_08_御神業の心得"
part_num = 39

pt_filename = f"{theme_key}_parte{part_num:02d}_pt.json"
pt_path_bkp = os.path.join(BKP_DIR, pt_filename)
pt_path_partes = os.path.join(PARTES_DIR, pt_filename)

print(f"Checking {pt_filename}...")
print(f"Path in BKP: {pt_path_bkp} (Exists: {os.path.exists(pt_path_bkp)})")
print(f"Path in PARTES: {pt_path_partes} (Exists: {os.path.exists(pt_path_partes)})")

actual_path = pt_path_bkp if os.path.exists(pt_path_bkp) else pt_path_partes

if not os.path.exists(actual_path):
    print("File not found anywhere!")
    exit(1)

with open(actual_path, 'r', encoding='utf-8') as f:
    try:
        data = json.load(f)
        print("JSON Load Success")
        print(f"Keys: {list(data.keys())}")
        pubs = data.get("publications", [])
        print(f"Publications count: {len(pubs)}")
        for i, pub in enumerate(pubs):
            print(f"  Pub {i}: {pub.get('publication_title')}")
            
    except Exception as e:
        print(f"JSON Load Error: {e}")

# Check original
orig_filename = pt_filename.replace("_pt.json", ".json")
orig_path_bkp = os.path.join(BKP_DIR, orig_filename)
print(f"\nChecking Original {orig_filename}...")
print(f"Path in BKP: {orig_path_bkp} (Exists: {os.path.exists(orig_path_bkp)})")

if os.path.exists(orig_path_bkp):
     with open(orig_path_bkp, 'r', encoding='utf-8') as f:
        try:
            d = json.load(f)
            print("Original JSON Load Success")
            or_pubs = d.get("publications", [])
            print(f"Original Pubs count: {len(or_pubs)}")
        except Exception as e:
            print(f"Original JSON Error: {e}")

