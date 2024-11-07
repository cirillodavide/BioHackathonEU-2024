import pandas as pd
import matplotlib.pyplot as plt
import os

# Step 1: Read the input TSV files
df_papers = pd.read_csv('enriched_aggregated_papers_with_topics_and_bip_scores.csv', sep='\t')  # Replace with actual input filename
df_gender = pd.read_csv('enriched_aggregated_papers_gender_authors_llama3.2.tsv', sep='\t')  # Replace with actual gender file

# Step 2: Check the columns in df_gender to debug the column name issue
print("Columns in df_gender:", df_gender.columns)

# Step 3: Merge the gender data with df_papers for first and last authors
df_papers = df_papers.merge(
    df_gender.rename(columns={"first_name": "first_author_firstName", "last_name": "first_author_lastName", "gender": "first_author_gender"}),
    on=["first_author_firstName", "first_author_lastName"],
    how="left"
)

df_papers = df_papers.merge(
    df_gender.rename(columns={"first_name": "last_author_firstName", "last_name": "last_author_lastName", "gender": "last_author_gender"}),
    on=["last_author_firstName", "last_author_lastName"],
    how="left"
)

# Step 4: Extract the first year if 'Year' contains multiple years (e.g., "2022 | 2024")
df_papers['Year'] = df_papers['Year'].apply(lambda x: str(x).split(' |')[0])  # Take the first year if it's a range
df_papers['Year'] = pd.to_numeric(df_papers['Year'], errors='coerce')  # Convert to numeric and handle errors

# Step 5: Group by 'Year' and calculate the average and sum for 'popularity', 'influence', 'cc', and 'impulse'
metrics = ['popularity', 'influence', 'cc', 'impulse']
yearly_avg_metrics = df_papers.groupby('Year')[metrics].mean()
yearly_sum_metrics = df_papers.groupby('Year')[metrics].sum()

# Step 6: Create output folder 'plots' if it doesn't exist
output_folder = 'plots'
if not os.path.exists(output_folder):
    os.makedirs(output_folder)

