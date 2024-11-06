import json
import csv
import re
import argparse
import subprocess
from tqdm import tqdm
import pandas as pd
from openai import OpenAI
import ollama


def parse_csv(file):
    try:
        # Read the CSV in chunks and specify separator and error handling
        df_iter = pd.read_csv(file, on_bad_lines="skip", sep="\t", chunksize=1)
        # Loop through each chunk (which is a single row here)
        for chunk in df_iter:
            try:
                # Extract author information for each row
                first_author_firstname = chunk["first_author_firstName"].values[0]
                first_author_lastname = chunk["first_author_lastName"].values[0]
                last_author_firstname = chunk["last_author_firstName"].values[0]
                last_author_lastname = chunk["last_author_lastName"].values[0]
                # Yield as a tuple for each row
                yield first_author_firstname, first_author_lastname, last_author_firstname, last_author_lastname
            except KeyError as e:
                print(f"Column not found in CSV: {e}")
                continue  # Skip rows with missing columns
    except Exception as e:
        print(f"Error reading CSV: {e}")
        return


def install_llm_model(model_name):
    try:
        subprocess.run(["ollama", "pull", model_name], check=True)
    except subprocess.CalledProcessError as e:
        print(f"An error occurred while installing the model: {e}")


def infer_gender(client, model_name, author, api='ollama'):
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

    message = [
                {"role": "user", "content": prompt_text}
            ]

    if api == 'openai':
        response = client.chat.completions.create(
            model=model_name,
            messages= message)

        return response.choices[0].message.content.strip()
    elif api == 'ollama':
        response = ollama.chat(model=model_name, 
                              messages=message)
        return response['message']['content'].strip()

    else:
        raise Exception('Miss an api')



def save_to_tsv(result, output_file='gender_data_dict.tsv'):
    with open(output_file, mode='a', newline='') as file:
        writer = csv.writer(file, delimiter='\t')
        
        if file.tell() == 0:
            writer.writerow(['author', 'gender_author', 'reasoning_author'])
        try:
            author_name = result.get("author", {}).get("name", "")
        #FIXME: Change the exception for the right one
        except Exception: 
            author_name = None
        try:
            gender_author = result.get("author", {}).get("gender", "")
        #FIXME: Change the exception for the right one
        except Exception: 
            gender_author = None
        try:
            reasoning_author = result.get("author", {}).get("reasoning", "")
        #FIXME: Change the exception for the right one
        except Exception: 
            reasoning_author = None
        writer.writerow([author_name, gender_author, reasoning_author])


def main(model, install_llm_model_flag=False):
    if install_llm_model_flag:
        install_llm_model(model)

    client = OpenAI(
        base_url="http://localhost:11434/v1", api_key="ollama"  # required, but unused
    )

    model_name = model
    csv_data_filename = "data/enriched_aggregated_papers.csv"

    size_data = (
        sum(1 for _ in open(csv_data_filename)) - 1
    )  # Subtract 1 to exclude the header row

    set_authors = set()
    for (
        first_author_firstname,
        first_author_lastname,
        last_author_firstname,
        last_author_lastname,
    ) in tqdm(parse_csv(csv_data_filename), total=size_data):
        if (
            pd.isna(first_author_firstname)
            or pd.isna(first_author_lastname)
            or pd.isna(last_author_firstname)
            or pd.isna(last_author_lastname)
        ):
            continue  # Skips to the next iteration if any name is NaN

        firstauthor = f"{first_author_firstname} {first_author_lastname}"
        lastauthor = f"{last_author_firstname} {last_author_lastname}"
        if firstauthor == lastauthor:
            to_parse = (firstauthor)
        else:
            to_parse = (firstauthor, lastauthor)

        for author in to_parse:

            if author in set_authors:
                continue
            set_authors.add(author)
            json_gender_response = infer_gender(
                client, model_name, author)
            json_match = re.search(r"{.*}", json_gender_response, re.DOTALL)
            if json_match:
                json_text = json_match.group(0)
                try:
                    result = json.loads(json_text)
                    save_to_tsv(result)
                except json.JSONDecodeError as e:
                    print("Failed to parse JSON:", e)
            else:
                print("No JSON found in the response content.")



if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-m", "--model", help="Name of the LLM model")
    parser.add_argument(
        "--install-model", action="store_true", help="Install the model"
    )

    args = parser.parse_args()

    main(args.model, args.install_model)
