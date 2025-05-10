#!/bin/bash
# Cleanup script to organize project files

# Create a backup directory for files we're not sure about
mkdir -p backup

# Clean up root directory
[ -f analysis_results.json ] && mv analysis_results.json data/
[ -f clinical_trials_with_eligibility.csv ] && mv clinical_trials_with_eligibility.csv data/
[ -f equity_analysis_results.json ] && mv equity_analysis_results.json data/
[ -f processed_clinical_trials.csv ] && mv processed_clinical_trials.csv data/

# Clean up figures directory
if [ -d figures ]; then
  cd figures
  [ -f sex_by_disease.png ] && mv sex_by_disease.png ../backup/
  [ -f sex_by_gii.png ] && mv sex_by_gii.png ../backup/
  [ -f sex_by_phase.png ] && mv sex_by_phase.png ../backup/
  [ -f sex_distribution.png ] && mv sex_distribution.png ../backup/
  cd ..
fi

# Clean up manuscript directory
if [ -d manuscript ]; then
  cd manuscript
  [ -f manuscript_BMC.docx ] && mv manuscript_BMC.docx ../backup/
  [ -f manuscript_draft.md ] && mv manuscript_draft.md ../backup/
  [ -f cover_letter.md ] && mv cover_letter.md ../backup/
  [ -f manuscript_BMC_format.md ] && mv manuscript_BMC_format.md ../backup/
  cd ..
fi

# Clean up tables directory
if [ -d tables ]; then
  cd tables
  [ -f "table 1.xlsx" ] && mv "table 1.xlsx" ../backup/
  [ -f "table 2.xlsx" ] && mv "table 2.xlsx" ../backup/
  cd ..
fi

# Remove duplicate files in data directory if they exist in root
if [ -d data ]; then
  cd data
  for file in *.json *.csv; do
    if [ -f "../$file" ] && [ -f "$file" ]; then
      echo "Duplicate found: $file - keeping data/ version"
      mv "../$file" ../backup/
    fi
  done
  cd ..
fi

# Create .gitignore to prevent backup files from being tracked
echo "backup/" > .gitignore

echo "Final directory structure:"
echo "/"
echo "├── data/"
echo "│   ├── merged_clinical_indicators_2025-05-01.csv (original data)"
echo "│   ├── processed_clinical_trials.csv (cleaned data)"
echo "│   └── equity_analysis_results.json (analysis results)"
echo "├── figures/"
echo "│   ├── figure1_sex_distribution.png"
echo "│   ├── figure2_inclusion_rates.png"
echo "│   └── figure3_disease_distribution.png"
echo "├── manuscript/"
echo "│   ├── manuscript_equity_focus.md (main manuscript)"
echo "│   ├── supplementary_methods.md"
echo "│   ├── cover_letter_equity.md"
echo "│   ├── journal_recommendations.md"
echo "│   └── README.md"
echo "├── tables/"
echo "│   ├── table1.md"
echo "│   └── table2.md"
echo "├── generate_figures.py"
echo "└── starter.py"

echo "Cleanup complete. Redundant files moved to backup directory."