# Step 7: Plot the average results for each metric and save the figures
# Step 7: Plot the average results for each metric and save the figures
for metric in metrics:
    # First Author Average Plot
    plt.figure(figsize=(6, 6))  # Square figure
    # Filter male/female/unknown data for first author
    male_data_first_avg = df_papers[df_papers['first_author_gender'] == 'male'].groupby('Year')[metric].mean()
    female_data_first_avg = df_papers[df_papers['first_author_gender'] == 'female'].groupby('Year')[metric].mean()
    unknown_data_first_avg = df_papers[df_papers['first_author_gender'].isna()].groupby('Year')[metric].mean()

    # Ensure all years are represented, fill missing years with zero values
    all_years = range(2007, 2025)  # Assuming years range from 2007 to 2024
    male_data_first_avg = male_data_first_avg.reindex(all_years, fill_value=0).fillna(0)
    female_data_first_avg = female_data_first_avg.reindex(all_years, fill_value=0).fillna(0)
    unknown_data_first_avg = unknown_data_first_avg.reindex(all_years, fill_value=0).fillna(0)  # Ensure "Not Retrieved" has all years

    # Find the max value for y-axis to ensure same scale for first and last author plots
    y_max_avg = max(male_data_first_avg.max(), female_data_first_avg.max(), unknown_data_first_avg.max())

    # Plot male, female, and unknown first authors
    plt.plot(male_data_first_avg.index, male_data_first_avg, marker='o', linestyle='-', color='green', alpha=0.7, label='Male')
    plt.plot(female_data_first_avg.index, female_data_first_avg, marker='o', linestyle='-', color='orange', alpha=0.7, label='Female')
    plt.plot(unknown_data_first_avg.index, unknown_data_first_avg, marker='o', linestyle='-', color='lightgrey', alpha=0.7, label='Not Retrieved')
    
    plt.title(f'{metric.capitalize()} per Year (Average) - First Author', fontsize=14)
    plt.xlabel('Year', fontsize=12)
    plt.ylabel(f'Average {metric.capitalize()}', fontsize=12)
    plt.xlim(2007, 2024)  # Set x-axis from 2007 to 2024
    plt.ylim(0, y_max_avg * 1.1)  # Set y-axis with the same max value for consistency
    plt.legend(loc='upper left', fontsize=10, title='Gender')  # Move legend to upper left corner
    plt.grid(True, linestyle='--', alpha=0.5)
    plt.tight_layout()

    avg_folder = os.path.join(output_folder, 'avg')
    if not os.path.exists(avg_folder):
        os.makedirs(avg_folder)
    plt.savefig(f'{avg_folder}/{metric}_first_author_avg.png')
    plt.close()

    # Last Author Average Plot
    plt.figure(figsize=(6, 6))  # Square figure
    male_data_last_avg = df_papers[df_papers['last_author_gender'] == 'male'].groupby('Year')[metric].mean()
    female_data_last_avg = df_papers[df_papers['last_author_gender'] == 'female'].groupby('Year')[metric].mean()
    unknown_data_last_avg = df_papers[df_papers['last_author_gender'].isna()].groupby('Year')[metric].mean()

    # Ensure all years are represented, fill missing years with zero values
    male_data_last_avg = male_data_last_avg.reindex(all_years, fill_value=0).fillna(0)
    female_data_last_avg = female_data_last_avg.reindex(all_years, fill_value=0).fillna(0)
    unknown_data_last_avg = unknown_data_last_avg.reindex(all_years, fill_value=0).fillna(0)  # Ensure "Not Retrieved" has all years

    # Plot male, female, and unknown last authors
    plt.plot(male_data_last_avg.index, male_data_last_avg, marker='o', linestyle='-', color='green', alpha=0.7, label='Male')
    plt.plot(female_data_last_avg.index, female_data_last_avg, marker='o', linestyle='-', color='orange', alpha=0.7, label='Female')
    plt.plot(unknown_data_last_avg.index, unknown_data_last_avg, marker='o', linestyle='-', color='lightgrey', alpha=0.7, label='Not Retrieved')

    plt.title(f'{metric.capitalize()} per Year (Average) - Last Author', fontsize=14)
    plt.xlabel('Year', fontsize=12)
    plt.ylabel(f'Average {metric.capitalize()}', fontsize=12)
    plt.xlim(2007, 2024)  # Set x-axis from 2007 to 2024
    plt.ylim(0, y_max_avg * 1.1)  # Set y-axis with the same max value for consistency
    plt.legend(loc='upper left', fontsize=10, title='Gender')  # Move legend to upper left corner
    plt.grid(True, linestyle='--', alpha=0.5)
    plt.tight_layout()

    plt.savefig(f'{avg_folder}/{metric}_last_author_avg.png')
    plt.close()

