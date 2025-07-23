import streamlit as st
import pandas as pd
import base64
import io

# Set page title and configuration
st.set_page_config(
    page_title="GSC CTR Stats By Position",
    page_icon="📊",
    layout="wide"
)

st.title("Calculate GSC CTR Stats By Position")
st.markdown("""
This app calculates CTR statistics by SERP position from your Google Search Console data.
Upload your 'Queries.csv' file exported from Google Search Console.
""")

# File uploader
uploaded_file = st.file_uploader("Upload your GSC Queries.csv file", type=['csv'])

if uploaded_file is not None:
    # Read the CSV file
    try:
        # Using a more robust method to read CSV with io
        csv_data = uploaded_file.read()
        df = pd.read_csv(io.StringIO(csv_data.decode('utf-8')))
        
        # Display raw data
        st.subheader("Raw Google Search Console Data")
        st.dataframe(df.head())
        
        # Define column name mappings for different possible column names
        column_mappings = {
            'Query': ['Query', 'query', 'queries', 'Queries', 'keywords', 'keyword', 'Keyword', 'Keywords'],
            'Landing Page': ['Landing Page', 'landing page', 'URLs', 'Address', 'address'],
            'Clicks': ['Clicks', 'clicks'],
            'Impressions': ['Impressions', 'impressions'],
            'CTR': ['CTR', 'Avg. CTR', 'URL CTR'],
            'Position': ['Position', 'Avg. Position', 'Avg Position', 'Avg. Pos', 'Avg Pos', 'Positions', 'positions', 'Pos', 'pos']
        }
        
        # Find actual column names in the dataframe
        actual_columns = {}
        missing_columns = []
        
        for standard_name, possible_names in column_mappings.items():
            found = False
            for possible_name in possible_names:
                if possible_name in df.columns:
                    actual_columns[standard_name] = possible_name
                    found = True
                    break
            
            if not found:
                missing_columns.append(standard_name)
        
        # Check for essential columns (Query, Clicks, Impressions, CTR, Position)
        essential_columns = ['Query', 'Clicks', 'Impressions', 'CTR', 'Position']
        missing_essential = [col for col in essential_columns if col in missing_columns]
        
        if missing_essential:
            st.error(f"Missing required columns: {', '.join(missing_essential)}. Please make sure your CSV file contains these columns.")
            st.info("Expected column names:")
            for col in missing_essential:
                st.write(f"- {col}: {', '.join(column_mappings[col])}")
        else:
            # Rename columns to standard names
            rename_dict = {actual_name: standard_name for standard_name, actual_name in actual_columns.items()}
            df = df.rename(columns=rename_dict)
            
            st.success("Successfully identified all required columns!")
            st.info(f"Columns found: {', '.join([f'{actual_columns[col]} → {col}' for col in essential_columns])}")
            
            # Set maximum positions to analyze
            max_positions = st.slider("Maximum Position to Analyze", min_value=1, max_value=20, value=9)
            
            if st.button("Calculate CTR Stats"):
                # Create variables and empty dataframe
                x = 1
                y = max_positions + 1
                d = {'Position': [], 'Sum Clicks': [], 'Sum Impressions':[], 'Avg CTR':[],'Min CTR':[],'Max CTR':[],'Max CTR KW':[]}
                df2 = pd.DataFrame(data=d)
                
                # Process the data
                with st.spinner("Processing data..."):
                    while x < y:
                        # Filter by position range (x to x.9)
                        df1 = df[(df['Position'] >= x) & (df['Position'] < x+1)]
                        
                        if not df1.empty:
                            df1 = df1.sort_values('CTR', ascending=False)
                            
                            # Handle different CTR formats (% or decimal)
                            df1['CTR_numeric'] = df1['CTR'].copy()
                            if df1['CTR_numeric'].dtype == 'object':
                                # Handle percentage strings (e.g., '5.2%')
                                df1['CTR_numeric'] = df1['CTR_numeric'].astype(str).str.replace('%', '')
                            
                            # Convert to numeric, handling errors
                            df1['CTR_numeric'] = pd.to_numeric(df1['CTR_numeric'], errors='coerce')
                            
                            # If values appear to be decimal (0.052 instead of 5.2), multiply by 100
                            if df1['CTR_numeric'].max() < 100:
                                df1['CTR_numeric'] = df1['CTR_numeric'] * 100
                            
                            try:
                                # Calculate statistics
                                ctr = int(round((df1['Clicks'].sum() / df1['Impressions'].sum()) * 100))
                                ctr_min = int(df1['CTR_numeric'].min())
                                ctr_max = int(df1['CTR_numeric'].max())
                                
                                # Get the keyword with maximum CTR
                                kw_col = 'Query'  # Now we know it's standardized
                                ctr_max_kw = df1.iloc[0][kw_col]
                                
                                clicks = int(df1['Clicks'].sum())
                                impressions = int(df1['Impressions'].sum())
                                
                                # Create a dictionary for this position's data
                                data = {
                                    'Position': int(x),
                                    'Sum Clicks': clicks,
                                    'Sum Impressions': impressions,
                                    'Avg CTR': ctr,
                                    'Min CTR': ctr_min,
                                    'Max CTR': ctr_max,
                                    'Max CTR KW': ctr_max_kw
                                }
                                
                                # Append to the results dataframe
                                df2 = pd.concat([df2, pd.DataFrame([data])], ignore_index=True)
                            except Exception as e:
                                st.warning(f"Could not process position {x}: {e}")
                        
                        x += 1
                    
                    # Check if we have any results
                    if df2.empty:
                        st.error("No results were generated. Please check that your data contains the required columns and position values.")
                    else:
                        # Convert numeric columns to integers
                        int_cols = ['Position', 'Sum Clicks', 'Sum Impressions', 'Avg CTR', 'Min CTR', 'Max CTR']
                        for col in int_cols:
                            if col in df2.columns:
                                df2[col] = pd.to_numeric(df2[col], errors='coerce').fillna(0).astype(int)
                        
                        # Format CTR columns to include '%'
                        for col in ['Avg CTR', 'Min CTR', 'Max CTR']:
                            df2[col] = df2[col].astype(str) + '%'
                        
                        # Display results
                        st.subheader("CTR Stats By Position")
                        st.dataframe(df2)
                        
                        # Create download link for results
                        csv = df2.to_csv(index=False)
                        b64 = base64.b64encode(csv.encode()).decode()
                        href = f'<a href="data:file/csv;base64,{b64}" download="gsc_ctr_stats.csv">Download CSV File</a>'
                        st.markdown(href, unsafe_allow_html=True)
                        
                        # Visualize the data
                        st.subheader("CTR by Position")
                        chart_data = df2.copy()
                        chart_data['Avg CTR'] = chart_data['Avg CTR'].str.replace('%', '').astype(int)
                        st.bar_chart(chart_data.set_index('Position')['Avg CTR'])
                        
                        st.subheader("Clicks and Impressions by Position")
                        st.line_chart(chart_data.set_index('Position')[['Sum Clicks', 'Sum Impressions']])
    except Exception as e:
        st.error(f"Error processing file: {e}")
