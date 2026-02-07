
import json
import glob
import os

BKP_DIR = "/Users/michael/Documents/Ensinamentos/Sites/ShinCollege_Pt/data/temasSeparados/bkp"

def analyze_loss():
    all_files = glob.glob(os.path.join(BKP_DIR, "*.json"))
    pt_files_map = {f.replace("_pt.json", ".json"): f for f in all_files if f.endswith("_pt.json")}
    
    total_orig_docs = 0
    ignored_files_docs = 0
    skipped_pubs_docs = 0
    
    print("Analisando perdas...")
    
    for fpath in all_files:
        if fpath.endswith("_pt.json"): continue
        
        # This is an original file
        try:
            with open(fpath, 'r', encoding='utf-8') as f:
                orig_data = json.load(f)
            orig_pubs = orig_data.get("publications", [])
            count_orig = len(orig_pubs)
            total_orig_docs += count_orig
            
            # Check if it has a translation counterpart
            if fpath in pt_files_map:
                pt_path = pt_files_map[fpath]
                with open(pt_path, 'r', encoding='utf-8') as f2:
                    pt_data = json.load(f2)
                pt_pubs = pt_data.get("publications", [])
                
                # Check discrepancy in count
                # Start with simple count diff (assuming PT is subset)
                # Ideally we check indices, but count diff gives a quick estimate
                if count_orig > len(pt_pubs):
                    diff = count_orig - len(pt_pubs)
                    skipped_pubs_docs += diff
                    # print(f"  {os.path.basename(fpath)}: Orig={count_orig}, PT={len(pt_pubs)} -> Skipped {diff}")
            else:
                # No translation file -> Ignored File
                ignored_files_docs += count_orig
                # print(f"  Ignored File: {os.path.basename(fpath)} ({count_orig} docs)")
                
        except Exception as e:
            print(f"Error reading {os.path.basename(fpath)}: {e}")
            
    print(f"\n--- RESUMO DA PERDA ---")
    print(f"Total de Documentos Originais (BKP): {total_orig_docs}")
    print(f"Total Perdido em Arquivos Ignorados: {ignored_files_docs}")
    print(f"Total Perdido em Publicações Puladas (dentro de arquivos mergeados): {skipped_pubs_docs}")
    print(f"Total GERAL Perdido: {ignored_files_docs + skipped_pubs_docs}")
    
    print("\nVerificação Matemática:")
    print(f"Esperado no Merge (se tudo fosse incluído): {total_orig_docs}")
    print(f"Atual no Merge (conhecido): {total_orig_docs - (ignored_files_docs + skipped_pubs_docs)}")

if __name__ == "__main__":
    analyze_loss()
