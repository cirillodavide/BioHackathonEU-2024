import pandas as pd
import requests
import time
import csv
import os

# Read the file with the topic IDs
file_path = 'enriched_aggregated_papers_with_topics_and_bip_scores.csv'
df = pd.read_csv(file_path, sep='\t')

# Configuration
email = "s.chatzopoulos@gmail.com"  # Update with your actual email
api_base_url = "https://api.openalex.org/works"
headers = {
    "User-Agent": f"MyApp/1.0 (mailto:{email})"
}

# Extract unique topic IDs
unique_topic_ids = set()
for topic_id_str in df['topic_ids'].dropna():
    topic_ids = topic_id_str.split('|')  # Split by '|'
    unique_topic_ids.update(topic_ids)  # Add to the set for unique IDs

# Output folder
output_folder = 'topic-results'
statistics_file = 'topic_statistics.csv'

# Create the output folder if it doesn't exist
if not os.path.exists(output_folder):
    os.makedirs(output_folder)

# Initialize the statistics file with headers if it's new
if not os.path.exists(statistics_file):
    with open(statistics_file, 'w', newline='', encoding='utf-8') as statfile:
        writer = csv.DictWriter(statfile, fieldnames=["topic_id", "meta_count", "total_papers", "unique_authors"], delimiter='\t')
        writer.writeheader()

# Function to query OpenAlex API for a topic ID with pagination and limit results to 10,000
def fetch_topic_data(topic_id):
    # Extract just the last part of the topic ID (e.g., T11577 from https://openalex.org/T11577)
    topic_id_simple = topic_id.split('/')[-1]
    
    url = f"{api_base_url}?filter=topics.id:{topic_id}&select=id,doi,publication_year,authorships&per-page=200&cursor=*"
    cursor = '*'
    results_count = 0
    all_authors = set()  # Track all unique authors
    meta_count = 0  # Total count from metadata
    
    # Prepare the file path for the current topic ID
    output_file = os.path.join(output_folder, f"{topic_id_simple}.csv")
    
    # Initialize the output file with headers for the first write
    with open(output_file, 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=["topic_id", "openalex_id", "doi", "publication_year", "authors"], delimiter='\t')
        writer.writeheader()

    while cursor and results_count < 10000:
        response = requests.get(url, headers=headers)
        time.sleep(0.1)  # Add a delay to avoid hitting rate limits
        
        if response.status_code == 200:
            data = response.json()
            results = data['results']
            meta_count = data['meta'].get('count', 0)  # Get the total count from meta
            
            results_count += len(results)
            
            topic_results = []
            for record in results:
                # Extract work details
                openalex_id = record.get("id")
                doi = record.get("doi")
                publication_year = record.get("publication_year")
                
                # Join author display names
                authors = []
                for author_entry in record.get("authorships", []):
                    author_name = author_entry.get("author", {}).get("display_name")
                    if author_name:
                        authors.append(author_name)
                        all_authors.add(author_name)  # Add to the set of unique authors
                
                authors_str = ', '.join(authors)
                
                topic_results.append({
                    "topic_id": topic_id,
                    "openalex_id": openalex_id,
                    "doi": doi,
                    "publication_year": publication_year,
                    "authors": authors_str
                })
            
            # Write results to the topic-specific file as they are fetched
            with open(output_file, 'a', newline='', encoding='utf-8') as csvfile:
                writer = csv.DictWriter(csvfile, fieldnames=["topic_id", "openalex_id", "doi", "publication_year", "authors"], delimiter='\t')
                writer.writerows(topic_results)
            
            # Update cursor for the next page
            cursor = data['meta'].get('next_cursor')
            url = f"{api_base_url}?filter=topics.id:{topic_id}&select=id,doi,publication_year,authorships&per-page=200&cursor={cursor}"
        else:
            print(f"Failed to fetch data for topic ID {topic_id} with status {response.status_code}")
            break

    # After collecting all data for the topic, write the statistics (total papers and unique authors)
    total_papers = results_count
    total_authors = len(all_authors)
    
    # Write statistics to the separate statistics file
    with open(statistics_file, 'a', newline='', encoding='utf-8') as statfile:
        writer = csv.DictWriter(statfile, fieldnames=["topic_id", "meta_count", "total_papers", "unique_authors"], delimiter='\t')
        writer.writerow({
            "topic_id": topic_id,
            "meta_count": meta_count,
            "total_papers": total_papers,
            "unique_authors": total_authors
        })

# Loop through each unique topic ID and fetch paginated data, writing each topic's data to a separate file
for topic_id in unique_topic_ids:
    fetch_topic_data(topic_id)

print(f"Data for all topics has been saved in the '{output_folder}' folder.")
print(f"Statistics have been saved in '{statistics_file}'.")
