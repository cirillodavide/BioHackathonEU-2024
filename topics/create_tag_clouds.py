import pandas as pd
import numpy as np
from wordcloud import WordCloud
import matplotlib.pyplot as plt
import json

# Read the CSV file with tab delimiter
df = pd.read_csv('enriched_aggregated_papers_with_topics.csv', sep='\t')

# Function to safely parse JSON and extract display names, subfields, fields, and domains
def extract_display_names(row):
    if pd.isna(row['openalex_topics']):
        return [], [], [], []  # Return empty lists if the data is NaN
    try:
        items = json.loads(row['openalex_topics'])
        topics = [item['display_name'] for item in items]
        subfields = [item['subfield']['display_name'] for item in items if 'subfield' in item]
        fields = [item['field']['display_name'] for item in items if 'field' in item]
        domains = [item['domain']['display_name'] for item in items if 'domain' in item]
        return topics, subfields, fields, domains
    except (ValueError, TypeError):
        return [], [], [], []  # Return empty lists on error

# Apply the function to extract topics, subfields, fields, and domains
df[['extracted_topics', 'extracted_subfields', 'extracted_fields', 'extracted_domains']] = df.apply(
    lambda row: pd.Series(extract_display_names(row)), axis=1
)

# Create a function to generate and save a tag cloud
def create_tag_cloud(data, title, filename):
    text = ' '.join([item for sublist in data.dropna() for item in sublist])
    wordcloud = WordCloud(width=800, height=400, background_color='white').generate(text)

    # Save the word cloud image to a file
    wordcloud.to_file(filename)

# Create and save tag clouds for topics, subfields, fields, and domains
create_tag_cloud(df['extracted_topics'], 'Topics Tag Cloud', 'tagclouds/topics_tag_cloud.png')
create_tag_cloud(df['extracted_subfields'], 'Subfields Tag Cloud', 'tagclouds/subfields_tag_cloud.png')
create_tag_cloud(df['extracted_fields'], 'Fields Tag Cloud', 'tagclouds/fields_tag_cloud.png')
create_tag_cloud(df['extracted_domains'], 'Domains Tag Cloud', 'tagclouds/domains_tag_cloud.png')
