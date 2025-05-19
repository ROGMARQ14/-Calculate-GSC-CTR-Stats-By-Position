import streamlit as st
import pandas as pd
import numpy as np
import base64

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
        df = pd.read_csv(uploaded_file)
        
        # Display raw data
        st.subheader("Raw Google Search Console Data")
        st.dataframe(df.head())
        
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
                        
                        # Convert CTR to numeric
                        df1['CTR'] = df1['CTR'].astype(str).str.replace('%', '')
                        df1['CTR'] = pd.to_numeric(df1['CTR'], errors='coerce')
                        
                        try:
                            ctr = int(round((df1['Clicks'].sum() / df1['Impressions'].sum()) * 100))
                            ctr_min = int(df1['CTR'].min())
                            ctr_max = int(df1['CTR'].max())
                            ctr_max_kw = df1.iloc[0]['Top queries'] if 'Top queries' in df1.columns else df1.iloc[0].iloc[0]
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

# Footer
st.markdown("---")
st.markdown("Built with Streamlit • Inspired by [importSEM's Python SEO tutorial](https://importsem.com/calculate-gsc-ctr-stats-by-position-using-python-for-seo/)")
