# GSC CTR Analyzer

A Streamlit application that calculates Click-Through Rate (CTR) statistics by position from Google Search Console (GSC) data.

## Features

- Upload GSC Queries.csv export files
- Calculate CTR statistics by SERP position
- View summary data including:
  - Sum of clicks per position
  - Sum of impressions per position
  - Average CTR per position
  - Minimum CTR per position
  - Maximum CTR per position
  - Keyword with maximum CTR per position
- Visualize results with charts
- Download processed data as CSV

## Installation

1. Clone this repository or download the files
2. Install the required packages:

```bash
pip install -r requirements.txt
```

## Usage

1. Export your Google Search Console data:
   - Go to Google Search Console
   - Open Performance report
   - Select date range (up to 16 months)
   - Click "EXPORT" → "CSV" for queries
   - Download and extract the Queries.csv file

2. Run the Streamlit app:

```bash
streamlit run app.py
```

3. Upload your Queries.csv file
4. Configure the maximum position to analyze
5. Click "Calculate CTR Stats"
6. View and download your results

## Data Requirements

The uploaded CSV file should contain the following columns:
- Top queries
- Position
- Clicks
- Impressions
- CTR

## Based On

This application is based on the tutorial from [importSEM](https://importsem.com/calculate-gsc-ctr-stats-by-position-using-python-for-seo/).
