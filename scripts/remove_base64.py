
import json
import re
import sys
import argparse

def remove_base64_images(text):
    if not isinstance(text, str):
        return text
    # Pattern to match data:image...base64,... up to the next quote or reasonable end
    # Often in markdown or HTML: ![alt](data:image/png;base64,...) or <img src="data:image...">
    # We'll look for the specific base64 pattern and replace it with empty string or a placeholder.
    # Pattern: data:image\/[a-zA-Z]+;base64,[a-zA-Z0-9+/=]+
    
    # Simple pattern for standard base64 images
    pattern = r'data:image\/[a-zA-Z]+;base64,[a-zA-Z0-9+\/=]+'
    
    # If the base64 string is very long, regex might be slow or hit limits, but usually okay for this.
    # Let's try to replace it with a placeholder to keep valid syntax if it's inside an img tag
    # But usually user wants to "apagar" (delete). 
    # If it's markdown `![](data:...)`, replacing with `()` removes the image but leaves empty link.
    # If we just remove the whole regex match:
    
    return re.sub(pattern, '', text)

def traverse_and_clean(node):
    count = 0
    if isinstance(node, list):
        for item in node:
            count += traverse_and_clean(item)
    elif isinstance(node, dict):
        for k, v in node.items():
            if isinstance(v, str):
                if "data:image" in v:
                    cleaned = remove_base64_images(v)
                    if cleaned != v:
                        node[k] = cleaned
                        count += 1
            else:
                count += traverse_and_clean(v)
    return count

def main():
    parser = argparse.ArgumentParser(description="Remove base64 images from JSON.")
    parser.add_argument("--input", default="data/shin_college_data.json", help="Input JSON file")
    parser.add_argument("--output", default="data/shin_college_data.json", help="Output JSON file (default: overwrite input)")
    args = parser.parse_args()

    print(f"Loading {args.input}...")
    try:
        with open(args.input, "r", encoding="utf-8") as f:
            data = json.load(f)
    except FileNotFoundError:
        print("Input file not found.")
        return

    print("Cleaning base64 images...")
    removed_count = traverse_and_clean(data)
    print(f"Removed base64 patterns from {removed_count} fields.")

    print(f"Saving to {args.output}...")
    with open(args.output, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    print("Done.")

if __name__ == "__main__":
    main()
