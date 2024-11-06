import pandas as pd
import matplotlib.pyplot as plt
import os

# Step 1: Read the input TSV file
df = pd.read_csv('enriched_aggregated_papers_with_topics_and_bip_scores.csv', sep='\t')  # Replace with actual input filename

# Step 2: Extract the first year if 'Year' contains multiple years (e.g., "2022 | 2024")
df['Year'] = df['Year'].apply(lambda x: str(x).split(' |')[0])  # Take the first year if it's a range
df['Year'] = pd.to_numeric(df['Year'], errors='coerce')  # Convert to numeric and handle errors

# Step 3: Group by 'Year' and calculate the average and sum for 'popularity', 'influence', 'cc', and 'impulse'
metrics = ['popularity', 'influence', 'cc', 'impulse']
yearly_avg_metrics = df.groupby('Year')[metrics].mean()
yearly_sum_metrics = df.groupby('Year')[metrics].sum()

# Step 4: Create output folder 'plots' if it doesn't exist
output_folder = 'plots'
if not os.path.exists(output_folder):
    os.makedirs(output_folder)

# Step 5: Plot the average results for each metric and save the figures
for metric in metrics:
    plt.figure(figsize=(6, 6))  # Square figure
    plt.plot(yearly_avg_metrics.index, yearly_avg_metrics[metric], marker='o', linestyle='-', color='green', alpha=0.7)
    plt.title(f'{metric.capitalize()} per Year (Average)', fontsize=14)
    plt.xlabel('Year', fontsize=12)
    plt.ylabel(f'Average {metric.capitalize()}', fontsize=12)
    
    # Set x-axis limits from min to max year and y-axis to start from 0
    plt.xlim(yearly_avg_metrics.index.min(), yearly_avg_metrics.index.max())
    plt.ylim(0, yearly_avg_metrics[metric].max() * 1.1)  # To add some space above the max value

    plt.grid(True, linestyle='--', alpha=0.5)
    plt.tight_layout()
    # Save the plot in the 'plots' folder
    plt.savefig(f'{output_folder}/{metric}_per_year_avg.png')
    plt.close()

# Step 6: Plot the sum results for each metric and save the figures
for metric in metrics:
    plt.figure(figsize=(6, 6))  # Square figure
    plt.plot(yearly_sum_metrics.index, yearly_sum_metrics[metric], marker='o', linestyle='-', color='blue', alpha=0.7)
    plt.title(f'{metric.capitalize()} per Year (Sum)', fontsize=14)
    plt.xlabel('Year', fontsize=12)
    plt.ylabel(f'Sum {metric.capitalize()}', fontsize=12)
    
    # Set x-axis limits from min to max year and y-axis to start from 0
    plt.xlim(yearly_sum_metrics.index.min(), yearly_sum_metrics.index.max())
    plt.ylim(0, yearly_sum_metrics[metric].max() * 1.1)  # To add some space above the max value

    plt.grid(True, linestyle='--', alpha=0.5)
    plt.tight_layout()
    # Save the plot in the 'plots' folder
    plt.savefig(f'{output_folder}/{metric}_per_year_sum.png')
    plt.close()

# Step 7: For pop_class, inf_class, count values not equal to 'C5' and calculate counts per year
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

# Step 8: Plot the number of papers considered per year
papers_per_year = df.groupby('Year').size()

# Step 9: Create the bar chart for total papers, popular works, and influential works per year
# Combine the metrics for easy plotting
combined_metrics = pd.DataFrame({
    'Total papers': papers_per_year,
    'Popular papers': pop_class_count,
    'Influential papers': inf_class_count
})

# Plot the enhanced bar chart
plt.figure(figsize=(10, 6))  # Wider figure for better spacing
ax = combined_metrics.plot(kind='bar', width=0.8, edgecolor='black', alpha=0.7, color=['blue', 'green', 'red'], ax=plt.gca())

# Add title and labels
plt.title('Total Papers, Popular Works, and Influential Works per Year', fontsize=14)
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
plt.savefig(f'{output_folder}/total_popular_influential_works_per_year_enhanced.png')
plt.close()

print(f"All plots have been saved to the '{output_folder}' folder.")
