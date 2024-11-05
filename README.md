# BioHackathonEU-2024
Project 6: Gender representation in ELIXIR-supported publications: a visibility analysis across academic search engines

## Getting Started

To install Ollama on your machine, run the following command:

```bash
curl -fsSL https://ollama.com/install.sh | sh
```

Once installed, start the Ollama engine by running:

```bash
ollama serve
```

To install all required dependencies, use:

```bash
pip install -r requirements.txt
```

To prompt the LLM to identify gender, execute the following script:

```bash
python3 code/retrieve_gender.py [-m MODEL]
```

For example, if you select the "llama2" model, please execute the following:

```bash
python3 code/retrieve_gender.py -m llama2
```