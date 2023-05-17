import os

from typing import Dict, List, Any
from dataclasses import dataclass

from llama_cpp import Llama
from dotenv import load_dotenv
from psutil import cpu_count

from utils.runner import create_llama, generate_llama
from utils.logger import logger
from utils import misc

# Makes a mess
VERBOSE = False

# Helps with swapping
USE_MLOCK = True

# Each model has its own developer-recommended prompt template
MODEL_CONFIG_REQUIRED_ARGS = [
    "pre_prompt",
    "prompt_prepend",
    "answer_prepend"
]

# All items must be present, even if unused - set to 0 in that case. In the case of repeat_penaltty, set to 1.0 to disable.
PRESET_REQUIRED_ARGS = [
    "tfs_z",
    "temperature",
    "top_k",
    "top_p",
    "mirostat_mode",
    "mirostat_eta",
    "mirostat_tau",
    "repeat_penalty",
    "presence_penalty",
    "frequency_penalty"
]


@dataclass
class Preset:
    tfs_z: int
    temperature: float
    top_k: int
    top_p: float
    mirostat_mode: int
    mirostat_eta: float
    mirostat_tau: float

    repeat_penalty: float
    presence_penalty: float
    frequency_penalty: float


@dataclass
class Result:
    model: str
    prompt: str
    output: str
    preset_used: Preset


# llama-cpp-python doesn't seem to properly parse "\n"
def create_internal_prompt(prompt: str, model_config: Dict[str, str]) -> str:
    return f"""{model_config['pre_prompt']}

{model_config["prompt_prepend"]}{prompt}

{model_config["answer_prepend"]}"""


def runner(model: Llama, model_config: Dict[str, str], preset: Dict[str, str], prompt: str, max_tokens: int) -> Result:
    internal_prompt = create_internal_prompt(prompt, model_config)
    model_name = os.path.basename(model.model_path)
    
    preset = Preset(
        tfs_z=preset["tfs_z"],
        temperature=preset["temperature"],
        top_k=preset["top_k"],
        top_p=preset["top_p"],
        mirostat_mode=preset["mirostat_mode"],
        mirostat_eta=preset["mirostat_eta"],
        mirostat_tau=preset["mirostat_tau"],

        repeat_penalty=preset["repeat_penalty"],
        presence_penalty=preset["presence_penalty"],
        frequency_penalty=preset["frequency_penalty"]
    )

    output = model(internal_prompt, max_tokens=max_tokens,
        tfs_z=preset.tfs_z,
        temperature=preset.temperature,
        top_k=preset.top_k,
        top_p=preset.top_p,
        mirostat_mode=preset.mirostat_mode,
        mirostat_eta=preset.mirostat_eta,
        mirostat_tau=preset.mirostat_tau,

        repeat_penalty=preset.repeat_penalty,
        presence_penalty=preset.presence_penalty,
        frequency_penalty=preset.frequency_penalty
    )

    result = Result(model_name, prompt, output["choices"][0]["text"], preset)
    return result


def main_loop(models_dir: str, prompts: List[str], presets: List[Dict[str, Any]], n_threads: int, seed: int, max_tokens: int, n_ctx: int) -> List[Result]:
    if not presets:
        logger.critical("No presets found")

    results = []
    bin_json_pairs = misc.find_bin_json_pairs(models_dir)

    if bin_json_pairs is not None:
        for bin_json_pair in bin_json_pairs:
            bin_path, json_path = [os.path.join(models_dir, file_name) for file_name in bin_json_pair]

            model_config = misc.safe_load_json(json_path, required_items=MODEL_CONFIG_REQUIRED_ARGS)

            misc.print_newlines(3)

            model = create_llama(bin_path, n_threads=n_threads, verbose=VERBOSE, seed=seed, n_ctx=n_ctx, use_mlock=USE_MLOCK)

            for preset in presets:
                for prompt in prompts:
                    result = runner(model, model_config, preset, prompt, max_tokens)
                    results.append(result)
    else:
        raise SystemExit(-1)    # exit reason logged from find_bin_json_pairs()
    return results


if __name__ == "__main__":
    load_dotenv()

    n_threads = os.getenv("N_THREADS")
    if n_threads is not None:
        n_threads = int(n_threads)
    else:
        n_threads = cpu_count(logical=False)
        logger.warning(f"N_THREADS not found in environment. Using {n_threads}")


    seed = os.getenv("SEED")
    if seed is not None:
        seed = int(seed)
    else:
        seed = 1337
        logger.warning(f"SEED not found in environment. Using {seed}")

    max_tokens = os.getenv("MAX_TOKENS")
    if max_tokens is not None:
        max_tokens = int(max_tokens)
    else:
        max_tokens = 256
        logger.warning(f"MAX_TOKENS not found in environment. Using {max_tokens}")

    n_ctx = os.getenv("N_CTX")
    if n_ctx is not None:
        n_ctx = int(n_ctx)
    else:
        n_ctx = 2048
        logger.warning(f"N_CTX not found in environment. Using {n_ctx}")


    project_dir = os.path.abspath(os.path.dirname(__file__))
    models_dir = os.path.join(project_dir, "models")
    prompts_dir = os.path.join(project_dir, "prompts")
    presets_dir = os.path.join(project_dir, "presets")


    prompts_paths = [os.path.join(prompts_dir, file_name) for file_name in misc.find_by_ext(prompts_dir, extension=".txt")]
    presets_paths = [os.path.join(presets_dir, file_name) for file_name in misc.find_by_ext(presets_dir, extension=".json")]

    prompts = []
    for prompt_path in prompts_paths:
        prompts.append(misc.read_file_contents(prompt_path))

    presets = []
    for preset_path in presets_paths:
        presets.append(misc.safe_load_json(preset_path, PRESET_REQUIRED_ARGS))

    results = main_loop(models_dir, prompts, presets, n_threads=n_threads, seed=seed, max_tokens=max_tokens, n_ctx=n_ctx)

    output_dir_path = os.path.join(project_dir, "outputs")
    json_result_path = misc.write_results_to_json(results)

    misc.pretty_write(json_result_path, output_dir_path)
