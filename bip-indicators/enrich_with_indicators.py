import pandas as pd
import requests
import time

# Step 1: Read the TSV file (tab-separated)
df = pd.read_csv('enriched_aggregated_papers_with_topics.csv', sep='\t')  # Replace with actual input filename
dois = df['final_doi'].dropna().unique()  # Remove NaN values and get unique DOIs

# Prepare the output TSV and write the header
output_file = 'enriched_aggregated_papers_with_topics_and_bip_scores.csv'
header_written = False  # To track whether header is written

# Initialize counters
found_count = 0
not_found_count = 0

# Function to request data for a batch of DOIs
def get_bip_scores(dois_batch):
    dois_query = ','.join([doi.replace('/', '%2F') for doi in dois_batch])  # URL encode DOIs
    url = f"https://bip-api.imsi.athenarc.gr/paper/scores/batch/{dois_query}"
    
    response = requests.get(url)
    if response.status_code == 200:
        return response.json()  # Return JSON response
    else:
        print(f"Error fetching data for batch: {dois_batch}")
        return []

# Step 3: Process each batch and write results incrementally
batch_size = 50
all_records = []

for i in range(0, len(dois), batch_size):
    batch = dois[i:i+batch_size]
    bip_data = get_bip_scores(batch)
    
    # Convert the batch result to a list of records, handling missing fields for "Not Found" entries
    records = []
    for record in bip_data:
        if "msg" in record and record["msg"] == "Not Found":
            not_found_count += 1
            # DOI was not found, add NaN or placeholder values
            records.append({
                "final_doi": record["doi"],
                "popularity": None,
                "influence": None,
                "impulse": None,
                "cc": None,
                "pop_class": None,
                "inf_class": None,
                "imp_class": None
            })
        else:
            found_count += 1
            # Normal record, add with renamed fields
            records.append({
                "final_doi": record.get("doi"),
                "popularity": record.get("attrank"),
                "influence": record.get("pagerank"),
                "impulse": int(record.get("3_year_cc", 0)),  # Handle possible None by defaulting to 0
                "cc": int(record.get("cc", 0)),               # Handle possible None by defaulting to 0
                "pop_class": record.get("pop_class"),
                "inf_class": record.get("inf_class"),
                "imp_class": record.get("imp_class")
            })

    # Append batch records to all_records to keep track of all results
    all_records.extend(records)

    # Pause between requests to respect API limits
    time.sleep(0.2)

# Convert all records to a DataFrame and merge back with original to preserve row count
bip_df = pd.DataFrame(all_records)
merged_df = df.merge(bip_df, on='final_doi', how='left')

# Write to output TSV with all rows once
merged_df.to_csv(output_file, sep='\t', index=False)

# Print the final counts
print(f"DOIs found: {found_count}")
print(f"DOIs not found: {not_found_count}")
print(f"Results saved to '{output_file}' with {len(merged_df)} rows.")
