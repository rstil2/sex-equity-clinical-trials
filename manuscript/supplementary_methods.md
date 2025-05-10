# Supplementary Methods

## Detailed Data Processing and Analysis Methods

### Data Cleaning and Processing Code

The following Python code was used for data cleaning and categorization:

```python
def clean_data(df):
    # Convert column types appropriately
    clean_df = df.copy()
    
    # Handle missing values
    for col in ['Sex', 'Phases', 'Country']:
        if col in clean_df.columns:
            clean_df[col] = clean_df[col].fillna('Unknown')
    
    # Filter out rows with no country or GII data
    clean_df = clean_df[clean_df['Country'].notna()]
    clean_df = clean_df[clean_df['Gender Inequality Index'].notna()]
    
    # Convert GII to numeric
    if 'Gender Inequality Index' in clean_df.columns:
        clean_df['Gender Inequality Index'] = pd.to_numeric(clean_df['Gender Inequality Index'], errors='coerce')
    
    return clean_df

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
```

### Disease Categorization Logic

The following code was used to categorize trials by disease type:

```python
def categorize_disease(conditions):
    if pd.isna(conditions):
        return 'Unknown'
    
    conditions = str(conditions).upper()
    
    disease_categories = {
        'COVID-19': ['COVID', 'SARS-COV-2', 'CORONAVIRUS'],
        'HIV/AIDS': ['HIV', 'AIDS', 'HUMAN IMMUNODEFICIENCY VIRUS'],
        'Cancer': ['CANCER', 'TUMOR', 'NEOPLASM', 'CARCINOMA'],
        'Cardiovascular': ['HEART', 'CARDIAC', 'CARDIOVASCULAR'],
        'Diabetes': ['DIABETES', 'DIABETIC'],
        'Mental Health': ['PSYCHIATRIC', 'DEPRESSION', 'ANXIETY'],
        'Respiratory': ['ASTHMA', 'COPD', 'LUNG', 'PULMONARY'],
        'Infectious Disease': ['INFECTION', 'INFECTIOUS', 'BACTERIAL', 'VIRAL']
    }
    
    for category, keywords in disease_categories.items():
        if any(keyword in conditions for keyword in keywords):
            return category
    
    return 'Other'
```

### Statistical Analysis Details

The following statistical methods were implemented:

1. Chi-square test for association between GII categories and sex representation:
```python
contingency_table = pd.crosstab(df['GII_Category'], df['Sex_Category'])
chi2, p, dof, expected = chi2_contingency(contingency_table)
```

2. Logistic regression for female inclusion vs GII:
```python
X = sm.add_constant(df['Gender Inequality Index'])
y = df['Female_Inclusion']
model = sm.Logit(y, X)
result = model.fit()
```

### Data Visualization Code

Detailed code for generating the manuscript figures is available in the `generate_figures.py` script in the project repository.

## Software and Package Versions

- Python 3.12
- pandas 1.5.3
- numpy 1.23.5
- statsmodels 0.13.5
- scipy 1.9.3
- matplotlib 3.6.2
- seaborn 0.12.2

