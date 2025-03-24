import os
import json

def main():
    selected_dir = "json-input"
    files_in_dir = os.listdir(selected_dir)
    for file in files_in_dir:
        if file.endswith(".json"):
            file = os.path.join(selected_dir, file)
            with open(file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            file_name = os.path.splitext(os.path.basename(file))[0]
            for recipe in data:
                path = f"{file_name}/{recipe['name'].lower().replace(' ', '_')}"
                recipe['image'] = f"{path}.jpg"
                recipe.pop('photo', None)  
                recipe['audio'] =  f"{path}.opus"
        with open(file, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=4)

if __name__ == "__main__":
    main()