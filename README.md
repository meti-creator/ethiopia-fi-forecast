
# Now create the README file
readme_content = '''# Ethiopia Financial Inclusion Dashboard

## Task 5: Interactive Dashboard Development

An interactive Streamlit dashboard for exploring Ethiopia's financial inclusion data, understanding event impacts, and viewing forecasts for 2025-2027.

---

## Overview

This dashboard integrates data and models from Tasks 1-4 to provide stakeholders with:

- **Key metrics** at a glance (account ownership, mobile money penetration, P2P/ATM crossover, gender gap)
- **Interactive trend exploration** with date range selectors and multi-channel comparisons
- **Forecast visualizations** with confidence intervals and three scenarios (Optimistic, Base Case, Pessimistic)
- **Inclusion projections** showing progress toward the 60% target
- **Answers to consortium key questions** based on integrated analysis

---

## Prerequisites

- Python 3.9+
- pip or conda package manager

---

## Installation

### 1. Clone or navigate to the project directory

```bash
cd dashboard/
```

### 2. Create a virtual environment (recommended)

```bash
# Using venv
python -m venv venv

# Activate on macOS/Linux
source venv/bin/activate

# Activate on Windows
venv\\Scripts\\activate
```

### 3. Install dependencies

```bash
pip install streamlit plotly pandas numpy
```

Or install from requirements:

```bash
pip install -r requirements.txt
```

### 4. Run the dashboard

```bash
streamlit run app.py
```

The dashboard will open in your default web browser at `http://localhost:8501`.

---

## Dashboard Sections

### 1. Overview
- Key metric summary cards with current values and trends
- P2P/ATM Crossover Ratio indicator (historic milestone: digital > cash)
- Growth rate highlights (P2P +158% YoY, Telebirr 54.8M users, M-Pesa +245%)
- Progress toward NFIS-II targets vs. current reality
- Events timeline visualization (2021-2025)
- Data download functionality

### 2. Trends
- **Account Ownership Trajectory**: Historical Findex data (2014-2024) with growth rate analysis
- **Mobile Money Penetration**: Demand-side (Findex) vs. supply-side (operator) comparison
- **P2P vs ATM**: The digital crossover milestone with interactive gauge indicator
- **Gender Analysis**: Account ownership by gender and gap trend
- **Channel Comparison**: Multi-indicator overlay with user-selected indicators

### 3. Forecasts
- Account Ownership Rate forecast (2025-2027) with all three scenarios and 95% CI
- Digital Payment Usage forecast with NFIS-II target comparison
- Mobile Money Account Rate forecast
- Key projected milestones table
- Model selection option (Event-Augmented Trend, Logistic Growth, Linear Regression, Comparable Country Benchmark)
- Data download for all forecast tables

### 4. Inclusion Projections
- Progress toward **60% revised target** (from NFIS-II 70% by 2025)
- Scenario comparison table with achievement status
- Multi-indicator projection dashboard (Account Ownership, Digital Payments, Mobile Money, Gender Gap)
- Scenario narratives explaining assumptions

### 5. Key Questions
Answers to six critical consortium questions:
1. Will Ethiopia reach 70% account ownership by 2025?
2. Why the +3pp growth despite 65M+ mobile money accounts?
3. What is the most impactful event?
4. What are the biggest risks to 60% by 2027?
5. How should stakeholders prioritize interventions?
6. What data gaps most limit analysis?

---

## Data Sources

| Source | Data Type | Coverage |
|--------|-----------|----------|
| World Bank Global Findex | Demand-side surveys | 2014, 2017, 2021, 2024 |
| EthSwitch | Transaction data | FY2023/24, FY2024/25 |
| Ethio Telecom | Operator metrics | FY2024/25 |
| Safaricom Ethiopia | Operator metrics | 2024 |
| NBE | Policy targets | NFIS-II (2021-2025) |
| GSMA | Mobile market data | 2024 |
| ITU/A4AI | Affordability | 2024 |

---

## Forecast Methodology

The dashboard uses an **Event-Augmented Trend Model** (recommended) that combines:

1. **Trend continuation**: Logistic growth fit to historical Findex points
2. **Event impact estimates**: Derived from the impact_link dataset (Task 3), incorporating:
   - Impact magnitude (high/medium/low)
   - Lag effects (1-24 months)
   - Evidence basis (empirical, literature, theoretical)
3. **Scenario weighting**: Optimistic (+strong event effects), Base Case (moderate), Pessimistic (weak)
4. **Confidence intervals**: Based on data sparsity (only 4 Findex observations)

**Limitations**: Sparse Findex data (4 points in 10 years) creates wide confidence intervals. Forecasts should be treated as directional indicators, not precise predictions.

---

## Interactive Features

- **Global scenario selector** in sidebar (applies across all pages)
- **Date range filters** on Trends page
- **Multi-select channel comparison** on Trends page
- **Model selection dropdown** on Forecasts page
- **Multi-indicator projection selector** on Inclusion Projections page
- **Expandable Q&A sections** on Key Questions page
- **CSV data download** buttons on Overview and Forecasts pages

---

## Technical Requirements Met

- [x] At least 4 interactive visualizations (10+ Plotly charts across pages)
- [x] Clear labels and explanations (every chart has title, axis labels, annotations)
- [x] Data download functionality (CSV exports on multiple pages)
- [x] Scenario selector (Optimistic/Base/Pessimistic)
- [x] Confidence intervals on forecasts
- [x] Key metrics summary cards
- [x] Event impact visualization
- [x] Progress toward target visualization

---

## Project Structure

```
dashboard/
├── app.py              # Main Streamlit application
├── README.md           # This file
├── requirements.txt    # Python dependencies
└── data/               # (Optional) Data files if loading externally
```

---

## Requirements File

Create a `requirements.txt` with:

```
streamlit>=1.28.0
plotly>=5.15.0
pandas>=2.0.0
numpy>=1.24.0
```

---

## Git Workflow (for Task 5)

```bash
# Ensure you're on main with task-3 merged
git checkout main
git pull origin main

# Create task-5 branch
git checkout -b task-5

# Add dashboard files
git add app.py README.md requirements.txt
git commit -m "Add Task 5: Interactive Streamlit dashboard for Ethiopia FI exploration"
git commit -m "Include 5 pages: Overview, Trends, Forecasts, Inclusion Projections, Key Questions"
git commit -m "Add 10+ interactive Plotly visualizations with scenario selectors"
git commit -m "Add data download functionality and confidence intervals"

# Push and create PR
git push origin task-5
# Create Pull Request on GitHub to merge task-5 -> main
```

---

## Contact

Built as part of the Ethiopia Financial Inclusion Data Science Program.
Dashboard integrates work from Tasks 1-4: Data Exploration, EDA, Event Impact Modeling, and Forecasting.
'''

with open('/mnt/agents/output/dashboard/README.md', 'w') as f:
    f.write(readme_content)

# Create requirements.txt
requirements = '''streamlit>=1.28.0
plotly>=5.15.0
pandas>=2.0.0
numpy>=1.24.0
openpyxl>=3.1.0
'''

with open('/mnt/agents/output/dashboard/requirements.txt', 'w') as f:
    f.write(requirements)

print("README.md saved!")
print("requirements.txt saved!")
