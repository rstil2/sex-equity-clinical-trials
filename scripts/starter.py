import pandas as pd
import numpy as np
import requests
import time
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import classification_report, confusion_matrix
import re
import statsmodels.api as sm
import statsmodels.formula.api as smf
from scipy.stats import chi2_contingency

# Set plotting style
sns.set(font_scale=1.2)
sns.set_style("whitegrid")

# --------------------------
# DATA LOADING AND CLEANING
# --------------------------

print("Loading and cleaning data...")
# Load your dataset
df = pd.read_csv("merged_clinical_indicators_2025-05-01.csv")

# Check for duplicate entries
print(f"Original row count: {df.shape[0]}")
df = df.drop_duplicates(subset=["NCT Number_trial"])
print(f"After removing duplicates: {df.shape[0]}")

# Basic data cleaning
def clean_data(df):
    # Convert column types appropriately
    # Make a copy to avoid warnings
    clean_df = df.copy()
    
    # Handle missing values
    # For categorical columns, fill with 'Unknown'
    for col in ['Sex', 'Phases', 'Country']:
        if col in clean_df.columns:
            clean_df[col] = clean_df[col].fillna('Unknown')
    
    # Filter out rows with no country or GII data if needed for analysis
    clean_df = clean_df[clean_df['Country'].notna()]
    clean_df = clean_df[clean_df['Gender Inequality Index'].notna()]
    
    # Convert GII to numeric, coercing errors to NaN
    if 'Gender Inequality Index' in clean_df.columns:
        clean_df['Gender Inequality Index'] = pd.to_numeric(clean_df['Gender Inequality Index'], errors='coerce')
    
    # For phases, standardize format
    if 'Phases' in clean_df.columns:
        # Extract phase number if present (Phase 1, Phase I, etc.)
        def standardize_phase(phase_text):
            if pd.isna(phase_text) or phase_text == 'Unknown':
                return 'Unknown'
            
            phase_text = str(phase_text).upper()
            if 'PHASE 1' in phase_text or 'PHASE I' in phase_text:
                return 'Phase 1'
            elif 'PHASE 2' in phase_text or 'PHASE II' in phase_text:
                return 'Phase 2'
            elif 'PHASE 3' in phase_text or 'PHASE III' in phase_text:
                return 'Phase 3'
            elif 'PHASE 4' in phase_text or 'PHASE IV' in phase_text:
                return 'Phase 4'
            elif 'EARLY' in phase_text:
                return 'Early Phase'
            elif 'NOT APPLICABLE' in phase_text:
                return 'Not Applicable'
            else:
                return 'Other'
        
        clean_df['Standardized_Phase'] = clean_df['Phases'].apply(standardize_phase)
    
    return clean_df

# Apply cleaning function
df_clean = clean_data(df)

# -------------------------------
# TRIAL CATEGORIZATION BY SEX
# -------------------------------

print("Categorizing trials by sex representation...")
def categorize_by_sex(sex_value):
    if pd.isna(sex_value) or sex_value == 'Unknown':
        return 'Unknown'
    
    sex_value = str(sex_value).upper()
    if sex_value == 'FEMALE' or sex_value == 'F':
        return 'Female Only'
    elif sex_value == 'MALE' or sex_value == 'M':
        return 'Male Only'
    elif 'FEMALE' in sex_value and 'MALE' in sex_value:
        return 'Both Sexes'
    elif 'ALL' in sex_value:
        return 'Both Sexes'
    else:
        return 'Unknown'

df_clean['Sex_Category'] = df_clean['Sex'].apply(categorize_by_sex)

# ----------------------------
# DISEASE TYPE CATEGORIZATION
# ----------------------------

