import os
import requests
import json
import base64
from PIL import Image
from io import BytesIO


# Model absolutereality_v181.safetensors [463d6a9fe8]


# Define the directory where the JSON files are located
input_directory = "json-input/"

# Define the URL of the Stable Diffusion API endpoint
api_url = "http://127.0.0.1:7860/sdapi/v1/txt2img"



# Function to generate image for a given recipe
def generate_image_from_recipe(
    recipe, output_dir, input_file_name, jpeg_quality=50
):
    name = recipe["name"]
    ingredients = ", ".join(recipe["ingredients"])

    # Create the prompt by incorporating the name and ingredients
    prompt = f"top down distant view, one {name}, (plate:0.7), (icon:0.8), simple, {ingredients}"

    # Define the parameters for the request
    data = {
        "prompt": prompt,
        "negative_prompt": "touching plates, (cutlery:0.4), zoom, makro, multiple, (saturated:0.4), egg, raw fish, (multiple plates), text, deformed, people",
        "styles": [],
        "seed": -1,
        "subseed": -1,
        "subseed_strength": 0,
        "sampler_name": "UniPC",
        "scheduler": "Automatic",
        "batch_size": 1,
        "n_iter": 1,
        "steps": 16,
        "cfg_scale": 6,
        "width": 1024,
        "height": 1024,
        "restore_faces": False,
        "tiling": True,
        "do_not_save_samples": False,
        "do_not_save_grid": True,
        "eta": 0,
        "denoising_strength": 0,
        "send_images": True,
        "save_images": False,
    }

    headers = {
        "Content-Type": "application/json",
    }

    # Send a POST request to the API
    response = requests.post(api_url, headers=headers, data=json.dumps(data))

    if response.status_code == 200:
        # Assuming the response contains the image as base64-encoded data
        result = response.json()
        image_data = result.get("images")[0]

        if image_data:
            # Decode the base64 data
            image_bytes = base64.b64decode(image_data)

            # Open the image using Pillow
            image = Image.open(BytesIO(image_bytes))

            # Convert the image to JPEG
            input_file_without_extension = os.path.splitext(input_file_name)[0]
            input_file_without_extension = input_file_without_extension.split(
                "/"
            )
            input_file_without_extension = "/".join(
                input_file_without_extension[1:]
            )
            os.makedirs(output_dir, exist_ok=True)
            gen_img_name = (
                f"{output_dir}/{name}.jpg"
            )
            gen_img_name = gen_img_name.replace(" ", "_")
            gen_img_name = str.lower(gen_img_name)
            # Compress into jpeg
            image.convert("RGB").save(
                gen_img_name, "JPEG", quality=jpeg_quality
            )
            print(f"Image saved as JPEG for {output_dir}/{name}.")

        else:
            print(f"No image data found for {name}.")
    else:
        print(
            f"Request failed for {name} with status code {response.status_code}"
        )
        print(response.text)


def check_if_image_exists(recipe, output_dir):
    if_exists = False
    name = recipe["name"]
    name = name.replace(" ", "_")
    name = str.lower(name)
    gen_img_name = f"{output_dir}/{name}.jpg"
    if_exists = os.path.exists(gen_img_name)

    return if_exists

# Process all JSON files in the directory
for filename in os.listdir(input_directory):
    if filename.endswith(".json"):
        input_file_name = os.path.join(input_directory, filename)

        # Load the JSON data from the file
        with open(input_file_name, "r", encoding="utf-8") as file:
            recipes_data = json.load(file)

        # Create an output directory for each JSON file
        output_dir = os.path.join("images-output", f"{filename.split('.')[0]}")
        os.makedirs(output_dir, exist_ok=True)

        # Process each recipe in the JSON file
        images_generated_counter = 0
        for recipe in recipes_data:
            # Check if the image already exists
            if check_if_image_exists(recipe, output_dir):
                # print(f"\nImage already exists for {recipe['name']}.")
                continue
            generate_image_from_recipe(recipe, output_dir, input_file_name)
            images_generated_counter += 1

        # Ask user if they want to continue to the next file
        if images_generated_counter > 0:
            user_input = input(
                f"Processed {filename}. Do you want to continue to the next file? (y/n): "
            )
            if user_input.lower() != "y":
                print("Exiting...")
                break
print("All files processed.")
