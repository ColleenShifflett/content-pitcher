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
import altair as alt
import matplotlib.pyplot as plt
import numpy as np

# Set page configuration
st.set_page_config(
    page_title="Content Pitcher - Content and Queries Analyzer",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Title and description
st.title("Content and Queries Analyzer")
st.write("Upload your content and query CSV files to analyze missing keywords.")

# File upload widgets
content_file = st.file_uploader("Upload Content CSV (Content, URL)", type="csv")
queries_file = st.file_uploader("Upload Queries CSV (queries, avgpos)", type="csv")

# Function to tokenize text by converting to lowercase and splitting by words
def tokenize(text):
    if text is None:
        return []
    
    text = str(text).lower()
    text = re.sub(r'[^a-z0-9\s]', ' ', text)  # Replace non-alphanumeric with spaces
    
    # Split into tokens
    tokens = text.split()
    
    return tokens

# Function to find missing queries in content and make recommendations
def find_missing_queries_with_recommendations(content_df, queries_df):
    recommendations = []

    for _, query_row in queries_df.iterrows():
        query = query_row['queries']
        query_tokens = tokenize(query)
        avgpos = query_row['avgpos']
        
        # Track the best match for each query
        best_match = {
            'score': 0,
            'url': None,
            'token_matches': 0
        }

        for _, content_row in content_df.iterrows():
            content_text = content_row['Content']
            content_tokens = tokenize(content_text)
            url = content_row['URL']
            # Extract meaningful tokens from URL by replacing common separators with spaces
            url_tokens = tokenize(url.replace('/', ' ').replace('-', ' ').replace('_', ' '))
            
            # Calculate content match score
            content_matches = sum(1 for token in query_tokens if token in content_tokens)
            content_score = content_matches / len(query_tokens) if query_tokens else 0
            
            # Calculate URL match score (this is key for recommending the most relevant URL)
            url_matches = sum(1 for token in query_tokens if token in url_tokens)
            url_score = url_matches / len(query_tokens) if query_tokens else 0
            
            # Combined score with higher weight on URL matches
            combined_score = (content_score * 0.4) + (url_score * 0.6)
            
            # Additional bonus for exact query matches in URL
            exact_query = ' '.join(query_tokens)
            url_lower = url.lower()
            if exact_query in url_lower:
                combined_score += 0.3
                
            # Track the best match
            if combined_score > best_match['score'] or (combined_score == best_match['score'] and url_matches > best_match['token_matches']):
                best_match['score'] = combined_score
                best_match['url'] = url
                best_match['token_matches'] = url_matches

        # Make recommendation based on the best match
        if best_match['score'] > 0:
            recommendations.append({
                'queries': query,
                'avgpos': avgpos,
                'recommendation': f"Add to {best_match['url']}",
                'relevance_score': round(best_match['score'] * 100, 2),
                'match_quality': "High" if best_match['score'] > 0.7 else "Medium" if best_match['score'] > 0.4 else "Low"
            })
        else:
            recommendations.append({
                'queries': query,
                'avgpos': avgpos,
                'recommendation': "Create new content",
                'relevance_score': 0,
                'match_quality': "None"
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

    # Create tabs for different views
    tab1, tab2, tab3 = st.tabs(["Analysis Results", "Visualizations", "Summary"])
    
    # Add filtering options in sidebar
    st.sidebar.header("Filter Options")
    min_relevance = st.sidebar.slider("Minimum Relevance Score", 0, 100, 0)
    match_quality_options = ["High", "Medium", "Low", "None"]
    selected_quality = st.sidebar.multiselect(
        "Match Quality", 
        match_quality_options,
        default=match_quality_options
    )
    
    # Apply filters
    filtered_df = recommendations_df[
        (recommendations_df['relevance_score'] >= min_relevance) & 
        (recommendations_df['match_quality'].isin(selected_quality))
    ]
    
    # Tab 1: Analysis Results
    with tab1:
        st.write("### Analysis Results")
        st.write(filtered_df)
        
        # Provide a download button for the recommendations
        csv = filtered_df.to_csv(index=False).encode('utf-8')
        st.download_button(
            label="Download Recommendations as CSV",
            data=csv,
            file_name='recommendations_output.csv',
            mime='text/csv',
        )
    
    # Tab 2: Visualizations
    with tab2:
        st.write("### Data Visualizations")
        
        # Visualization 1: Recommendation distribution
        st.subheader("Recommendation Distribution")
        recommendation_counts = filtered_df['recommendation'].value_counts().reset_index()
        recommendation_counts.columns = ['recommendation', 'count']
        
        # Create two columns for visualizations
        col1, col2 = st.columns(2)
        
        with col1:
            # Create Pie Chart for recommendation distribution using matplotlib
            fig1, ax1 = plt.subplots(figsize=(7, 5))
            labels = recommendation_counts['recommendation']
            sizes = recommendation_counts['count']
            
            # Create a list of colors for each unique recommendation
            colors = plt.cm.Paired(np.linspace(0, 1, len(recommendation_counts)))
            
            # Create pie chart
            wedges, texts, autotexts = ax1.pie(
                sizes, 
                labels=None,  # No labels on the pie itself
                autopct='%1.1f%%',
                shadow=False, 
                startangle=90,
                colors=colors
            )
            
            # Improve legibility of percentage text
            for autotext in autotexts:
                autotext.set_color('white')
                autotext.set_fontsize(9)
            
            # Add legend
            ax1.legend(
                wedges, 
                labels,
                title="Recommendation Types",
                loc="center left",
                bbox_to_anchor=(1, 0, 0.5, 1)
            )
            
            ax1.set_title('Recommendation Distribution')
            ax1.axis('equal')  # Equal aspect ratio ensures that pie is drawn as a circle
            st.pyplot(fig1)
        
        with col2:
            # Create a bar chart using Altair
            chart = alt.Chart(recommendation_counts).mark_bar().encode(
                x=alt.X('recommendation:N', title='Recommendation', sort='-y'),
                y=alt.Y('count:Q', title='Count'),
                color=alt.Color('recommendation:N', scale=alt.Scale(scheme='category10'))
            ).properties(
                title='Recommendation Counts'
            )
            st.altair_chart(chart, use_container_width=True)
        
        # Visualization 2: Match Quality Distribution
        st.subheader("Match Quality Distribution")
        match_quality_counts = filtered_df['match_quality'].value_counts().reset_index()
        match_quality_counts.columns = ['match_quality', 'count']
        
        # Create ordered categories for match quality
        quality_order = ['High', 'Medium', 'Low', 'None']
        match_quality_counts['match_quality'] = pd.Categorical(
            match_quality_counts['match_quality'], 
            categories=quality_order, 
            ordered=True
        )
        match_quality_counts = match_quality_counts.sort_values('match_quality')
        
        # Create a color scale for match quality
        color_scale = alt.Scale(
            domain=['High', 'Medium', 'Low', 'None'],
            range=['#1f77b4', '#2ca02c', '#ff7f0e', '#d62728']
        )
        
        # Create chart for match quality
        quality_chart = alt.Chart(match_quality_counts).mark_bar().encode(
            x=alt.X('match_quality:N', title='Match Quality', sort=quality_order),
            y=alt.Y('count:Q', title='Count'),
            color=alt.Color('match_quality:N', scale=color_scale)
        ).properties(
            title='Match Quality Distribution'
        )
        st.altair_chart(quality_chart, use_container_width=True)
        
        # Visualization 3: Relevance Score Distribution
        st.subheader("Relevance Score Distribution")
        
        # Create a histogram of relevance scores
        hist_chart = alt.Chart(filtered_df).mark_bar().encode(
            x=alt.X('relevance_score:Q', bin=alt.Bin(maxbins=20), title='Relevance Score'),
            y=alt.Y('count()', title='Count')
        ).properties(
            title='Distribution of Relevance Scores'
        )
        st.altair_chart(hist_chart, use_container_width=True)
        
        # Visualization 4: Average Position vs Relevance Score
        st.subheader("Average Position vs Relevance Score")
        
        scatter_chart = alt.Chart(filtered_df).mark_circle(size=60).encode(
            x=alt.X('avgpos:Q', title='Average Position'),
            y=alt.Y('relevance_score:Q', title='Relevance Score'),
            color=alt.Color('match_quality:N', scale=color_scale),
            tooltip=['queries', 'avgpos', 'relevance_score', 'match_quality', 'recommendation']
        ).properties(
            title='Relevance Score vs Average Position'
        ).interactive()
        
        st.altair_chart(scatter_chart, use_container_width=True)
    
    # Tab 3: Summary Statistics
    with tab3:
        st.write("### Summary Statistics")
        
        # Create a summary dataframe
        summary_data = {
            'Metric': [
                'Total Queries Analyzed',
                'Queries with Existing Content Match',
                'Queries Needing New Content',
                'Average Relevance Score',
                'High Quality Matches',
                'Medium Quality Matches',
                'Low Quality Matches',
                'No Matches'
            ],
            'Value': [
                len(filtered_df),
                len(filtered_df[filtered_df['recommendation'] != "Create new content"]),
                len(filtered_df[filtered_df['recommendation'] == "Create new content"]),
                f"{filtered_df['relevance_score'].mean():.2f}",
                len(filtered_df[filtered_df['match_quality'] == "High"]),
                len(filtered_df[filtered_df['match_quality'] == "Medium"]),
                len(filtered_df[filtered_df['match_quality'] == "Low"]),
                len(filtered_df[filtered_df['match_quality'] == "None"])
            ]
        }
        
        summary_df = pd.DataFrame(summary_data)
        st.table(summary_df)
        
        # Display percentage of queries matched vs not matched
        col1, col2 = st.columns(2)
        
        with col1:
            match_percent = (len(filtered_df[filtered_df['recommendation'] != "Create new content"]) / len(filtered_df)) * 100
            not_match_percent = 100 - match_percent
            
            fig, ax = plt.subplots(figsize=(5, 5))
            ax.pie(
                [match_percent, not_match_percent],
                labels=['Matched', 'Not Matched'],
                autopct='%1.1f%%',
                colors=['#1f77b4', '#d62728'],
                startangle=90
            )
            ax.set_title('Percentage of Queries Matched')
            ax.axis('equal')
            st.pyplot(fig)
        
        with col2:
            # Display the top recommended URLs
            if 'recommendation' in filtered_df.columns and any(filtered_df['recommendation'] != "Create new content"):
                # Extract URL from recommendation column
                url_df = filtered_df[filtered_df['recommendation'] != "Create new content"].copy()
                url_df['URL'] = url_df['recommendation'].str.replace('Add to ', '')
                url_counts = url_df['URL'].value_counts().reset_index()
                url_counts.columns = ['URL', 'Count']
                
                st.write("### Top Recommended URLs")
                st.write(url_counts.head(10))
else:
    st.write("Please upload both content and queries CSV files to start the analysis.")
    
    # Display instructions when no files are uploaded
    st.markdown("""
    ### How to Use This App
    
    This app helps you analyze your content and identify keyword opportunities by matching queries with the most relevant content pages.
    
    **Instructions:**
    
    1. **Upload a Content CSV file** that contains at least two columns:
       - `Content`: The text content of each page
       - `URL`: The URL of the content page
    
    2. **Upload a Queries CSV file** that contains at least two columns:
       - `queries`: The search query terms
       - `avgpos`: The average position in search results
    
    3. **Review the analysis** which will:
       - Match queries to the most relevant content pages based on both content and URL
       - Prioritize pages where query terms appear in the URL
       - Suggest when to create new content vs. enhance existing pages
       - Provide visualizations to help understand the results
    
    4. **Use the sidebar filters** to refine your view of the recommendations
    
    5. **Download the recommendations** for implementation in your content strategy
    """)