print("Categorizing trials by disease type...")
def categorize_disease(conditions):
    if pd.isna(conditions):
        return 'Unknown'
    
    conditions = str(conditions).upper()
    
    # Define categories with associated keywords
    disease_categories = {
        'COVID-19': ['COVID', 'SARS-COV-2', 'CORONAVIRUS', 'CORONA VIRUS'],
        'HIV/AIDS': ['HIV', 'AIDS', 'HUMAN IMMUNODEFICIENCY VIRUS'],
        'Cancer': ['CANCER', 'TUMOR', 'NEOPLASM', 'CARCINOMA', 'LEUKEMIA', 'LYMPHOMA', 'ONCOLOGY'],
        'Cardiovascular': ['HEART', 'CARDIAC', 'CARDIOVASCULAR', 'STROKE', 'HYPERTENSION'],
        'Diabetes': ['DIABETES', 'DIABETIC'],
        'Mental Health': ['PSYCHIATRIC', 'DEPRESSION', 'ANXIETY', 'SCHIZOPHRENIA', 'BIPOLAR', 'MENTAL'],
        'Respiratory': ['ASTHMA', 'COPD', 'LUNG', 'PULMONARY', 'RESPIRATORY'],
        'Infectious Disease': ['INFECTION', 'INFECTIOUS', 'BACTERIAL', 'VIRAL', 'FUNGAL', 'MALARIA', 'TUBERCULOSIS']
    }
    
    # Check if conditions contain any keywords for each category
    for category, keywords in disease_categories.items():
        if any(keyword in conditions for keyword in keywords):
            return category
    
    return 'Other'

df_clean['Disease_Category'] = df_clean['Conditions'].apply(categorize_disease)

# ------------------------
# GII CATEGORIZATION
# ------------------------

print("Categorizing countries by GII level...")
# Create GII categories (low, medium, high) based on percentiles
if 'Gender Inequality Index' in df_clean.columns:
    # Only consider rows with valid GII values
    gii_data = df_clean['Gender Inequality Index'].dropna()
    
    # Create quantile-based categories
    low_threshold = gii_data.quantile(0.33)
    high_threshold = gii_data.quantile(0.67)
    
    def categorize_gii(gii_value):
        if pd.isna(gii_value):
            return 'Unknown'
        elif gii_value <= low_threshold:
            return 'Low GII'
        elif gii_value <= high_threshold:
            return 'Medium GII'
        else:
            return 'High GII'
    
    df_clean['GII_Category'] = df_clean['Gender Inequality Index'].apply(categorize_gii)

# ----------------------------------
# DEFINE FUNCTION TO FETCH ELIGIBILITY
# ----------------------------------

def fetch_eligibility(nct_id):
    url = f"https://clinicaltrials.gov/api/query/full_studies?expr={nct_id}&min_rnk=1&max_rnk=1&fmt=json"
    try:
        response = requests.get(url)
        data = response.json()
        eligibility = data["FullStudiesResponse"]["FullStudies"][0]["Study"]["ProtocolSection"]["EligibilityModule"].get("EligibilityCriteria", "")
        return eligibility
    except Exception as e:
        print(f"Error fetching data for {nct_id}: {e}")
        return ""

# ----------------------------------------
# EXPLORATORY ANALYSIS AND VISUALIZATION
# ----------------------------------------

print("Performing exploratory analysis...")

