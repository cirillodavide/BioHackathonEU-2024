import pandas as pd
from collections import Counter

# Load the CSV file
file_path = 'enriched_aggregated_papers_with_topics_and_bip_scores.csv'
df = pd.read_csv(file_path, sep='\t')  # Adjust delimiter if necessary

# Function to count and rank occurrences in a specific column
def count_and_rank(column_name, output_filename):
    counter = Counter()
    for entry in df[column_name].dropna():
        items = entry.split('|')  # Split by '|'
        counter.update(items)     # Update counts for each item
    
    # Convert counter to a sorted DataFrame
    result_df = pd.DataFrame(counter.items(), columns=['id', 'frequency'])  # Rename first column to 'id'
    result_df = result_df.sort_values(by='frequency', ascending=False).reset_index(drop=True)
    
    # Save to a CSV file
    result_df.to_csv(output_filename, index=False, sep='\t')
    print(f"Ranked frequencies for {column_name} saved to '{output_filename}'")

out_folder = 'elixir-topic-counts/'

# Apply the function to each column of interest
count_and_rank('topic_ids', out_folder + 'topic_frequencies_ranked.csv')
count_and_rank('field_ids', out_folder + 'field_frequencies_ranked.csv')
count_and_rank('subfield_ids', out_folder + 'subfield_frequencies_ranked.csv')
count_and_rank('domain_ids', out_folder + 'domain_frequencies_ranked.csv')
