import pandas as pd
import matplotlib.pyplot as plt
import os

# Load the files with the correct separator for TSV
gender_df = pd.read_csv('enriched_aggregated_papers_gender_authors_llama3.2.tsv', sep='\t')
papers_df = pd.read_csv('enriched_aggregated_papers_with_topics_and_bip_scores.csv', sep='\t')

# Merge the dataframes based on author names for both first and last authors
first_author_merged = papers_df.merge(
    gender_df, left_on=['first_author_firstName', 'first_author_lastName'], 
    right_on=['first_name', 'last_name'], how='inner'
).rename(columns={'gender': 'first_author_gender'})

last_author_merged = papers_df.merge(
    gender_df, left_on=['last_author_firstName', 'last_author_lastName'], 
    right_on=['first_name', 'last_name'], how='inner'
).rename(columns={'gender': 'last_author_gender'})

# Filter for popular and influential works
popular_first_authors = first_author_merged[first_author_merged['pop_class'] != 'C5']
popular_last_authors = last_author_merged[last_author_merged['pop_class'] != 'C5']
influential_first_authors = first_author_merged[first_author_merged['inf_class'] != 'C5']
influential_last_authors = last_author_merged[last_author_merged['inf_class'] != 'C5']

# Create the output directory if it doesn't exist
os.makedirs('plots', exist_ok=True)

# Function to plot and save gender distribution by year
def plot_and_save_gender_by_year(df, gender_column, title, filename):
    # Make a copy of the dataframe to avoid modifying the original slice
    df_copy = df.copy()
    
    # Split the year by "|" and keep only the first value using .loc to avoid SettingWithCopyWarning
    df_copy.loc[:, 'Year'] = df_copy['Year'].str.split('|').str[0]

    # Count the number of papers by gender and year
    yearly_counts = df_copy.groupby(['Year', gender_column]).size().unstack(fill_value=0)
    
    # Convert the year to numeric for sorting
    yearly_counts.index = pd.to_numeric(yearly_counts.index, errors='coerce')
    yearly_counts = yearly_counts.sort_index()

    # Plotting
    plt.figure(figsize=(8, 8))  # Square plot
    yearly_counts['male'].plot(kind='line', color='green', marker='o', linewidth=2, label='Male')
    yearly_counts['female'].plot(kind='line', color='orange', marker='o', linewidth=2, label='Female')
    
    # Adding grid
    plt.grid(True, which='both', linestyle='--', linewidth=0.5)

    # Labeling
    plt.xlabel('Year')
    plt.ylabel('Number of Papers')
    plt.title(title)

    # Set the x-axis limits from 2007 to 2024 and only show labels starting from 2008
    plt.xlim(2007, 2024)
    plt.xticks(range(2007, 2025, 2))  # Show x-axis labels every 2 years from 2007
    
    # Set y-axis to start from 0
    plt.ylim(0, yearly_counts.max().max() + 5)  # Adjust the y-axis limit dynamically based on data

    # Move legend to the left
    plt.legend(loc='upper left')

    # Save the plot
    plt.savefig(f'plots/{filename}')
    plt.close()  # Close the plot to avoid display during runtime

# Generate and save each plot
plot_and_save_gender_by_year(popular_first_authors, 'first_author_gender', 'Popular Works by First Author Gender per Year', 'popular_first_author_gender_year.png')
plot_and_save_gender_by_year(popular_last_authors, 'last_author_gender', 'Popular Works by Last Author Gender per Year', 'popular_last_author_gender_year.png')
plot_and_save_gender_by_year(influential_first_authors, 'first_author_gender', 'Influential Works by First Author Gender per Year', 'influential_first_author_gender_year.png')
plot_and_save_gender_by_year(influential_last_authors, 'last_author_gender', 'Influential Works by Last Author Gender per Year', 'influential_last_author_gender_year.png')
