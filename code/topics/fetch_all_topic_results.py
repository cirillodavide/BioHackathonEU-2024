import pandas as pd
import requests
import time
import csv
import os

# Configuration
email = "s.chatzopoulos@gmail.com"  # Update with your actual email
api_base_url = "https://api.openalex.org/works"
headers = {
    "User-Agent": f"MyApp/1.0 (mailto:{email})"
}
input_folder = 'elixir-topic-counts'  # Folder with category frequency files
output_folder = 'topic-results'
statistics_file = os.path.join(output_folder, 'category_statistics.csv')

# Ensure output folders exist for each category
categories = {
    # 'topics': 'topic_frequencies_ranked.csv',
    'domains': 'domain_frequencies_ranked.csv',
    'fields': 'field_frequencies_ranked.csv',
    'subfields': 'subfield_frequencies_ranked.csv'
}

for category in categories:
    category_folder = os.path.join(output_folder, category)
    if not os.path.exists(category_folder):
        os.makedirs(category_folder)

# Initialize the statistics file
if not os.path.exists(statistics_file):
    with open(statistics_file, 'w', newline='', encoding='utf-8') as statfile:
        writer = csv.DictWriter(statfile, fieldnames=["category", "id", "meta_count", "total_papers", "unique_authors"], delimiter='\t')
        writer.writeheader()

# Function to read the first 10 entries from a category file
def get_first_10_entries(file_name):
    df = pd.read_csv(os.path.join(input_folder, file_name), sep='\t')
    # Assuming the ID column is named 'id' or similarly identifiable in each file
    return df['id'].head(10).tolist()

# Fetch and process OpenAlex data for each category entry
def fetch_category_data(category, entry_id):
    # Extract the ID suffix (e.g., T11577 from https://openalex.org/T11577)
    entry_id_simple = entry_id.split('/')[-1]
    
    # Adjust the filter syntax based on category
    filter_type = {
        "topics": "topics.id",
        "domains": "topics.domain.id",
        "fields": "topics.field.id",
        "subfields": "topics.subfield.id"
    }
    
    # API URL with the correct filter for the category
    url = f"{api_base_url}?filter={filter_type[category]}:{entry_id_simple}&select=id,doi,publication_year,authorships&per-page=200&cursor=*"
    cursor = '*'
    results_count = 0
    all_authors = set()
    meta_count = 0
    
    # Prepare file paths
    output_file = os.path.join(output_folder, category, f"{entry_id_simple}.csv")
    with open(output_file, 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=["category", "entry_id", "openalex_id", "doi", "publication_year", "authors"], delimiter='\t')
        writer.writeheader()
    
    while cursor and results_count < 5000:
        response = requests.get(url, headers=headers)
        time.sleep(0.1)  # Delay to avoid rate limits
        
        if response.status_code == 200:
            data = response.json()
            results = data['results']
            meta_count = data['meta'].get('count', 0)  # Get total count from meta
            
            results_count += len(results)
            category_results = []
            for record in results:
                openalex_id = record.get("id")
                doi = record.get("doi")
                publication_year = record.get("publication_year")
                
                # Process authors
                authors = []
                for author_entry in record.get("authorships", []):
                    author_name = author_entry.get("author", {}).get("display_name")
                    if author_name:
                        authors.append(author_name)
                        all_authors.add(author_name)
                
                authors_str = ', '.join(authors)
                
                category_results.append({
                    "category": category,
                    "entry_id": entry_id,
                    "openalex_id": openalex_id,
                    "doi": doi,
                    "publication_year": publication_year,
                    "authors": authors_str
                })
            
            # Write data for the current page to the output file
            with open(output_file, 'a', newline='', encoding='utf-8') as csvfile:
                writer = csv.DictWriter(csvfile, fieldnames=["category", "entry_id", "openalex_id", "doi", "publication_year", "authors"], delimiter='\t')
                writer.writerows(category_results)
            
            cursor = data['meta'].get('next_cursor')
            url = f"{api_base_url}?filter={filter_type[category]}:{entry_id_simple}&select=id,doi,publication_year,authorships&per-page=200&cursor={cursor}"
        else:
            print(f"Failed to fetch data for {category} ID {entry_id_simple} with status {response.status_code}")
            break

    # Write statistics to the main statistics file
    total_papers = results_count
    total_authors = len(all_authors)
    with open(statistics_file, 'a', newline='', encoding='utf-8') as statfile:
        writer = csv.DictWriter(statfile, fieldnames=["category", "id", "meta_count", "total_papers", "unique_authors"], delimiter='\t')
        writer.writerow({
            "category": category,
            "id": entry_id,
            "meta_count": meta_count,
            "total_papers": total_papers,
            "unique_authors": total_authors
        })

# Process the first 10 entries for each category
for category, file_name in categories.items():
    first_10_entries = get_first_10_entries(file_name)
    
    for entry_id in first_10_entries:
        fetch_category_data(category, entry_id)

print(f"Data for the first 10 entries in each category has been saved in the '{output_folder}' folder.")
print(f"Statistics have been saved in '{statistics_file}'.")