# Step 8: Plot the sum results for each metric and save the figures
for metric in metrics:
    # First Author Sum Plot
    plt.figure(figsize=(6, 6))  # Square figure
    male_data_first_sum = df_papers[df_papers['first_author_gender'] == 'male'].groupby('Year')[metric].sum()
    female_data_first_sum = df_papers[df_papers['first_author_gender'] == 'female'].groupby('Year')[metric].sum()
    unknown_data_first_sum = df_papers[df_papers['first_author_gender'].isna()].groupby('Year')[metric].sum()

    # Ensure all years are represented, fill missing years with zero values
    male_data_first_sum = male_data_first_sum.reindex(all_years, fill_value=0)
    female_data_first_sum = female_data_first_sum.reindex(all_years, fill_value=0)
    unknown_data_first_sum = unknown_data_first_sum.reindex(all_years, fill_value=0)  # Ensure "Not Retrieved" has all years

    # Find the max value for y-axis to ensure same scale for first and last author plots
    y_max_sum = max(male_data_first_sum.max(), female_data_first_sum.max(), unknown_data_first_sum.max())

    # Plot male, female, and unknown first authors
    plt.plot(male_data_first_sum.index, male_data_first_sum, marker='o', linestyle='-', color='green', alpha=0.7, label='Male')
    plt.plot(female_data_first_sum.index, female_data_first_sum, marker='o', linestyle='-', color='orange', alpha=0.7, label='Female')
    plt.plot(unknown_data_first_sum.index, unknown_data_first_sum, marker='o', linestyle='-', color='lightgrey', alpha=0.7, label='Not Retrieved')

    plt.title(f'{metric.capitalize()} per Year (Sum) - First Author', fontsize=14)
    plt.xlabel('Year', fontsize=12)
    plt.ylabel(f'Sum {metric.capitalize()}', fontsize=12)
    plt.xlim(2007, 2024)  # Set x-axis from 2007 to 2024
    plt.ylim(0, y_max_sum * 1.1)  # Set y-axis with the same max value for consistency
    plt.legend(loc='upper left', fontsize=10, title='Gender')  # Move legend to upper left corner
    plt.grid(True, linestyle='--', alpha=0.5)
    plt.tight_layout()

    sum_folder = os.path.join(output_folder, 'sum')
    if not os.path.exists(sum_folder):
        os.makedirs(sum_folder)
    plt.savefig(f'{sum_folder}/{metric}_first_author_sum.png')
    plt.close()

    # Last Author Sum Plot
    plt.figure(figsize=(6, 6))  # Square figure
    male_data_last_sum = df_papers[df_papers['last_author_gender'] == 'male'].groupby('Year')[metric].sum()
    female_data_last_sum = df_papers[df_papers['last_author_gender'] == 'female'].groupby('Year')[metric].sum()
    unknown_data_last_sum = df_papers[df_papers['last_author_gender'].isna()].groupby('Year')[metric].sum()

    # Ensure all years are represented, fill missing years with zero values
    male_data_last_sum = male_data_last_sum.reindex(all_years, fill_value=0).fillna(0)
    female_data_last_sum = female_data_last_sum.reindex(all_years, fill_value=0).fillna(0)
    unknown_data_last_sum = unknown_data_last_sum.reindex(all_years, fill_value=0).fillna(0)  # Ensure "Not Retrieved" has all years

    # Plot male, female, and unknown last authors
    plt.plot(male_data_last_sum.index, male_data_last_sum, marker='o', linestyle='-', color='green', alpha=0.7, label='Male')
    plt.plot(female_data_last_sum.index, female_data_last_sum, marker='o', linestyle='-', color='orange', alpha=0.7, label='Female')
    plt.plot(unknown_data_last_sum.index, unknown_data_last_sum, marker='o', linestyle='-', color='lightgrey', alpha=0.7, label='Not Retrieved')

    plt.title(f'{metric.capitalize()} per Year (Sum) - Last Author', fontsize=14)
    plt.xlabel('Year', fontsize=12)
    plt.ylabel(f'Sum {metric.capitalize()}', fontsize=12)
    plt.xlim(2007, 2024)  # Set x-axis from 2007 to 2024
    plt.ylim(0, y_max_sum * 1.1)  # Set y-axis with the same max value for consistency
    plt.legend(loc='upper left', fontsize=10, title='Gender')  # Move legend to upper left corner
    plt.grid(True, linestyle='--', alpha=0.5)
    plt.tight_layout()

    plt.savefig(f'{sum_folder}/{metric}_last_author_sum.png')
    plt.close()


