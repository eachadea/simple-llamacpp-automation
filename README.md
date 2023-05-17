# simple-llamacpp-automation
A simple cli tool that automates running lots of prompts. It takes a list of models, presets, and prompts, and generates using every possible combination of the three.

### Usage
- Put your model(s) in the models dir.
- Ensure each model has a config file of the same name, but with the `.json` extension instead of `.bin`. This file must contain the following key/value pairs: `pre_prompt`, `prompt_prepend`, and `answer_prepend`. Each can be set to an empty string to disable.
- Put your prompts (text files) in the prompts dir. Do not include any kind of prompt template - each model uses a different template, which is configured in that model's configurational file.
- Double-click run-windows.bat or ./run-unix
