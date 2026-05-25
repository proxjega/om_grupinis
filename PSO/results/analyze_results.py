import pandas as pd
import glob
import os
from pathlib import Path

csv_files = sorted(glob.glob("GNBG_III_Detailed_Results_*.csv"))

all_results = []

for csv_file in csv_files:
    print(f"\n{'='*80}")
    print(f"File: {csv_file}")
    print(f"{'='*80}\n")
    
    df = pd.read_csv(csv_file)
    
    success_cols = [col for col in df.columns if 'Success' in col]
    
    problem_stats = []
    for problem in sorted(df['Problem'].unique(), key=lambda x: int(x[1:])):
        problem_data = df[df['Problem'] == problem]
        
        success_ones = 0
        for col in success_cols:
            success_ones += (problem_data[col] == 1).sum()
        
        min_error = problem_data['Error_500K'].min()
        max_error = problem_data['Error_500K'].max()
        mean_error = problem_data['Error_500K'].mean()
        
        problem_stats.append({
            'Problem': problem,
            'Min_Error_500K': min_error,
            'Max_Error_500K': max_error,
            'Mean_Error_500K': mean_error,
            'Success_Count': success_ones
        })
    
    result_df = pd.DataFrame(problem_stats).set_index('Problem')
    
    print("Statistics by Problem:")
    print("-" * 80)
    print(result_df.to_string())
    print()
    
    avg_mean_error = result_df['Mean_Error_500K'].mean()
    total_success = result_df['Success_Count'].sum()
    
    all_results.append({
        'File': csv_file,
        'Avg_Mean_Error_500K': avg_mean_error,
        'Total_Success_Count': total_success
    })

print("\n" + "="*80)
print("RANKING SUMMARY (Rank-Based Comparison)")
print("="*80 + "\n")

ranking_df = pd.DataFrame(all_results)

file_ranks = {}
problems = []

for result in all_results:
    for stat in problem_stats if 'problem_stats' in locals() else []:
        if stat['Problem'] not in problems:
            problems.append(stat['Problem'])

for result in all_results:
    file_ranks[result['File']] = {'error_ranks': [], 'success_ranks': []}

print("Detailed Rankings by Problem:")
print("-" * 80)

problem_results = {}

for csv_file in csv_files:
    df = pd.read_csv(csv_file)
    success_cols = [col for col in df.columns if 'Success' in col]
    
    for problem in sorted(df['Problem'].unique(), key=lambda x: int(x[1:])):
        problem_data = df[df['Problem'] == problem]
        
        success_ones = sum((problem_data[col] == 1).sum() for col in success_cols)
        mean_error = problem_data['Error_500K'].mean()
        
        if problem not in problem_results:
            problem_results[problem] = []
        
        problem_results[problem].append({
            'File': csv_file,
            'Mean_Error': mean_error,
            'Success_Count': success_ones
        })

for problem in sorted(problem_results.keys(), key=lambda x: int(x[1:])):
    problem_df = pd.DataFrame(problem_results[problem])
    
    problem_df['Error_Rank'] = problem_df['Mean_Error'].rank()
    problem_df['Success_Rank'] = problem_df['Success_Count'].rank(ascending=False)
    
    problem_df['Combined_Rank'] = (problem_df['Error_Rank'] + problem_df['Success_Rank']) / 2
    problem_df_sorted = problem_df.sort_values('Combined_Rank')
    
    print(f"\n{problem}:")
    print(problem_df_sorted[['File', 'Mean_Error', 'Success_Count', 'Error_Rank', 'Success_Rank']].to_string(index=False))
    
    for idx, row in problem_df_sorted.iterrows():
        if row['File'] not in file_ranks:
            file_ranks[row['File']] = {'error_ranks': [], 'success_ranks': []}
        file_ranks[row['File']]['error_ranks'].append(row['Error_Rank'])
        file_ranks[row['File']]['success_ranks'].append(row['Success_Rank'])

print("\n" + "="*80)
print("Overall Ranking (Average Ranks):")
print("-" * 80)

overall_ranks = []
for file, ranks in file_ranks.items():
    avg_error_rank = sum(ranks['error_ranks']) / len(ranks['error_ranks']) if ranks['error_ranks'] else 0
    avg_success_rank = sum(ranks['success_ranks']) / len(ranks['success_ranks']) if ranks['success_ranks'] else 0
    combined_rank = (avg_error_rank + avg_success_rank) / 2
    
    overall_ranks.append({
        'File': file,
        'Avg_Error_Rank': avg_error_rank,
        'Avg_Success_Rank': avg_success_rank,
        'Combined_Rank': combined_rank
    })

overall_df = pd.DataFrame(overall_ranks).sort_values('Combined_Rank')
overall_df['Rank'] = range(1, len(overall_df) + 1)

display_cols = ['Rank', 'File', 'Combined_Rank', 'Avg_Error_Rank', 'Avg_Success_Rank']
print(overall_df[display_cols].to_string(index=False))
print()
