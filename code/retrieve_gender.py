import os
import httpx
import json
import csv
import re
import logging
import argparse
import asyncio
import subprocess
from tqdm import tqdm
import pandas as pd
from openai import OpenAI
from ollama import AsyncClient
import ollama
from prompt import get_gender_prompt

logging.basicConfig(level=logging.WARNING)


def extract_author_names(chunk, author_type):
    """Helper function to extract and strip author names, ensuring they are valid strings."""
    # Try to get the first and last names, default to empty strings if not found
    first_name = (
        chunk.get(f"{author_type}_firstName", "").values[0]
        if f"{author_type}_firstName" in chunk
        else ""
    )
    last_name = (
        chunk.get(f"{author_type}_lastName", "").values[0]
        if f"{author_type}_lastName" in chunk
        else ""
    )
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


async def infer_gender(
    client,
    queue,
    model_name,
    author_firstname,
    author_lastname,
    progress_bar,
    api="ollama",
    loaded_models_semaphore=None,
    parallel_requests_semaphore=None,
):
    prompt_text = get_gender_prompt(author_firstname, author_lastname)
    message = [{"role": "user", "content": prompt_text}]
    retries = 3

    async with loaded_models_semaphore:

        async with parallel_requests_semaphore:
            try:
                if api == "openai":
                    response = await client.chat.completions.create(
                        model=model_name, messages=message
                    )

                    await queue.put(response.choices[0].message.content.strip())
                elif api == "ollama":
                    response = await AsyncClient().chat(
                        model=model_name, messages=message
                    )

                    await queue.put(response["message"]["content"].strip())

                else:
                    raise Exception("Miss an api")
            except httpx.ConnectError as e:
                print(f"Failed to connect to {api} API: {e}")
            except Exception as e:
                print(f"Error during API call: {e}")
        # Update the progress bar as soon as each task completes
    progress_bar.update(1)


async def save_to_tsv(queue, output_file="gender_data_dict.tsv"):
    with open(output_file, mode="a", newline="") as file:
        writer = csv.writer(file, delimiter="\t")
        if file.tell() == 0:
            writer.writerow(["first_name", "last_name", "gender", "reasoning"])

        while True:
            result = await queue.get()
            # When receive the None signal that the queue is empty
            if result is None:
                break
            json_match = re.search(r"{.*}", result, re.DOTALL)
            if json_match:
                json_text = json_match.group(0)
                try:
                    result_data = json.loads(json_text)
                    try:
                        first_name = result_data.get("author", {}).get("first_name", "")
                    # FIXME: Change the exception for the right one
                    except Exception:
                        first_name = None
                    try:
                        last_name = result_data.get("author", {}).get("last_name", "")
                    # FIXME: Change the exception for the right one
                    except Exception:
                        last_name = None
                    try:
                        gender_author = result_data.get("author", {}).get("gender", "")
                    # FIXME: Change the exception for the right one
                    except Exception:
                        gender_author = None
                    try:
                        reasoning_author = result_data.get("author", {}).get(
                            "reasoning", ""
                        )
                    # FIXME: Change the exception for the right one
                    except Exception:
                        reasoning_author = None
                    writer.writerow(
                        [first_name, last_name, gender_author, reasoning_author]
                    )
                except json.JSONDecodeError as e:
                    print("Failed to parse JSON:", e)
            else:
                print("No JSON found in the response content.")
            queue.task_done()  # Mark the task as done


def get_already_done_authors(file_path):
    # Check if file exists
    if not os.path.exists(file_path):
        return set()
    first_column_set = set()

    # Open the TSV file and read the first column without header
    with open(file_path, newline="") as file:
        reader = csv.reader(file, delimiter="\t")
        next(reader, None)  # Skip the header row if present
        first_column_set = {
            row[0] for row in reader if row
        }  # Set comprehension, handles empty rows
    return first_column_set


async def main(model, install_llm_model_flag=False, continue_file_flag=False):
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
    # Create a queue to avoid race condition in recording results
    queue = asyncio.Queue()
    # Create a tasks list for inference
    tasks = []

    # Setting concurrency maximum
    ## Get environment variables with fallback defaults
    max_loaded_models = int(os.getenv("OLLAMA_MAX_LOADED_MODELS", 3))
    num_parallel = int(os.getenv("OLLAMA_NUM_PARALLEL", 4))
    max_queue = int(os.getenv("OLLAMA_MAX_QUEUE", 512))

    # Define semaphores based on concurrency limits
    # 1. Semaphore for limiting total number of loaded models concurrently
    loaded_models_semaphore = asyncio.Semaphore(max_loaded_models)

    # 2. Semaphore for parallel requests per model
    parallel_requests_semaphore = asyncio.Semaphore(num_parallel)

    # Start the saving to tsv in background
    asyncio.create_task(save_to_tsv(queue, output_file=csv_results_filename))

    with tqdm(total=size_data) as progress_bar:
        for firstname, lastname in parse_csv(csv_data_filename):
            if firstname and lastname:
                author = f"{firstname} {lastname}"
                if author in set_authors:
                    continue
                set_authors.add(author)

                tasks.append(
                    infer_gender(
                        client=client,
                        queue=queue,
                        model_name=model_name,
                        author_firstname=firstname,
                        author_lastname=lastname,
                        progress_bar=progress_bar,
                        loaded_models_semaphore=loaded_models_semaphore,
                        parallel_requests_semaphore=parallel_requests_semaphore,
                    )
                )

        # Await all tasks concurrently (inference tasks)
        await asyncio.gather(*tasks)
        # Signal the consumer to stop after all tasks are done
        await queue.put(None)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-m", "--model", help="Name of the LLM model")
    parser.add_argument(
        "--install-model", action="store_true", help="Install the model"
    )
    parser.add_argument(
        "-c",
        "--continue_file",
        action="store_true",
        help="To continue an existing parsed file and get the list of names",
    )

    args = parser.parse_args()

    try:
        asyncio.run(main(args.model, args.install_model, args.continue_file))
    except (KeyboardInterrupt, EOFError):
        raise
