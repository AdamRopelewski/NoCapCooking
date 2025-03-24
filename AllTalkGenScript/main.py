import os
import json
import requests
import subprocess


def split_text(text, max_length=2000):
    sentences = text.split(". ")
    segments = []
    current_segment = ""
    for sentence in sentences:
        if len(current_segment) + len(sentence) + 1 <= max_length:
            current_segment += sentence + ". "
        else:
            segments.append(current_segment.strip())
            current_segment = sentence + ". "
    if current_segment:
        segments.append(current_segment.strip())
    return segments


def generate_tts(text, server_ip, server_port, output_file):
    url = f"http://{server_ip}:{server_port}/api/tts-generate"
    payload = {
        "text_input": text,
        "text_filtering": "none",
        "character_voice_gen": "WojciechZoladkowiczV2.wav",
        "rvccharacter_voice_gen": "W.Zoladkowicz18minMUSTAR\W.Zoladkowicz18minMUSTAR_e114_s9120.pth",
        "narrator_enabled": "false",
        "language": "pl",
    }
    response = requests.post(url, data=payload)
    if response.status_code == 200:
        response_json = response.json()
        download_url = f"http://{server_ip}:{server_port}{response_json.get('output_cache_url')}"
        download_response = requests.get(download_url)
        if download_response.status_code != 200:
            print(f"Błąd podczas pobierania pliku: {download_url}")
            return None
        with open(output_file, "wb") as f:
            f.write(download_response.content)
        return output_file
    else:
        print(f"Błąd podczas generowania TTS: {response.status_code}")
        return None


def process_json_files(folder_path, server_ip, server_port):
    output_root = "audio-output"
    os.makedirs(output_root, exist_ok=True)

    for filename in os.listdir(folder_path):
        if filename.endswith(".json"):
            file_path = os.path.join(folder_path, filename)
            json_name = os.path.splitext(filename)[0]
            json_output_folder = os.path.join(output_root, json_name)
            os.makedirs(json_output_folder, exist_ok=True)

            with open(file_path, "r", encoding="utf-8") as file:
                data = json.load(file)
                for idx, entry in enumerate(data):
                    name = entry.get("name", "").replace(" ", "_")
                    recipe = entry.get("recipe", "")
                    if name and recipe:
                        # Konstruuj final_audio z małymi literami w nazwie pliku
                        final_audio = os.path.join(
                            json_output_folder, f"{name}.opus".lower()
                        )
                        if os.path.isfile(final_audio):
                            print(
                                f"Plik {final_audio} już istnieje. Pomijanie."
                            )
                            continue
                        text_input = f"{name.replace('_',' ')}. {recipe}"
                        segments = split_text(text_input)
                        audio_files = []
                        for i, segment in enumerate(segments):
                            temp_file = os.path.join(
                                json_output_folder, f"temp_{idx}_{i}.wav"
                            )
                            audio_file = generate_tts(
                                segment, server_ip, server_port, temp_file
                            )
                            if audio_file:
                                audio_files.append(audio_file)
                        if audio_files:
                            combine_audio_files(audio_files, final_audio)
                            for file in audio_files:
                                os.remove(file)
                            print(f"Pomyślnie wygenerowano plik: {final_audio}")


def combine_audio_files(audio_files, output_file):
    output_file = output_file.lower()
    with open("file_list.txt", "w") as f:
        for file in audio_files:
            f.write(f"file '{os.path.relpath(file)}'\n")
    command = [
        "ffmpeg",
        "-f",
        "concat",
        "-safe",
        "0",
        "-i",
        "file_list.txt",
        "-c:a",
        "libopus",
        "-b:a",
        "48k",
        "-ar",
        "48000",
        output_file,
    ]
    # subprocess.run(command)
    subprocess.run(
        command, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL
    )
    os.remove("file_list.txt")


# Przykład użycia
folder_path = "json-input"
server_ip = "127.0.0.1"
server_port = "7851"
process_json_files(folder_path, server_ip, server_port)
