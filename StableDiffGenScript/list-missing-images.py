import os
import json


def check_if_image_exists(recipe, output_dir):
    if_exists = False
    name = recipe.get("name")
    name = name.replace(" ", "_")
    name = str.lower(name)
    gen_img_name = f"{output_dir}/{name}.jpg"
    if_exists = os.path.exists(gen_img_name)

    return if_exists


input_directory = "json-input"

with open("missing-images.txt", "w", encoding="utf-8") as file:
    file.write("\t\t\tMissing images:\n")

for filename in os.listdir(input_directory):
    if filename.endswith(".json"):
        input_file_name = os.path.join(input_directory, filename)

        # Load the JSON data from the file
        with open(input_file_name, "r", encoding="utf-8") as file:
            recipes_data = json.load(file)

        # Create an output directory for each JSON file
        output_dir = os.path.join("images-output", f"{filename.split('.')[0]}")
        os.makedirs(output_dir, exist_ok=True)

        for recipe in recipes_data:
            # Check if the image already exists
            if not check_if_image_exists(recipe, output_dir):
                message = f"\n{filename}:\t\t{recipe.get('name')}"
                with open("missing-images.txt", "a", encoding="utf-8") as file:
                    file.write(message)