else:
    st.info("Please upload your Google Search Console Queries.csv file to begin analysis.")

# Sample data option for testing
if st.checkbox("Don't have a GSC file? Use sample data instead"):
    sample_data = {
        'Position': [1.1, 1.5, 1.8, 2.2, 2.7, 3.1, 3.6, 4.2, 4.8],
        'Clicks': [120, 95, 80, 65, 50, 35, 25, 15, 10],
        'Impressions': [1000, 900, 850, 800, 750, 700, 650, 600, 550],
        'CTR': ['12%', '10.5%', '9.4%', '8.1%', '6.7%', '5%', '3.8%', '2.5%', '1.8%'],
        'Query': ['seo tips', 'python seo', 'seo guide', 'search console', 'gsc api', 'seo reporting', 'ctr analysis', 'position tracking', 'rank checker']
    }
    sample_df = pd.DataFrame(sample_data)
    st.subheader("Sample Data")
    st.dataframe(sample_df)
    
    if st.button("Calculate with Sample Data"):
        # Reuse the file uploader's logic but with sample data
        df = sample_df
        max_positions = 5
        
        # Create variables and empty dataframe
        x = 1
        y = max_positions + 1
        d = {'Position': [], 'Sum Clicks': [], 'Sum Impressions':[], 'Avg CTR':[],'Min CTR':[],'Max CTR':[],'Max CTR KW':[]}
        df2 = pd.DataFrame(data=d)
        
        # Process the data
        with st.spinner("Processing sample data..."):
            while x < y:
                df1 = df[(df['Position'] >= x) & (df['Position'] < x+1)]
                
                if not df1.empty:
                    df1 = df1.sort_values('CTR', ascending=False)
                    
                    # Handle percentage strings
                    df1['CTR_numeric'] = df1['CTR'].str.replace('%', '')
                    df1['CTR_numeric'] = pd.to_numeric(df1['CTR_numeric'], errors='coerce')
                    
                    try:
                        ctr = int(round((df1['Clicks'].sum() / df1['Impressions'].sum()) * 100))
                        ctr_min = int(df1['CTR_numeric'].min())
                        ctr_max = int(df1['CTR_numeric'].max())
                        ctr_max_kw = df1.iloc[0]['Query']
                        clicks = int(df1['Clicks'].sum())
                        impressions = int(df1['Impressions'].sum())
                        
                        data = {
                            'Position': int(x),
                            'Sum Clicks': clicks,
                            'Sum Impressions': impressions,
                            'Avg CTR': ctr,
                            'Min CTR': ctr_min,
                            'Max CTR': ctr_max,
                            'Max CTR KW': ctr_max_kw
                        }
                        
                        df2 = pd.concat([df2, pd.DataFrame([data])], ignore_index=True)
                    except Exception as e:
                        st.warning(f"Could not process position {x}: {e}")
                
                x += 1
            
            # Format results
            int_cols = ['Position', 'Sum Clicks', 'Sum Impressions', 'Avg CTR', 'Min CTR', 'Max CTR']
            for col in int_cols:
                df2[col] = pd.to_numeric(df2[col], errors='coerce').fillna(0).astype(int)
            
            for col in ['Avg CTR', 'Min CTR', 'Max CTR']:
                df2[col] = df2[col].astype(str) + '%'
            
            # Display results
            st.subheader("CTR Stats By Position")
            st.dataframe(df2)
            
            # Visualize the data
            st.subheader("CTR by Position")
            chart_data = df2.copy()
            chart_data['Avg CTR'] = chart_data['Avg CTR'].str.replace('%', '').astype(int)
            st.bar_chart(chart_data.set_index('Position')['Avg CTR'])
            
            st.subheader("Clicks and Impressions by Position")
            st.line_chart(chart_data.set_index('Position')[['Sum Clicks', 'Sum Impressions']])

# Footer
st.markdown("---")
st.markdown("Built with Streamlit • Inspired by [importSEM's Python SEO tutorial](https://importsem.com/calculate-gsc-ctr-stats-by-position-using-python-for-seo/)")
