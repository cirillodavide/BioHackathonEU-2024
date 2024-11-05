import json
import argparse
import subprocess
import pandas as pd
from openai import OpenAI

def parse_csv(file):
    try:
        df = pd.read_csv(file, on_bad_lines="skip", sep="\t")
        first_author_firstname = df['first_author_firstName'].iloc[0]
        first_author_lastname = df['first_author_lastName'].iloc[0]
        last_author_firstname = df['last_author_firstName'].iloc[0]
        last_author_lastname = df['last_author_lastName'].iloc[0]
    except KeyError as e:
        print(f"Column not found in CSV: {e}")
        return None, None, None, None
    
    return first_author_firstname, first_author_lastname, last_author_firstname, last_author_lastname

def install_llm_model(model_name):
    try:
        subprocess.run(["ollama", "pull", model_name], check=True)
    except subprocess.CalledProcessError as e:
        print(f"An error occurred while installing the model: {e}")

def infer_gender(client, model_name, firstname, lastname):
    prompt_text = f"Identify the likely gender based on the name '{firstname} {lastname}'."
    response = client.chat.completions.create(
        model=model_name,
        messages=[
            {"role": "user", "content": prompt_text}
        ]
    )
    
    return response.choices[0].message.content.strip()

def main(model):
    client = OpenAI(
        base_url='http://localhost:11434/v1',
        api_key='ollama'  # required, but unused
    )
    
    model_name = model
    install_llm_model(model_name)
    
    first_author_firstname, first_author_lastname, last_author_firstname, last_author_lastname = parse_csv("data/enriched_aggregated_papers.csv")
    
    if first_author_firstname and first_author_lastname:
        first_author_gender = infer_gender(client, model_name, first_author_firstname, first_author_lastname)
        
        result = {
            "first_author": {
                "firstname": first_author_firstname,
                "lastname": first_author_lastname,
                "gender": first_author_gender
            }
        }
        
        print(json.dumps(result, indent=4))

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-m", "--model", help="Name of the LLM model")
    args = parser.parse_args()

    main(args.model)