def run_exploratory_analysis(df):
    # Create output directory for figures
    import os
    if not os.path.exists('figures'):
        os.makedirs('figures')
    
    # Store detailed statistics for manuscript
    detailed_stats = {}
    
    try:
        # 1. Overall distribution of sex categories
        plt.figure(figsize=(10, 6))
        sex_counts = df['Sex_Category'].value_counts()
        sex_counts.plot(kind='bar', color='skyblue')
        plt.title('Distribution of Trials by Sex Category')
        plt.ylabel('Number of Trials')
        plt.xlabel('Sex Category')
        plt.tight_layout()
        plt.savefig('figures/sex_distribution.png')
        
        # Save detailed sex category distribution
        detailed_stats['sex_distribution'] = sex_counts.to_dict()
        detailed_stats['sex_percentages'] = (sex_counts / sex_counts.sum() * 100).round(1).to_dict()
        
        print("\n--- Sex Distribution Details ---")
        for category, count in sex_counts.items():
            percentage = (count / len(df) * 100).round(1)
            print(f"{category}: {count} trials ({percentage}%)")
    except Exception as e:
        print(f"Error generating sex distribution plot: {e}")
    
    try:
        # 2. Distribution of sex categories by disease type
        plt.figure(figsize=(14, 8))
        sex_disease = pd.crosstab(df['Disease_Category'], df['Sex_Category'])
        sex_disease_pct = sex_disease.div(sex_disease.sum(axis=1), axis=0) * 100
        sex_disease_pct.plot(kind='bar', stacked=True, colormap='viridis')
        plt.title('Distribution of Sex Categories by Disease Type')
        plt.ylabel('Percentage of Trials')
        plt.xlabel('Disease Category')
        plt.legend(title='Sex Category')
        plt.tight_layout()
        plt.savefig('figures/sex_by_disease.png')
        
        # Save detailed disease-sex cross-tabulation
        detailed_stats['disease_sex_counts'] = sex_disease.to_dict()
        detailed_stats['disease_sex_percentages'] = sex_disease_pct.round(1).to_dict()
        
        print("\n--- Disease Type by Sex Category (counts) ---")
        print(sex_disease)
        
        print("\n--- Disease Type by Sex Category (percentages) ---")
        print(sex_disease_pct.round(1))
        
        # Calculate female inclusion rate by disease
        female_inclusion_by_disease = {}
        for disease in sex_disease.index:
            total_trials = sex_disease.loc[disease].sum()
            female_trials = 0
            if 'Female Only' in sex_disease.columns:
                female_trials += sex_disease.loc[disease, 'Female Only']
            if 'Both Sexes' in sex_disease.columns:
                female_trials += sex_disease.loc[disease, 'Both Sexes']
            
            rate = (female_trials / total_trials * 100).round(1) if total_trials > 0 else 0
            female_inclusion_by_disease[disease] = rate
        
        detailed_stats['female_inclusion_by_disease'] = female_inclusion_by_disease
        
        print("\n--- Female Inclusion Rate by Disease (%) ---")
        for disease, rate in female_inclusion_by_disease.items():
            print(f"{disease}: {rate}%")
    except Exception as e:
        print(f"Error generating disease distribution plot: {e}")
    
    try:
        # 3. Distribution of sex categories by trial phase
        if 'Standardized_Phase' in df.columns:
            plt.figure(figsize=(12, 7))
            phase_sex = pd.crosstab(df['Standardized_Phase'], df['Sex_Category'])
            phase_sex_pct = phase_sex.div(phase_sex.sum(axis=1), axis=0) * 100
            phase_sex_pct.plot(kind='bar', stacked=True, colormap='plasma')
            plt.title('Distribution of Sex Categories by Trial Phase')
            plt.ylabel('Percentage of Trials')
            plt.xlabel('Trial Phase')
            plt.legend(title='Sex Category')
            plt.tight_layout()
            plt.savefig('figures/sex_by_phase.png')
            
            # Save detailed phase-sex cross-tabulation
            detailed_stats['phase_sex_counts'] = phase_sex.to_dict()
            detailed_stats['phase_sex_percentages'] = phase_sex_pct.round(1).to_dict()
            
            print("\n--- Trial Phase by Sex Category (counts) ---")
            print(phase_sex)
            
            print("\n--- Trial Phase by Sex Category (percentages) ---")
            print(phase_sex_pct.round(1))
            
            # Calculate female inclusion rate by phase
            female_inclusion_by_phase = {}
            for phase in phase_sex.index:
                total_trials = phase_sex.loc[phase].sum()
                female_trials = 0
                if 'Female Only' in phase_sex.columns:
                    female_trials += phase_sex.loc[phase, 'Female Only']
                if 'Both Sexes' in phase_sex.columns:
                    female_trials += phase_sex.loc[phase, 'Both Sexes']
                
                rate = (female_trials / total_trials * 100).round(1) if total_trials > 0 else 0
                female_inclusion_by_phase[phase] = rate
            
            detailed_stats['female_inclusion_by_phase'] = female_inclusion_by_phase
            
            print("\n--- Female Inclusion Rate by Trial Phase (%) ---")
            for phase, rate in female_inclusion_by_phase.items():
                print(f"{phase}: {rate}%")
    except Exception as e:
        print(f"Error generating phase distribution plot: {e}")
    
    try:
        # 4. Relationship between GII and sex categories
        if 'GII_Category' in df.columns:
            # Check if there's more than one GII category
            if df['GII_Category'].nunique() > 1:
                plt.figure(figsize=(12, 7))
                gii_sex = pd.crosstab(df['GII_Category'], df['Sex_Category'])
                gii_sex_pct = gii_sex.div(gii_sex.sum(axis=1), axis=0) * 100
                gii_sex_pct.plot(kind='bar', stacked=True, colormap='cividis')
                plt.title('Distribution of Sex Categories by GII Level')
                plt.ylabel('Percentage of Trials')
                plt.xlabel('GII Category')
                plt.legend(title='Sex Category')
                plt.tight_layout()
                plt.savefig('figures/sex_by_gii.png')
                
                # Save detailed GII-sex cross-tabulation
                detailed_stats['gii_sex_counts'] = gii_sex.to_dict()
                detailed_stats['gii_sex_percentages'] = gii_sex_pct.round(1).to_dict()
                
                print("\n--- GII Category by Sex Category (counts) ---")
                print(gii_sex)
                
                print("\n--- GII Category by Sex Category (percentages) ---")
                print(gii_sex_pct.round(1))
            else:
                print("\nWARNING: Only one GII category found. GII analysis skipped.")
                detailed_stats['gii_categories'] = df['GII_Category'].unique().tolist()
    except Exception as e:
        print(f"Error generating GII distribution plot: {e}")
    
    # 5. Country distribution
    try:
        country_counts = df['Country'].value_counts()
        detailed_stats['country_distribution'] = country_counts.to_dict()
        
        print("\n--- Country Distribution ---")
        for country, count in country_counts.items():
            print(f"{country}: {count} trials")
    except Exception as e:
        print(f"Error analyzing country distribution: {e}")
    
    # 6. Summary statistics table
    summary_stats = {
        'Total Trials': len(df),
        'Trials with Female Only': (df['Sex_Category'] == 'Female Only').sum(),
        'Trials with Male Only': (df['Sex_Category'] == 'Male Only').sum(),
        'Trials with Both Sexes': (df['Sex_Category'] == 'Both Sexes').sum(),
        'Avg GII': df['Gender Inequality Index'].mean(),
        'Countries Represented': df['Country'].nunique()
    }
    
    print("\n--- Summary Statistics ---")
    for stat, value in summary_stats.items():
        print(f"{stat}: {value}")
    
    # Save statistics to file for manuscript preparation
    import json
    try:
        with open('analysis_results.json', 'w') as f:
            # Convert any non-serializable objects to strings
            json_stats = {k: str(v) if not isinstance(v, (dict, list, str, int, float, bool, type(None))) else v 
                         for k, v in detailed_stats.items()}
            json.dump(json_stats, f, indent=4)
    except Exception as e:
        print(f"Error saving analysis results to JSON: {e}")

    return detailed_stats

