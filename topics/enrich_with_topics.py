import pandas as pd
import requests
import sys
import time
import json

# Load the file path from the command line argument
aggregated_papers_fd = sys.argv[1]

# Load TSV into DataFrame
df = pd.read_csv(aggregated_papers_fd, sep='\t')

# Initialize the new columns
df['topics'] = None
df['subfields'] = None
df['fields'] = None
df['domains'] = None

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

# Function to query OpenAlex API
def get_topics(openalex_url):
    global success_count, not_found_count, error_count
    response = requests.get(openalex_url, headers=headers)
    time.sleep(0.1)  # Rate limiting
    
    if response.status_code == 200:
        success_count += 1
        data = response.json()
        if 'topics' in data:
            # Extract topics, subfields, fields, domains
            topics = []
            subfields = []
            fields = []
            domains = []

            for concept in data['topics']:
                topics.append(concept['display_name'])
                subfields.append(concept['subfield']['display_name'] if 'subfield' in concept else '')
                fields.append(concept['field']['display_name'] if 'field' in concept else '')
                domains.append(concept['domain']['display_name'] if 'domain' in concept else '')

            return {
                "topics": '|'.join(topics),
                "subfields": '|'.join(set(subfields)),  # Use set to remove duplicates
                "fields": '|'.join(set(fields)),
                "domains": '|'.join(set(domains))
            }
    elif response.status_code == 404:
        not_found_count += 1
    else:
        error_count += 1
        print(f"Error: Status code {response.status_code} for URL: {openalex_url}")

    return None  # Return None if the request was not successful

# Function to build OpenAlex URL and try with fallbacks
def fetch_openalex_topics(row):
    # Try DOI, then PMID, then PMCID
    doi_list = str(row['final_doi']).split('|') if pd.notna(row['final_doi']) else []
    pmid_list = str(row['pmid']).split('|') if pd.notna(row['pmid']) else []
    pmcid_list = str(row['pmcid']).split('|') if pd.notna(row['pmcid']) else []

    for doi in doi_list:
        openalex_url = f"{api_base_url}/doi/{doi.strip()}?mailto={email}"
        topics_data = get_topics(openalex_url)
        if topics_data:
            return topics_data

    for pmid in pmid_list:
        openalex_url = f"{api_base_url}/pmid:{int(float(pmid.strip()))}?mailto={email}"
        topics_data = get_topics(openalex_url)
        if topics_data:
            return topics_data

    for pmcid in pmcid_list:
        openalex_url = f"{api_base_url}/pmcid:{pmcid.strip()}?mailto={email}"
        topics_data = get_topics(openalex_url)
        if topics_data:
            return topics_data

    return None

# Output file
output_file = "enriched_aggregated_papers_with_topics.csv"
df.iloc[0:0].to_csv(output_file, sep='\t', index=False)  # Write header

# Apply the topic-fetching function
for index, row in df.iterrows():
    topics_data = fetch_openalex_topics(row)
    
    # Assign the data to the DataFrame columns
    if topics_data:
        df.at[index, 'topics'] = topics_data["topics"]
        df.at[index, 'subfields'] = topics_data["subfields"]
        df.at[index, 'fields'] = topics_data["fields"]
        df.at[index, 'domains'] = topics_data["domains"]

    # Write the updated row to the file
    row_with_topics = row.copy()  # Make a copy of the row
    row_with_topics['topics'] = topics_data["topics"] if topics_data else None
    row_with_topics['subfields'] = topics_data["subfields"] if topics_data else None
    row_with_topics['fields'] = topics_data["fields"] if topics_data else None
    row_with_topics['domains'] = topics_data["domains"] if topics_data else None

    # Append to file without the header
    row_with_topics.to_frame().T.to_csv(output_file, sep='\t', mode='a', header=False, index=False)
    
print("Processing complete. Check the output file for enriched data.")
