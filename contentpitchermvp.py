#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Oct  2 18:45:40 2024

@author: colleenshifflett
"""
import pandas as pd
import streamlit as st
from io import StringIO
import re

# Title and description
st.title("Content and Queries Analyzer")
st.write("Upload your content and query CSV files to analyze missing keywords.")

# File upload widgets
content_file = st.file_uploader("Upload Content CSV (Content, URL)", type="csv")
queries_file = st.file_uploader("Upload Queries CSV (queries, avgpos)", type="csv")

# Function to tokenize text by converting to lowercase and splitting by words
def tokenize(text):
    text = text.lower()
    text = re.sub(r'[^a-z0-9\s]', '', text)  # Keep only letters, numbers, and spaces
    tokens = text.split()
    return tokens

# Function to find missing queries in content and make recommendations
def find_missing_queries_with_recommendations(content_df, queries_df):
    recommendations = []

    for _, query_row in queries_df.iterrows():
        query = query_row['queries']
        query_tokens = tokenize(query)
        avgpos = query_row['avgpos']
        found_in_content = False

        for _, content_row in content_df.iterrows():
            content_tokens = tokenize(content_row['Content'])
            if all(token in content_tokens for token in query_tokens):
                recommendations.append({
                    'queries': query,
                    'avgpos': avgpos,
                    'recommendation': f"Add to {content_row['URL']}"
                })
                found_in_content = True
                break

        if not found_in_content:
            recommendations.append({
                'queries': query,
                'avgpos': avgpos,
                'recommendation': "Create new content"
            })

    recommendations_df = pd.DataFrame(recommendations)
    return recommendations_df

# Trigger analysis only when both files are uploaded
if content_file is not None and queries_file is not None:
    # Read uploaded CSV files
    content_df = pd.read_csv(content_file)
    queries_df = pd.read_csv(queries_file)

    # Run the analysis
    recommendations_df = find_missing_queries_with_recommendations(content_df, queries_df)

    # Display results
    st.write("### Analysis Results")
    st.write(recommendations_df)

    # Provide a download button for the recommendations
    csv = recommendations_df.to_csv(index=False).encode('utf-8')
    st.download_button(
        label="Download Recommendations as CSV",
        data=csv,
        file_name='recommendations_output.csv',
        mime='text/csv',
    )
else:
    st.write("Please upload both content and queries CSV files to start the analysis.")
