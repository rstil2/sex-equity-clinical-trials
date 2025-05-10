import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np

# Set style for publication-quality figures
plt.style.use('seaborn-v0_8')
plt.rcParams['figure.dpi'] = 300
plt.rcParams['savefig.dpi'] = 300

# Load the processed data
try:
    df = pd.read_csv('data/processed_clinical_trials.csv')
except FileNotFoundError:
    # Try alternative path if data directory is not found
    df = pd.read_csv('processed_clinical_trials.csv')

print(f"Successfully loaded data with {len(df)} trials")

# Figure 1: Distribution of clinical trials by sex representation
plt.figure(figsize=(10, 6))
sex_counts = df['Sex_Category'].value_counts()
sns.barplot(x=sex_counts.index, y=sex_counts.values)
plt.title('Distribution of Clinical Trials by Sex Representation')
plt.xlabel('Sex Category')
plt.ylabel('Number of Trials')
plt.xticks(rotation=45)
plt.tight_layout()
plt.savefig('figures/figure1_sex_distribution.png')
print("Figure 1 saved: Distribution of Clinical Trials by Sex Representation")
plt.close()

# Figure 2: Female inclusion rates across disease categories
disease_inclusion = df.groupby('Disease_Category').apply(
    lambda x: ((x['Sex_Category'] == 'Female Only') | 
               (x['Sex_Category'] == 'Both Sexes')).mean() * 100
).sort_values(ascending=True)

plt.figure(figsize=(12, 6))
sns.barplot(x=disease_inclusion.values, y=disease_inclusion.index)
plt.title('Female Inclusion Rates Across Disease Categories')
plt.xlabel('Female Inclusion Rate (%)')
plt.ylabel('Disease Category')
plt.axvline(x=90, color='red', linestyle='--', alpha=0.5)  # Reference line at 90%
plt.tight_layout()
plt.savefig('figures/figure2_inclusion_rates.png')
print("Figure 2 saved: Female Inclusion Rates Across Disease Categories")
plt.close()

# Figure 3: Distribution of sex representation by disease type
plt.figure(figsize=(15, 8))
disease_sex_dist = pd.crosstab(df['Disease_Category'], df['Sex_Category'], normalize='index') * 100
disease_sex_dist.plot(kind='bar', stacked=True)
plt.title('Distribution of Sex Representation by Disease Type')
plt.xlabel('Disease Category')
plt.ylabel('Percentage of Trials')
plt.legend(title='Sex Category', bbox_to_anchor=(1.05, 1), loc='upper left')
plt.tight_layout()
plt.savefig('figures/figure3_disease_distribution.png')
print("Figure 3 saved: Distribution of Sex Representation by Disease Type")
plt.close()

print("All figures generated successfully!")

