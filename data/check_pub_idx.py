
import json

FILES = [
    "/Users/michael/Documents/Ensinamentos/Sites/ShinCollege_Pt/data/temasSeparados/bkp/04_4.その他_04_宗教断片集_parte20.json",
    "/Users/michael/Documents/Ensinamentos/Sites/ShinCollege_Pt/data/temasSeparados/bkp/02_2.浄霊・神示の健康法・自然農法編_02_浄霊の方法_parte33.json"
]

def check_pub_idx():
    for fpath in FILES:
        print(f"\n--- {fpath.split('/')[-1]} ---")
        try:
            with open(fpath, 'r') as f:
                data = json.load(f)
            pubs = data.get("publications", [])
            print(f"Total Pubs: {len(pubs)}")
            indices = [p.get("pub_idx") for p in pubs]
            print(f"Indices: {indices}")
        except Exception as e:
            print(f"Error: {e}")

if __name__ == "__main__":
    check_pub_idx()
