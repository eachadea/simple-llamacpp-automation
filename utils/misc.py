import os
import json
import datetime
import tempfile

from typing import Any

from utils.logger import logger


def find_bin_json_pairs(folder_path):
    file_names = os.listdir(folder_path)

    file_pairs = []
    for file_name in file_names:
        if file_name.endswith(".bin"):
            json_name = file_name.replace(".bin", ".json")
            if json_name in file_names:
                file_pairs.append((file_name, json_name))
            else:
                logger.critical(f"JSON file {json_name} is missing for {file_name}")
                return None

        elif file_name.endswith(".json"):
            bin_name = file_name.replace(".json", ".bin")
            if bin_name not in file_names:
                logger.critical(f"Binary file {bin_name} is missing for {file_name}")
                return None

    if len(file_pairs) == 0:
        logger.critical("No matching pairs of .bin and .json files found.")
        return None

    return file_pairs


def find_by_ext(folder_path, extension=".txt"):
    file_names = os.listdir((folder_path))

    matching_file_names = []
    for file_name in file_names:
        if file_name.endswith(extension):
            matching_file_names.append(file_name)

    return matching_file_names


def safe_load_json(path, required_items):
    try:
        with open(path, 'r') as f:
            json_data = json.load(f)
    except FileNotFoundError:
        logger.critical(f"File not found at path {path}")
        return None

    # Check if all required items are present in the loaded JSON
    for item in required_items:
        if item not in json_data:
            logger.critical(f"Required item '{item}' not found in JSON file at {path}")
            return None

    # If all required items are present, return the loaded JSON as a Python dict
    return json_data


def read_file_contents(file_path) -> str:
    if not os.path.isfile(file_path):
        raise logger.critical(f"File doesn't exist: '{file_path}'")

    with open(file_path, 'r') as file:
        contents = file.read()

    return str(contents).strip('\n').strip()


def write_results_to_json(results: Any) -> str:
    now = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    filename = f"Output {now}.json"

    output = {
        "timestamp": now,
        "results": []
    }
    for result in results:
        output["results"].append({
            "model": result.model,
            "prompt": result.prompt,
            "output": result.output,
            "preset_used": {
                "tfs_z": result.preset_used.tfs_z,
                "temperature": result.preset_used.temperature,
                "top_k": result.preset_used.top_k,
                "top_p": result.preset_used.top_p,
                "mirostat_mode": result.preset_used.mirostat_mode,
                "mirostat_eta": result.preset_used.mirostat_eta,
                "mirostat_tau": result.preset_used.mirostat_tau,
                "repeat_penalty": result.preset_used.repeat_penalty,
                "presence_penalty": result.preset_used.presence_penalty,
                "frequency_penalty": result.preset_used.frequency_penalty
            }
        })

    with tempfile.NamedTemporaryFile(mode='w', delete=False) as temp_file:
        json.dump(output, temp_file, indent=4)
        temp_file.flush()
        return temp_file.name

    output_path = os.path.join(output_dir_path, filename)
    with open(output_path, 'w') as f:
        json.dump(output, f, indent=4)


def print_newlines(count: int = 3) -> None:
    newline_literal = "\n"
    print(f"{''.join([newline_literal for newline in range(count)])}")


def pretty_write(json_path: str, output_dir: str) -> None:
    now = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")

    # Read the JSON data from a file
    with open(json_path) as f:
        data = json.load(f)

    # Sort the results by model name
    results = sorted(data['results'], key=lambda r: r['model'])

    filename = f"Output {now}.txt"
    output_path = os.path.join(output_dir, filename)

    with open(output_path, 'w') as f:
        for result in results:
            f.write(f"Model: {result['model']}\n")
            f.write(f"Prompt: {result['prompt']}\n")
            f.write(f"Output: {result['output']}\n\n")
            f.write(f"Preset used: {json.dumps(result['preset_used'], indent=4)}\n\n")
