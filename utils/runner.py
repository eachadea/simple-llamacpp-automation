import os
from psutil import cpu_count
from llama_cpp import Llama


def create_llama(model_path: str, seed: int = 1337, *args, **kwargs) -> Llama:
    return Llama(model_path, *args, **kwargs, seed=seed)


def generate_llama(model: Llama, prompt: str, *args, **kwargs) -> str:
    return model(prompt, *args, **kwargs)
