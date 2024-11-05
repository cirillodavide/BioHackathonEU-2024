import json
import csv
import re
import argparse
import subprocess
import pandas as pd
from openai import OpenAI

import pandas as pd

def parse_csv(file):
    try:
        df = pd.read_csv(file, on_bad_lines="skip", sep="\t")[:]
        first_author_firstname = df['first_author_firstName']
        first_author_lastname = df['first_author_lastName']
        last_author_firstname = df['last_author_firstName']
        last_author_lastname = df['last_author_lastName']
    except KeyError as e:
        print(f"Column not found in CSV: {e}")
        return None 

    first_authors_full_names = first_author_firstname + ' ' + first_author_lastname
    last_authors_full_names = last_author_firstname + ' ' + last_author_lastname

    all_names = pd.concat([first_authors_full_names, last_authors_full_names])

    string_names = all_names[all_names.str.isin(all_names.dropna())].dropna()

    unique_names = string_names.unique() 

    return unique_names.tolist()

def install_llm_model(model_name):
    try:
        subprocess.run(["ollama", "pull", model_name], check=True)
    except subprocess.CalledProcessError as e:
        print(f"An error occurred while installing the model: {e}")

def infer_gender(client, model_name, author):
    prompt_text = (
        f'Given the names of the author, please identify the likely gender of the author. '
        f'Provide the gender as either "male", "female", "other", or "not retrievable". '
        f'Also, include a reasoning for each author based on the name provided. '
        f'The name of the author is: {author}. '
        f'Please return the response in **strict JSON format only**, with no additional text. '
        f'Use the following structure:\n'
        '{\n'
        '    "author": {\n'
        '        "name": {author}, \n'
        '        "gender": "male/female/other/not retrievable",\n'
        '        "reasoning": "Explanation for the gender determination of the author."\n'
        '}'
    )

    response = client.chat.completions.create(
        model=model_name,
        messages=[
            {"role": "user", "content": prompt_text}
        ]
    )

    return response.choices[0].message.content.strip()

def save_to_tsv(result, output_file='gender_data_dict.tsv'):
    with open(output_file, mode='a', newline='') as file:
        writer = csv.writer(file, delimiter='\t')
        
        if file.tell() == 0:
            writer.writerow(['author', 'gender_author', 'reasoning_author'])

        writer.writerow([result["author"]["name"], 
                         result["author"]["gender"], 
                         result["author"]["reasoning"]])


def main(model):
    client = OpenAI(
        base_url='http://localhost:11434/v1',
        api_key='ollama'  # required, but unused
    )
    
    model_name = model
    install_llm_model(model_name)
    
    unique_author_names = parse_csv("data/enriched_aggregated_papers.csv")
    for author_name in unique_author_names:
        json_gender_response = infer_gender(client, model_name, author_name)
        json_match = re.search(r'{.*}', json_gender_response, re.DOTALL)
        if json_match:
            json_text = json_match.group(0)
            try:
                result = json.loads(json_text)
            except json.JSONDecodeError as e:
                print("Failed to parse JSON:", e)
        else:
            print("No JSON found in the response content.")
                    
        save_to_tsv(result)

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-m", "--model", help="Name of the LLM model")
    args = parser.parse_args()

    main(args.model)