# Step 9: Plot the counts for male, female, and not retrieved authors combined into one plot for both first and last authors
for gender in ['male', 'female']:
    # Get the gender-specific counts for first and last authors
    gender_data_first = df_papers[df_papers['first_author_gender'] == gender].groupby('Year').size()
    gender_data_last = df_papers[df_papers['last_author_gender'] == gender].groupby('Year').size()

    # Ensure all years are represented, fill missing years with zero values
    gender_data_first = gender_data_first.reindex(all_years, fill_value=0).fillna(0)
    gender_data_last = gender_data_last.reindex(all_years, fill_value=0).fillna(0)

    # First Author Gender Count Plot (combining male, female, and not retrieved)
    plt.figure(figsize=(6, 6))  # Square figure
    male_count_first = df_papers[df_papers['first_author_gender'] == 'male'].groupby('Year').size()
    female_count_first = df_papers[df_papers['first_author_gender'] == 'female'].groupby('Year').size()
    unknown_count_first = df_papers[df_papers['first_author_gender'].isna()].groupby('Year').size()
    
    # Ensure all years are represented for male, female, and unknown counts, fill missing years with zero values
    male_count_first = male_count_first.reindex(all_years, fill_value=0).fillna(0)
    female_count_first = female_count_first.reindex(all_years, fill_value=0).fillna(0)
    unknown_count_first = unknown_count_first.reindex(all_years, fill_value=0).fillna(0)

    # Plot combined male, female, and unknown counts for first authors
    plt.plot(male_count_first.index, male_count_first, marker='o', linestyle='-', color='green', alpha=0.7, label='Male')
    plt.plot(female_count_first.index, female_count_first, marker='o', linestyle='-', color='orange', alpha=0.7, label='Female')
    plt.plot(unknown_count_first.index, unknown_count_first, marker='o', linestyle='-', color='lightgrey', alpha=0.7, label='Not Retrieved')

    plt.title('Authors Count per Year - First Author', fontsize=14)
    plt.xlabel('Year', fontsize=12)
    plt.ylabel('Count', fontsize=12)
    plt.xlim(2007, 2024)  # Set x-axis from 2007 to 2024
    plt.legend(loc='upper left', fontsize=10)  # Move legend to the upper left corner
    plt.grid(True, linestyle='--', alpha=0.5)
    plt.tight_layout()

    # Save the plot
    plt.savefig(f'{output_folder}/gender_count_first_author_combined.png')
    plt.close()

    # Last Author Gender Count Plot (combining male, female, and not retrieved)
    plt.figure(figsize=(6, 6))  # Square figure
    male_count_last = df_papers[df_papers['last_author_gender'] == 'male'].groupby('Year').size()
    female_count_last = df_papers[df_papers['last_author_gender'] == 'female'].groupby('Year').size()
    unknown_count_last = df_papers[df_papers['last_author_gender'].isna()].groupby('Year').size()

    # Ensure all years are represented for male, female, and unknown counts, fill missing years with zero values
    male_count_last = male_count_last.reindex(all_years, fill_value=0).fillna(0)
    female_count_last = female_count_last.reindex(all_years, fill_value=0).fillna(0)
    unknown_count_last = unknown_count_last.reindex(all_years, fill_value=0).fillna(0)

    # Plot combined male, female, and unknown counts for last authors
    plt.plot(male_count_last.index, male_count_last, marker='o', linestyle='-', color='green', alpha=0.7, label='Male')
    plt.plot(female_count_last.index, female_count_last, marker='o', linestyle='-', color='orange', alpha=0.7, label='Female')
    plt.plot(unknown_count_last.index, unknown_count_last, marker='o', linestyle='-', color='lightgrey', alpha=0.7, label='Not Retrieved')

    plt.title('Authors Count per Year - Last Author', fontsize=14)
    plt.xlabel('Year', fontsize=12)
    plt.ylabel('Count', fontsize=12)
    plt.xlim(2007, 2024)  # Set x-axis from 2007 to 2024
    plt.legend(loc='upper left', fontsize=10)  # Move legend to the upper left corner
    plt.grid(True, linestyle='--', alpha=0.5)
    plt.tight_layout()

    # Save the plot
    plt.savefig(f'{output_folder}/gender_count_last_author_combined.png')
    plt.close()

print("All combined gender count plots have been successfully saved.")
