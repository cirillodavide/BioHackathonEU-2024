import pandas as pd
import matplotlib.pyplot as plt
import os

# Step 1: Read the input TSV file
df = pd.read_csv('enriched_aggregated_papers_with_topics_and_bip_scores.csv', sep='\t')  # Replace with actual input filename

# Step 2: Extract the first year if Year contains multiple years (e.g., "2022 | 2024")
df['Year'] = df['Year'].apply(lambda x: str(x).split(' |')[0])  # Take the first year if it's a range
df['Year'] = pd.to_numeric(df['Year'], errors='coerce')  # Convert to numeric and handle errors

# Step 3: For pop_class, inf_class, count values not equal to 'C5' and calculate averages per year

# Function to count occurrences where class is not 'C5' for each year
def count_not_C5(df, class_column):
    return df[df[class_column] != 'C5'].groupby('Year').size()

# Get counts of non-'C5' for pop_class and inf_class
pop_class_count = count_not_C5(df, 'pop_class')
inf_class_count = count_not_C5(df, 'inf_class')

# Create a DataFrame for these counts
count_metrics = pd.DataFrame({
    'pop_class_count': pop_class_count,
    'inf_class_count': inf_class_count
})

# Step 4: Plot the number of papers considered per year
papers_per_year = df.groupby('Year').size()

# Step 5: Create the bar chart for total papers, popular works, and influential works per year
# Combine the metrics for easy plotting
combined_metrics = pd.DataFrame({
    'Total papers': papers_per_year,
    'Popular papers': pop_class_count,
    'Influential papers': inf_class_count
})

# Plot the bar chart
plt.figure(figsize=(10, 6))  # Wider figure for better spacing
ax = combined_metrics.plot(kind='bar', width=0.8, edgecolor='black', alpha=0.7, color=['blue', 'green', 'red'], ax=plt.gca())

# Add title and labels
# plt.title('Total Papers, Popular Works, and Influential Works per Year', fontsize=14)
plt.xlabel('Publication year', fontsize=12)
plt.ylabel('Num. of papers', fontsize=12)
plt.xticks(rotation=45, ha='right', fontsize=10)
plt.yticks(fontsize=10)

# Set y-axis to start from 0
plt.ylim(0, combined_metrics.max().max() * 1.1)  # To add some space above the max value

# Add horizontal gridlines for better readability
ax.grid(True, axis='y', linestyle='--', alpha=0.5)

# Add legend with custom styling
plt.legend(title_fontsize=12, loc='upper left', fontsize=10)

# Tighten layout to avoid overlapping
plt.tight_layout()

# Save the enhanced bar chart in the 'plots' folder
output_folder = 'plots'
if not os.path.exists(output_folder):
    os.makedirs(output_folder)

plt.savefig(f'{output_folder}/total_popular_influential_works_per_year_enhanced.png')
plt.close()

print(f"Enhanced plot has been saved to the '{output_folder}' folder.")
