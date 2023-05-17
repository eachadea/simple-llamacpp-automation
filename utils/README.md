# simple-llamacpp-automation
A simple cli tool to automate running lots of prompts. It takes a list of models, presets, and prompts, and generates using every possible combination.

### Usage
- Put your models in the models directory. Every model must have a config file of the same name, but with a .json extension instead of .bin
- Put your presets in the presets directory.
- Put your prompts in the prompts directory (.txt, don't use prompt templates - every model uses a different one, which is why this is set in each model's config)
- Double-click run-windows.bat or ./run-nix