# ----------------------------------
# INITIAL STATISTICAL ANALYSIS
# ----------------------------------

print("Performing initial statistical analysis...")

def run_statistical_analysis(df):
    results = {}
    
    # 1. Chi-square test for association between GII category and Sex category
    if 'GII_Category' in df.columns:
        contingency_table = pd.crosstab(df['GII_Category'], df['Sex_Category'])
        chi2, p, dof, expected = chi2_contingency(contingency_table)
        results['chi2_test'] = {
            'chi2': chi2,
            'p_value': p,
            'degrees_of_freedom': dof
        }
        print(f"\nChi-square test for GII Category vs Sex Category:")
        print(f"Chi2 = {chi2:.4f}, p = {p:.4f}, dof = {dof}")
    
    # 2. Logistic regression for female inclusion vs GII
    # Create binary outcome: female inclusion (female only or both) vs no female inclusion (male only)
    df['Female_Inclusion'] = df['Sex_Category'].apply(
        lambda x: 1 if x in ['Female Only', 'Both Sexes'] else 0 if x == 'Male Only' else np.nan
    )
    
    # Filter data for regression
    regression_data = df[['Female_Inclusion', 'Gender Inequality Index', 'Disease_Category', 'Standardized_Phase']].dropna()
    
    if len(regression_data) > 0:
        # Simple logistic regression with GII
        X = sm.add_constant(regression_data['Gender Inequality Index'])
        y = regression_data['Female_Inclusion']
        
        model = sm.Logit(y, X)
        try:
            result = model.fit()
            results['logistic_regression'] = {
                'params': result.params.to_dict(),
                'pvalues': result.pvalues.to_dict(),
                'summary': result.summary().as_text()
            }
            print("\nLogistic Regression Results (Female Inclusion vs GII):")
            print(f"Coefficient for GII: {result.params[1]:.4f}, p-value: {result.pvalues[1]:.4f}")
            
            # If coefficient is negative, higher GII associated with lower female inclusion
            if result.params[1] < 0:
                print("Result: Higher GII associated with LOWER female inclusion in trials")
            else:
                print("Result: Higher GII associated with HIGHER female inclusion in trials")
        
        except Exception as e:
            print(f"Error in logistic regression: {e}")
    
    # 3. Interaction analysis with disease type
    # Create a model with interaction terms
    if len(regression_data) > 0 and 'Disease_Category' in regression_data.columns:
        # Create dummy variables for disease categories
        disease_dummies = pd.get_dummies(regression_data['Disease_Category'], prefix='disease', drop_first=True)
        
        # Add dummies to regression data
        regression_data_with_dummies = pd.concat([regression_data, disease_dummies], axis=1)
        
        # Create interaction terms
        for col in disease_dummies.columns:
            regression_data_with_dummies[f"{col}_x_GII"] = regression_data_with_dummies[col] * regression_data_with_dummies['Gender Inequality Index']
        
        # Select predictor columns (GII, disease dummies, and interaction terms)
        predictor_cols = ['Gender Inequality Index'] + list(disease_dummies.columns) + [col for col in regression_data_with_dummies.columns if '_x_GII' in col]
        
        # Add constant
        X_interaction = sm.add_constant(regression_data_with_dummies[predictor_cols])
        y = regression_data_with_dummies['Female_Inclusion']
        
        try:
            # Fit model
            interaction_model = sm.Logit(y, X_interaction)
            interaction_result = interaction_model.fit()
            
            # Store and print results
            results['interaction_model'] = {
                'params': interaction_result.params.to_dict(),
                'pvalues': interaction_result.pvalues.to_dict()
            }
            
            print("\nDisease-GII Interaction Model:")
            print("Significant interactions (p < 0.05):")
            for col in predictor_cols:
                if '_x_GII' in col and interaction_result.pvalues[col] < 0.05:
                    disease = col.replace('_x_GII', '')
                    effect = "negative" if interaction_result.params[col] < 0 else "positive"
                    print(f"  {disease}: {effect} interaction (coef={interaction_result.params[col]:.4f}, p={interaction_result.pvalues[col]:.4f})")
        
        except Exception as e:
            print(f"Error in interaction model: {e}")
    
    # 4. Interaction with trial phase
    if len(regression_data) > 0 and 'Standardized_Phase' in regression_data.columns:
        # Create dummy variables for phase categories
        # Exclude unknown phase
        phase_data = regression_data[regression_data['Standardized_Phase'] != 'Unknown'].copy()
        phase_dummies = pd.get_dummies(phase_data['Standardized_Phase'], prefix='phase', drop_first=True)
        
        # Add dummies to regression data
        phase_data_with_dummies = pd.concat([phase_data, phase_dummies], axis=1)
        
        # Create interaction terms
        for col in phase_dummies.columns:
            phase_data_with_dummies[f"{col}_x_GII"] = phase_data_with_dummies[col] * phase_data_with_dummies['Gender Inequality Index']
        
        # Select predictor columns
        phase_predictor_cols = ['Gender Inequality Index'] + list(phase_dummies.columns) + [col for col in phase_data_with_dummies.columns if '_x_GII' in col]
        
        # Add constant
        X_phase = sm.add_constant(phase_data_with_dummies[phase_predictor_cols])
        y_phase = phase_data_with_dummies['Female_Inclusion']
        
        try:
            # Fit model
            phase_model = sm.Logit(y_phase, X_phase)
            phase_result = phase_model.fit()
            
            # Store and print results
            results['phase_model'] = {
                'params': phase_result.params.to_dict(),
                'pvalues': phase_result.pvalues.to_dict()
            }
            
            print("\nPhase-GII Interaction Model:")
            print("Significant interactions (p < 0.05):")
            for col in phase_predictor_cols:
                if '_x_GII' in col and phase_result.pvalues[col] < 0.05:
                    phase = col.replace('_x_GII', '')
                    effect = "negative" if phase_result.params[col] < 0 else "positive"
                    print(f"  {phase}: {effect} interaction (coef={phase_result.params[col]:.4f}, p={phase_result.pvalues[col]:.4f})")
        
        except Exception as e:
            print(f"Error in phase interaction model: {e}")
    
    return results

