import pandas as pd
from collections import Counter
from wordcloud import WordCloud
import matplotlib.pyplot as plt

# Read the CSV file with tab delimiter
df = pd.read_csv('enriched_aggregated_papers_with_topics.csv', sep='\t')

# Helper function to split and flatten columns containing '|' separated values, and get frequencies
def get_frequency_dict(column_data):
    # Flatten, split on '|', remove empty items, and count frequencies
    words = [item.strip() for sublist in column_data.dropna() for item in sublist.split('|') if item.strip()]
    return dict(Counter(words))

# Generate a word cloud from a frequency dictionary
def create_tag_cloud_from_frequencies(freq_dict, title, filename):
    # Generate the word cloud with full canvas utilization settings
    wordcloud = WordCloud(
        width=800, 
        height=400, 
        background_color='white', 
        collocations=False,
        max_words=200,  # Adjust as needed based on the frequency dictionary size
        scale=2,  # Increase scaling for better fit
        prefer_horizontal=0.7,  # Adjust orientation to fit more words
        margin=0  # Remove outer margin for full canvas usage
    ).generate_from_frequencies(freq_dict)
    
    # Display and save the word cloud
    plt.figure(figsize=(10, 5))
    plt.imshow(wordcloud, interpolation="bilinear")
    plt.axis('off')
    plt.title(title)
    plt.savefig(filename, bbox_inches='tight')  # bbox_inches='tight' to minimize padding in saved file
    plt.close()


# Extract frequencies for topics, subfields, fields, and domains
topics_freq = get_frequency_dict(df['topics'])
subfields_freq = get_frequency_dict(df['subfields'])
fields_freq = get_frequency_dict(df['fields'])
domains_freq = get_frequency_dict(df['domains'])

# Create and save tag clouds using frequencies
create_tag_cloud_from_frequencies(topics_freq, 'Topics Tag Cloud', 'tagclouds/topics_tag_cloud.png')
create_tag_cloud_from_frequencies(subfields_freq, 'Subfields Tag Cloud', 'tagclouds/subfields_tag_cloud.png')
create_tag_cloud_from_frequencies(fields_freq, 'Fields Tag Cloud', 'tagclouds/fields_tag_cloud.png')
create_tag_cloud_from_frequencies(domains_freq, 'Domains Tag Cloud', 'tagclouds/domains_tag_cloud.png')
