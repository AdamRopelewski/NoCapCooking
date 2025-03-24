import os
import json
import glob


def generate_prompt(name, cuisine, ingredients):
    # Jeśli ingredients jest listą, łączymy elementy przecinkiem
    if isinstance(ingredients, list):
        ingredients_str = ", ".join(ingredients)
    else:
        ingredients_str = str(ingredients)
    prompt = f"opisz {name} {cuisine} {ingredients_str} w okolo 20 slowach jak wyglada to danie po angielsku, po przecinku dla stable diffusion"
    return prompt


def process_json_file(file_path):
    with open(file_path, "r", encoding="utf-8") as f:
        try:
            data = json.load(f)
        except json.JSONDecodeError as e:
            print(f"Nie można wczytać pliku {file_path}: {e}")
            return

    # Zakładamy, że dane są listą rekordów lub pojedynczym rekordem
    records = []
    if isinstance(data, list):
        records = data
    elif isinstance(data, dict):
        records = [data]
    else:
        print(f"Nieoczekiwany format danych w pliku {file_path}")
        return

    output_lines = []
    # Przetwarzamy tylko do 20 rekordów
    for i, record in enumerate(records):
        if i >= 20:
            break
        # Pobieramy wymagane pola, jeśli nie istnieją – używamy pustego ciągu znaków
        name = record.get("name", "")
        cuisine = record.get("cuisine", "")
        ingredients = record.get("ingredients", "")
        prompt = generate_prompt(name, cuisine, ingredients)
        output_lines.append(prompt)

    output_lines.append(
        f"odpowiedz podaj w json o kluczach name, image_prompt. kontekst: kuchnia {cuisine}"
    )
    # Budujemy nazwę pliku wyjściowego: gpt_{oryginalna_nazwa_pliku}
    directory, filename = os.path.split(file_path)
    output_filename = f"gpt_{filename}"
    output_file_path = os.path.join(
        "gpt_gen_stable_diff_prompts", output_filename
    )
    # Tworzymy folder gpt_gen, jeśli nie istnieje
    output_directory = "gpt_gen_stable_diff_prompts"
    os.makedirs(output_directory, exist_ok=True)
    # Zmieniamy rozszerzenie pliku wyjściowego na .txt
    output_filename = os.path.splitext(output_filename)[0] + ".txt"
    output_file_path = os.path.join(output_directory, output_filename)
    with open(output_file_path, "w", encoding="utf-8") as out_f:
        # Zapisujemy każdy prompt w nowej linii
        out_f.write("\n".join(output_lines))
    print(f"Zapisano {len(output_lines)} promptów do pliku {output_file_path}")


def main():
    # Używamy bieżącego folderu; można zmienić na inny, np. folder z argumentami skryptu
    folder_path = "json-input"
    json_files = glob.glob(os.path.join(folder_path, "*.json"))
    if not json_files:
        print("Brak plików JSON w folderze.")
        return

    for file_path in json_files:
        process_json_file(file_path)


if __name__ == "__main__":
    main()
