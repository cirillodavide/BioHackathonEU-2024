import pandas as pd
import requests
import sys
import time
import json

# Load the file path from the command line argument
aggregated_papers_fd = sys.argv[1]

# Load TSV into DataFrame
df = pd.read_csv(aggregated_papers_fd, sep='\t')

# Initialize the 'openalex_topics' column with None
df['openalex_topics'] = None

# Configuration
email = "s.chatzopoulos@gmail.com"  # Update to your actual email
api_base_url = "https://api.openalex.org/works"
headers = {
    "User-Agent": f"MyApp/1.0 (mailto:{email})"
}

# Counters for request statuses
success_count = 0
not_found_count = 0
error_count = 0

# Counters for each ID type attempt
doi_attempts = 0
pmid_attempts = 0
pmcid_attempts = 0

# Time-tracking for periodic printout
start_time = time.time()
status_print_interval = 60  # seconds

# Function to query OpenAlex API with rate limiting and status tracking
def get_topics(openalex_url):
    global success_count, not_found_count, error_count
    response = requests.get(openalex_url, headers=headers)
    time.sleep(0.1)  # 5 requests per second = 0.2 second delay
    
    if response.status_code == 200:
        success_count += 1
        data = response.json()
        if 'topics' in data:
            return data['topics']
    elif response.status_code == 404:
        not_found_count += 1
    else:
        error_count += 1
        print(f"Error: Status code {response.status_code} for URL: {openalex_url}")

    return None  # Return None if the request was not successful

# Function to build OpenAlex URL and try with fallbacks
def fetch_openalex_topics(row):
    global doi_attempts, pmid_attempts, pmcid_attempts
    
    # Split identifiers by '|'
    doi_list = str(row['final_doi']).split('|') if pd.notna(row['final_doi']) else []
    pmid_list = str(row['pmid']).split('|') if pd.notna(row['pmid']) else []
    pmcid_list = str(row['pmcid']).split('|') if pd.notna(row['pmcid']) else []

    # Attempt with DOI
    for doi in doi_list:
        doi_attempts += 1
        doi = doi.strip()  # Clean whitespace
        openalex_url = f"{api_base_url}/doi/{doi}?mailto={email}"
        topics = get_topics(openalex_url)
        if topics:  # Return topics if found using DOI
            return json.dumps(topics)

    # Attempt with PMID
    for pmid in pmid_list:
        pmid_attempts += 1
        pmid_value = float(pmid.strip())  # Convert to float first
        openalex_url = f"{api_base_url}/pmid:{int(pmid_value)}?mailto={email}"
        topics = get_topics(openalex_url)
        if topics:  # Return topics if found using PMID
            return json.dumps(topics)

    # Attempt with PMCID
    for pmcid in pmcid_list:
        pmcid_attempts += 1
        pmcid = pmcid.strip()  # Clean whitespace
        openalex_url = f"{api_base_url}/pmcid:{pmcid}?mailto={email}"
        topics = get_topics(openalex_url)
        if topics:  # Return topics if found using PMCID
            return json.dumps(topics)

    return None  # Return None if no topics were found for any identifier

# Open the output file in write mode first to create the header
output_file = "enriched_aggregated_papers_with_topics.csv"
df.iloc[0:0].to_csv(output_file, sep='\t', index=False)  # Write the header only

# Apply the topic-fetching function to each row with periodic status output
for index, row in df.iterrows():
    topics = fetch_openalex_topics(row)
    df.at[index, 'openalex_topics'] = topics

    # Write the entire row to the file immediately
    row_with_topics = row.copy()  # Make a copy of the row
    row_with_topics['openalex_topics'] = topics  # Assign the fetched topics
    row_with_topics.to_frame().T.to_csv(output_file, sep='\t', mode='a', header=False, index=False)

    # Print status every specified interval
    if (time.time() - start_time) >= status_print_interval:
        print(f"Requests succeeded: {success_count}")
        print(f"Requests not found (404): {not_found_count}")
        print(f"Requests errored: {error_count}")
        print(f"DOI attempts: {doi_attempts}")
        print(f"PMID attempts: {pmid_attempts}")
        print(f"PMCID attempts: {pmcid_attempts}")
        print()
        start_time = time.time()  # reset start time after each print

# Final status output after completing all requests
print("Final counts after processing all rows:")
print(f"Requests succeeded: {success_count}")
print(f"Requests not found (404): {not_found_count}")
print(f"Requests errored: {error_count}")
print(f"DOI attempts: {doi_attempts}")
print(f"PMID attempts: {pmid_attempts}")
print(f"PMCID attempts: {pmcid_attempts}")
