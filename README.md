# Gender Inequality and Trial Representation Analysis

This repository contains the analysis and manuscript examining sex representation equity in clinical trials.

## Project Structure

```
/
├── data/                                 # Data files
│   ├── merged_clinical_indicators_2025-05-01.csv  # Original raw data
│   ├── processed_clinical_trials.csv     # Cleaned and processed data
│   ├── equity_analysis_results.json      # Statistical analysis results
│   ├── analysis_results.json             # Additional analysis outputs
│   └── clinical_trials_with_eligibility.csv  # Trial eligibility data
├── figures/                              # Generated visualizations
│   ├── figure1_sex_distribution.png      # Distribution of trials by sex
│   ├── figure2_inclusion_rates.png       # Female inclusion rates
│   └── figure3_disease_distribution.png  # Disease-specific patterns
├── manuscript/                           # Manuscript and submission files
│   ├── manuscript_equity_focus.md        # Main manuscript
│   ├── supplementary_methods.md          # Detailed methods
│   ├── cover_letter_equity.md            # Journal cover letter
│   ├── journal_recommendations.md        # Alternative journal options
│   └── README.md                         # This file
├── scripts/                              # Analysis scripts
│   ├── starter.py                        # Main analysis script
│   ├── generate_figures.py               # Figure generation
│   └── cleanup.sh                        # Directory organization
└── tables/                               # Analysis tables
    ├── table1.md                         # Statistical equity analysis
    └── table2.md                         # Trial design distribution
```

## Files Description

### Data Files
- `merged_clinical_indicators_2025-05-01.csv`: Original dataset from ClinicalTrials.gov
- `processed_clinical_trials.csv`: Cleaned data with standardized categories
- `equity_analysis_results.json`: Results from statistical equity analysis

### Scripts
- `starter.py`: Main analysis script implementing equity testing framework
- `generate_figures.py`: Creates publication-quality figures
- `cleanup.sh`: Maintains clean directory structure

### Manuscript Files
- `manuscript_equity_focus.md`: Complete manuscript prepared for submission
- `supplementary_methods.md`: Detailed technical methods
- `cover_letter_equity.md`: Journal submission cover letter

### Tables and Figures
- `table1.md`: Statistical analysis of sex representation equity
- `table2.md`: Distribution of trial designs
- `figure1-3`: Visualizations supporting key findings

## Analysis Reproduction

To reproduce the analysis:

1. Run `scripts/starter.py` to process data and perform statistical analysis
2. Run `scripts/generate_figures.py` to create visualizations
3. Results will be saved in data/, figures/, and tables/ directories

## Dependencies

- Python 3.12
- pandas 1.5.3
- numpy 1.23.5
- statsmodels 0.13.5
- matplotlib 3.6.2
- seaborn 0.12.2