# ------------------------------------------
# EQUITY IN SEX REPRESENTATION ANALYSIS
# ------------------------------------------

def analyze_sex_representation_equity(df):
    """
    Analyze whether clinical trials show equitable sex representation
    comparing against population expectations.
    """
    # US population sex ratio (as of 2025 estimates)
    EXPECTED_FEMALE_RATIO = 0.508  # 50.8% female in general population
    
    # Analysis by disease type
    results = {}
    
    for disease in df['Disease_Category'].unique():
        disease_trials = df[df['Disease_Category'] == disease]
        
        # Calculate total participants that could be female
        total_both_sex = len(disease_trials[disease_trials['Sex_Category'] == 'Both Sexes'])
        female_only = len(disease_trials[disease_trials['Sex_Category'] == 'Female Only'])
        male_only = len(disease_trials[disease_trials['Sex_Category'] == 'Male Only'])
        
        # Expected female participation
        total_potential_participants = (total_both_sex * 2) + female_only + male_only
        expected_female = total_potential_participants * EXPECTED_FEMALE_RATIO
        
        # Actual maximum female participation (assuming equal split in both-sex trials)
        actual_female = (total_both_sex) + female_only
        
        # Chi-square test
        observed = [actual_female, total_potential_participants - actual_female]
        expected = [expected_female, total_potential_participants - expected_female]
        chi2, p_value = chi2_contingency([observed, expected])[0:2]
        
        results[disease] = {
            'total_trials': len(disease_trials),
            'both_sex_trials': total_both_sex,
            'female_only_trials': female_only,
            'male_only_trials': male_only,
            'potential_female_ratio': actual_female / total_potential_participants,
            'expected_female_ratio': EXPECTED_FEMALE_RATIO,
            'chi2_statistic': chi2,
            'p_value': p_value,
            'significant_difference': p_value < 0.05,
            'direction': 'over-representation' if actual_female > expected_female else 'under-representation' if actual_female < expected_female else 'equal'
        }
    
    return results

