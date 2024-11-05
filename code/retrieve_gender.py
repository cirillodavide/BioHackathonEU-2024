import json
import csv
import re
import argparse
import subprocess
import pandas as pd
from openai import OpenAI

def parse_csv(file):
    try:
        df = pd.read_csv(file, on_bad_lines="skip", sep="\t")
        first_author_firstname = df['first_author_firstName']
        first_author_lastname = df['first_author_lastName']
        last_author_firstname = df['last_author_firstName']
        last_author_lastname = df['last_author_lastName']
    except KeyError as e:
        print(f"Column not found in CSV: {e}")
        return None, None, None, None
    
    return first_author_firstname, first_author_lastname, last_author_firstname, last_author_lastname

def install_llm_model(model_name):
    try:
        subprocess.run(["ollama", "pull", model_name], check=True)
    except subprocess.CalledProcessError as e:
        print(f"An error occurred while installing the model: {e}")

def infer_gender(client, model_name, firstauthor, lastauthor):
    prompt_text = (
        f'Given the names of two authors, please identify the likely gender of each author. '
        f'Provide the gender as either "male", "female", "other", or "not retrievable". '
        f'Also, include a brief reasoning for each author based on the names provided. '
        f'The name of the first author is: {firstauthor} and the name of the last author is: {lastauthor}. '
        f'Please return the response in **strict JSON format only**, with no additional text. '
        f'Use the following structure:\n'
        '{\n'
        '    "first_author": {\n'
        '        "name": {firstauthor}, \n'
        '        "gender": "male/female/other/not retrievable",\n'
        '        "reasoning": "Explanation for the gender determination of the first author."\n'
        '    },\n'
        '    "last_author": {\n'
        '        "name": {lastauthor}, \n'
        '        "gender": "male/female/other/not retrievable",\n'
        '        "reasoning": "Explanation for the gender determination of the last author."\n'
        '    }\n'
        '}'
    )

    response = client.chat.completions.create(
        model=model_name,
        messages=[
            {"role": "user", "content": prompt_text}
        ]
    )

    return response.choices[0].message.content.strip()

def save_to_tsv(result, output_file='gender_data.tsv'):
    with open(output_file, mode='a', newline='') as file:
        writer = csv.writer(file, delimiter='\t')
        
        if file.tell() == 0:
            writer.writerow(['first_author', 'gender_firstauthor', 'reasoning_firstauthor', 'last_author', 'gender_lastauthor', 'reasoning_lastauthor'])

        writer.writerow([result["first_author"]["name"], 
                         result["first_author"]["gender"], 
                         result["first_author"]["reasoning"],
                         result["last_author"]["name"], 
                         result["last_author"]["gender"], 
                         result["last_author"]["reasoning"]])


def main(model):
    client = OpenAI(
        base_url='http://localhost:11434/v1',
        api_key='ollama'  # required, but unused
    )
    
    model_name = model
    install_llm_model(model_name)
    
    first_author_firstname, first_author_lastname, last_author_firstname, last_author_lastname = parse_csv("data/enriched_aggregated_papers.csv")
    
    for first_author_firstname, first_author_lastname, last_author_firstname, last_author_lastname in zip(
        first_author_firstname, first_author_lastname, last_author_firstname, last_author_lastname):

        if pd.isna(first_author_firstname) or pd.isna(first_author_lastname) or pd.isna(last_author_firstname) or pd.isna(last_author_lastname):
            continue  # Skips to the next iteration if any name is NaN

        firstauthor = f"{first_author_firstname} {first_author_lastname}"
        lastauthor = f"{last_author_firstname} {last_author_lastname}"

        if firstauthor and lastauthor:
            json_gender_response = infer_gender(client, model_name, firstauthor, lastauthor)

            json_gender_response = infer_gender(client, model_name, firstauthor, lastauthor)
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