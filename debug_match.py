
import glob
import os
import re

PARTES_DIR = "data/temasSeparados/partes/"
FILTER = "御神体とお光"

print(f"Scanning {PARTES_DIR}...")
files = glob.glob(os.path.join(PARTES_DIR, "*_pt.json"))
print(f"Found {len(files)} _pt.json files total.")

filtered_files = []
for f in files:
    if FILTER in f:
        filtered_files.append(f)

print(f"Found {len(filtered_files)} files matching filter '{FILTER}'")
for f in filtered_files:
    print(f"  {os.path.basename(f)}")

# Regex Test
pattern = re.compile(r"^(.+?)_parte(\d+)(?:_pt)?\.json$")
for f in filtered_files:
    basename = os.path.basename(f)
    match = pattern.match(basename.replace("_pt.json", ".json"))
    if match:
        print(f"  Regex Match: {basename} -> Theme: {match.group(1)}, Part: {match.group(2)}")
    else:
        print(f"  Regex NO MATCH: {basename}")
