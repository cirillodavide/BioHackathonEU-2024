import os
import json
import csv
import re
import argparse
import asyncio
import subprocess
from tqdm import tqdm
import pandas as pd
from openai import OpenAI
import ollama
from prompt import get_gender_prompt

def extract_author_names(chunk, author_type):
    """Helper function to extract and strip author names, ensuring they are valid strings."""
    # Try to get the first and last names, default to empty strings if not found
    first_name = chunk.get(f"{author_type}_firstName", "").values[0] if f"{author_type}_firstName" in chunk else ""
    last_name = chunk.get(f"{author_type}_lastName", "").values[0] if f"{author_type}_lastName" in chunk else ""
    # Check if first and last names are valid strings (non-empty and of type string)
    if isinstance(first_name, str) and isinstance(last_name, str):
        first_name = first_name.strip()
        last_name = last_name.strip()
        # Only return if both names are non-empty
        if first_name and last_name:
            return (first_name, last_name)
    return None

def parse_csv(file):
    try:
        # Read the CSV in chunks, specifying separator and error handling
        df_iter = pd.read_csv(file, on_bad_lines="skip", sep="\t", chunksize=1)
        for chunk in df_iter:
            try:
                # Extract first and last author information
                first_author = extract_author_names(chunk, "first_author")
                last_author = extract_author_names(chunk, "last_author")
                # Yield first author (if present)
                if first_author:
                    yield first_author
                # Yield last author (if present)
                if last_author:
                    yield last_author

            except KeyError as e:
                print(f"Column not found in CSV: {e}")
                continue  # Skip rows with missing columns

    except Exception as e:
        print(f"Error reading CSV: {e}")
        return  # Returns None if there's an error opening the file

def install_llm_model(model_name):
    try:
        subprocess.run(["ollama", "pull", model_name], check=True)
    except subprocess.CalledProcessError as e:
        print(f"An error occurred while installing the model: {e}")


def infer_gender(client, model_name, author_firstname, author_lastname, api='ollama'):
    prompt_text = get_gender_prompt(author_firstname, author_lastname)
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
            writer.writerow(['first_name', 'last_name', 'gender', 'reasoning'])
        try:
            first_name = result.get("author", {}).get("first_name", "")
        #FIXME: Change the exception for the right one
        except Exception: 
            first_name = None
        try:
            last_name = result.get("author", {}).get("last_name", "")
        #FIXME: Change the exception for the right one
        except Exception: 
            last_name = None
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
        writer.writerow([first_name, last_name, gender_author, reasoning_author])

def get_already_done_authors(file_path):
    # Check if file exists
    if not os.path.exists(file_path):
        return set()
    first_column_set = set()

    # Open the TSV file and read the first column without header
    with open(file_path, newline='') as file:
        reader = csv.reader(file, delimiter='\t')
        next(reader, None)  # Skip the header row if present
        first_column_set = {row[0] for row in reader if row}  # Set comprehension, handles empty rows
    return first_column_set


def main(model, install_llm_model_flag=False, continue_file_flag=False):
    if install_llm_model_flag:
        install_llm_model(model)

    client = OpenAI(
        base_url="http://localhost:11434/v1", api_key="ollama"  # required, but unused
    )

    model_name = model
    csv_data_filename = "data/enriched_aggregated_papers.csv"
    source_filename = os.path.splitext(os.path.basename(csv_data_filename))[0]
    csv_results_filename = f"data/{source_filename}_gender_authors_{model_name}.tsv"


    size_data = (
        sum(1 for _ in open(csv_data_filename)) - 1
    )  # Subtract 1 to exclude the header row

    # Get the authors already parsed
    if continue_file_flag: 
        set_authors = get_already_done_authors(csv_results_filename)
    else:
        set_authors = set()

    for firstname, lastname in tqdm(parse_csv(csv_data_filename), total=size_data):
        if firstname and lastname:
            author = f"{firstname} {lastname}"
            if author in set_authors:
                continue
            set_authors.add(author)
            json_gender_response = infer_gender(
                client, model_name, firstname, lastname)
            json_match = re.search(r"{.*}", json_gender_response, re.DOTALL)
            if json_match:
                json_text = json_match.group(0)
                try:
                    result = json.loads(json_text)
                    save_to_tsv(result, output_file=csv_results_filename)
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
    parser.add_argument('-c', "--continue_file", action="store_true", help='To continue an existing parsed file and get the list of names')

    args = parser.parse_args()

    main(args.model, args.install_model, args.continue_file)
