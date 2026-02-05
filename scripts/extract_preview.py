import json
import argparse

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--file", default="data/shin_college_data_translated.json")
    parser.add_argument("--theme", default="御神体とお光")
    parser.add_argument("--output", default="data/preview_translation.json")
    args = parser.parse_args()

    with open(args.file, 'r', encoding='utf-8') as f:
        data = json.load(f)

    found_themes = []

    def find_theme(node):
        if isinstance(node, dict):
            if "theme" in node and node["theme"] == args.theme:
                found_themes.append(node)
                return # Don't recurse into the found theme to avoid duplication if nested (unlikely)
            
            # Recurse
            for k, v in node.items():
                if isinstance(v, (dict, list)):
                    find_theme(v)
        elif isinstance(node, list):
            for item in node:
                find_theme(item)

    find_theme(data)

    print(f"Found {len(found_themes)} occurrences of theme '{args.theme}'")
    
    with open(args.output, 'w', encoding='utf-8') as f:
        json.dump(found_themes, f, ensure_ascii=False, indent=2)
    print(f"Saved to {args.output}")

if __name__ == "__main__":
    main()
