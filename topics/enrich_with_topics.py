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
df['topic_ids'] = None
df['subfield_ids'] = None
df['field_ids'] = None
df['domain_ids'] = None

# Configuration
email = "s.chatzopoulos@gmail.com"  # Update to your actual email
api_base_url = "https://api.openalex.org/works"
headers = {
    "User-Agent": f"MyApp/1.0 (mailto:{email})"
}

# Function to query OpenAlex API
def get_topics(openalex_url):
    response = requests.get(openalex_url, headers=headers)
    time.sleep(0.1)  # Rate limiting
    
    if response.status_code == 200:
        data = response.json()
        if 'topics' in data:
            # Initialize lists for names and ids
            topics, topic_ids = [], []
            subfields, subfield_ids = [], []
            fields, field_ids = [], []
            domains, domain_ids = [], []

            # Extract both display_name and id for each concept
            for concept in data['topics']:
                topics.append(concept['display_name'])
                topic_ids.append(concept['id'])
                
                # Extract subfields, fields, domains with IDs if present
                if 'subfield' in concept:
                    subfields.append(concept['subfield']['display_name'])
                    subfield_ids.append(concept['subfield']['id'])
                if 'field' in concept:
                    fields.append(concept['field']['display_name'])
                    field_ids.append(concept['field']['id'])
                if 'domain' in concept:
                    domains.append(concept['domain']['display_name'])
                    domain_ids.append(concept['domain']['id'])

            # Join each list of names and IDs with '|'
            return {
                "topics": '|'.join(topics),
                "topic_ids": '|'.join(topic_ids),
                "subfields": '|'.join(set(subfields)),
                "subfield_ids": '|'.join(set(subfield_ids)),
                "fields": '|'.join(set(fields)),
                "field_ids": '|'.join(set(field_ids)),
                "domains": '|'.join(set(domains)),
                "domain_ids": '|'.join(set(domain_ids))
            }
    elif response.status_code == 404:
        print(f"Not found: {openalex_url}")
    else:
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
        df.at[index, 'topic_ids'] = topics_data["topic_ids"]
        df.at[index, 'subfields'] = topics_data["subfields"]
        df.at[index, 'subfield_ids'] = topics_data["subfield_ids"]
        df.at[index, 'fields'] = topics_data["fields"]
        df.at[index, 'field_ids'] = topics_data["field_ids"]
        df.at[index, 'domains'] = topics_data["domains"]
        df.at[index, 'domain_ids'] = topics_data["domain_ids"]

    # Write the updated row to the file without the header
    df.loc[[index]].to_csv(output_file, sep='\t', mode='a', header=False, index=False)

print("Processing complete. Check the output file for enriched data.")
