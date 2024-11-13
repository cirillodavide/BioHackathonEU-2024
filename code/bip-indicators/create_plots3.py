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

# Helper function to standardize gender values and classify unknowns
def clean_gender_column(df, gender_column):
    df.loc[:, gender_column] = df[gender_column].str.strip().str.lower()
    df.loc[:, gender_column] = df[gender_column].apply(lambda x: x if x in ['male', 'female'] else 'not retrieved')
    return df

# Clean gender columns for each dataset
popular_first_authors = clean_gender_column(popular_first_authors, 'first_author_gender')
popular_last_authors = clean_gender_column(popular_last_authors, 'last_author_gender')
influential_first_authors = clean_gender_column(influential_first_authors, 'first_author_gender')
influential_last_authors = clean_gender_column(influential_last_authors, 'last_author_gender')

# Calculate the percentage of each gender category for each author type
def calculate_gender_percentages(df, gender_column):
    gender_counts = df[gender_column].value_counts(normalize=True) * 100  # Get percentages
    return [gender_counts.get('male', 0), gender_counts.get('female', 0), gender_counts.get('not retrieved', 0)]

# Data for plotting
categories = ['First Author', 'Last Author', 'First Author', 'Last Author']
group_labels = ['Popular papers (top 10%)', 'Influential papers (top 10%)']
male_percentages = [
    calculate_gender_percentages(popular_first_authors, 'first_author_gender')[0],
    calculate_gender_percentages(popular_last_authors, 'last_author_gender')[0],
    calculate_gender_percentages(influential_first_authors, 'first_author_gender')[0],
    calculate_gender_percentages(influential_last_authors, 'last_author_gender')[0],
]
female_percentages = [
    calculate_gender_percentages(popular_first_authors, 'first_author_gender')[1],
    calculate_gender_percentages(popular_last_authors, 'last_author_gender')[1],
    calculate_gender_percentages(influential_first_authors, 'first_author_gender')[1],
    calculate_gender_percentages(influential_last_authors, 'last_author_gender')[1],
]
unknown_percentages = [
    calculate_gender_percentages(popular_first_authors, 'first_author_gender')[2],
    calculate_gender_percentages(popular_last_authors, 'last_author_gender')[2],
    calculate_gender_percentages(influential_first_authors, 'first_author_gender')[2],
    calculate_gender_percentages(influential_last_authors, 'last_author_gender')[2],
]

# Plotting the grouped stacked bar chart
bar_width = 0.6  # Increased bar width for better visibility
x = [0, 1, 3, 4]  # Positions for grouped bars, with gaps between groups
fig, ax = plt.subplots(figsize=(8, 8))  # Square plot

# Plot each gender stack with some transparency and an outline
ax.bar(x, male_percentages, color='green', edgecolor='black', alpha=0.8, label='Male', width=bar_width)
ax.bar(x, female_percentages, bottom=male_percentages, color='orange', edgecolor='black', alpha=0.8, label='Female', width=bar_width)
ax.bar(x, unknown_percentages, bottom=[i + j for i, j in zip(male_percentages, female_percentages)], 
       color='lightgrey', edgecolor='black', alpha=0.8, label='Not retrieved', width=bar_width)

# Adding percentages on each bar segment
for i in range(len(categories)):
    # Male percentages
    ax.text(x[i], male_percentages[i] / 2, f"{male_percentages[i]:.1f}%", ha='center', color='white', fontweight='bold')
    # Female percentages
    ax.text(x[i], male_percentages[i] + female_percentages[i] / 2, f"{female_percentages[i]:.1f}%", ha='center', color='white', fontweight='bold')
    # Not retrieved percentages
    ax.text(x[i], male_percentages[i] + female_percentages[i] + unknown_percentages[i] / 2, f"{unknown_percentages[i]:.1f}%", 
            ha='center', color='black', fontweight='bold')

# Add x-axis labels for "First Author" and "Last Author"
ax.set_xticks(x)
ax.set_xticklabels(categories)

# Group labels for "Popular papers" and "Influential works"
for idx, group_label in enumerate(group_labels):
    ax.text(x[idx * 2] + 0.5, -8, group_label, ha='center', fontsize=12, fontweight='bold', color='black')

# Labels and legend
ax.set_ylabel('Percentage (%)')
ax.set_title('Gender Distribution by Author position for Popular and Influential papers')

# Set y-axis limit to 100%
ax.set_ylim(0, 100)

# Move legend outside the plot
ax.legend(loc='lower left')

# Save the plot
plt.tight_layout()
plt.savefig('plots/grouped_stacked_gender_distribution_grouped.png', bbox_inches='tight')
plt.close()
