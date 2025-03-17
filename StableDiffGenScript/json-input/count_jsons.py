import os
import json

#!/usr/bin/env python3

def count_items_in_json(file_path):
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        # Jeśli dane są listą, liczymy elementy listy,
        # jeśli słownikiem, liczymy klucze,
        # w przeciwnym wypadku informujemy, że struktura jest inna.
        if isinstance(data, list):
            return len(data)
        elif isinstance(data, dict):
            return len(data.keys())
        else:
            return f"Nieobsługiwana struktura typu {type(data).__name__}"
    except Exception as e:
        return f"Błąd: {e}"

def main():
    current_directory = "."
    files_in_dir = os.listdir(current_directory)
    
    json_files = sorted([f for f in files_in_dir if f.lower().endswith(".json")])
    
    if not json_files:
        print("Brak plików JSON w bieżącym katalogu.")
        return
    
    for json_file in json_files:
        count = count_items_in_json(json_file)
        print(f"{json_file}: {count} item(ów)")

if __name__ == "__main__":
    main()