# -------------------------------------------------
# FETCH ELIGIBILITY CRITERIA FOR A SUBSET OF TRIALS
# -------------------------------------------------

# This maintains the original functionality of the starter.py script

def fetch_eligibility_data(df, n_trials=100):
    print(f"\nFetching eligibility criteria for {n_trials} trials...")
    # Ensure we have a column with NCT IDs
    nct_ids = df["NCT Number_trial"].dropna().unique()
    
    # Limit to n_trials
    if len(nct_ids) > n_trials:
        nct_ids = nct_ids[:n_trials]
    
    # Fetch eligibility text
    eligibility_texts = []
    for nct_id in nct_ids:
        text = fetch_eligibility(nct_id)
        eligibility_texts.append({"NCT Number_trial": nct_id, "Eligibility Criteria": text})
        time.sleep(0.5)  # Respectful delay
    
    # Create DataFrame and merge
    eligibility_df = pd.DataFrame(eligibility_texts)
    df_with_eligibility = pd.merge(df, eligibility_df, on="NCT Number_trial", how="left")
    
    return df_with_eligibility

# --------------------------
# MAIN EXECUTION
# --------------------------

if __name__ == "__main__":
    # Run exploratory analysis on clean data
    summary_stats = run_exploratory_analysis(df_clean)
    
    # Run statistical analysis
    stat_results = run_statistical_analysis(df_clean)
    
    # Run equity analysis on sex representation
    print("\n=== Sex Representation Equity Analysis ===")
    equity_results = analyze_sex_representation_equity(df_clean)
    
    # Print results
    for disease, stats in equity_results.items():
        print(f"\nDisease: {disease}")
        print(f"Total trials: {stats['total_trials']}")
        print(f"Actual female ratio: {stats['potential_female_ratio']:.3f}")
        print(f"Expected female ratio: {stats['expected_female_ratio']:.3f}")
        print(f"Chi-square statistic: {stats['chi2_statistic']:.2f}")
        print(f"P-value: {stats['p_value']:.4f}")
        if stats['significant_difference']:
            print(f"Significant {stats['direction']} of females")
        else:
            print("No significant difference from expected ratio")
    
    # Save equity results to JSON for manuscript preparation
    try:
        with open('data/equity_analysis_results.json', 'w') as f:
            json.dump(equity_results, f, indent=4)
        print("\nEquity analysis results saved to data/equity_analysis_results.json")
    except Exception as e:
        print(f"Error saving equity analysis results: {e}")
        # Try alternative path
        try:
            with open('equity_analysis_results.json', 'w') as f:
                json.dump(equity_results, f, indent=4)
            print("\nEquity analysis results saved to equity_analysis_results.json")
        except Exception as e2:
            print(f"Could not save equity results: {e2}")

    # Fetch eligibility criteria for a subset of trials
    df_with_eligibility = fetch_eligibility_data(df_clean, n_trials=50)  # Limiting to 50 for demonstration
    
    # Save processed data to files
    print("\nSaving processed data to files...")
    df_clean.to_csv("processed_clinical_trials.csv", index=False)
    df_with_eligibility.to_csv("clinical_trials_with_eligibility.csv", index=False)
    
    print("\nAnalysis complete! Results saved to figures/ directory and CSV files.")
    print("Next step: Review the results and draft the manuscript.")
