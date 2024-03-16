import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime
import urllib.parse

# Define S3 URL
s3_url = "https://serendipitytech.s3.amazonaws.com/public/vote_latham_streamlit.txt"

# Race mappings
race_mapping = {
    1: "Other",
    2: "Other",
    6: "Other",
    7: "Other",
    9: "Other",
    3: "African American",
    4: "Hispanic",
    5: "White"
}

# Function to calculate age
def calculate_age(born):
    today = datetime.today()
    return today.year - born.year - ((today.month, today.day) < (born.month, born.day))

# Function to categorize age into ranges
def categorize_age(age):
    if age < 29:
        return "18-28"
    elif age < 41:
        return "29-40"
    elif age < 56:
        return "41-55"
    else:
        return "56+"


def load_data():
    # Load data from S3 into a DataFrame
    try:
        df = pd.read_csv(s3_url)
        return df
    except Exception as e:
        st.error(f"Error loading data: {e}")
        return None

def main():
    st.title("District 29 Voter Data")
    st.subheader("If you are on mobile, tap the small arrow icon in the top left corner to open the filter options")
    
    # Load data
    df = load_data()
    
    # Display treemap for count breakdown by race, gender, and party
    if df is not None:
        # Replace race codes with race names
        df['Race'] = df['Race'].map(race_mapping)
        
        # Convert birth date to datetime
        df['Birth_Date'] = pd.to_datetime(df['Birth_Date'], errors='coerce')
        
        # Calculate age and age range
        df['Age'] = df['Birth_Date'].apply(calculate_age)
        df['Age_Range'] = df['Age'].apply(categorize_age)
        
        # Sidebar filters
        logo_url = "https://votelatham.com/assets/images/logo/logo_lightbg.png"
        st.sidebar.image(logo_url, width=300)
        st.sidebar.subheader("Filters")
        selected_status = st.sidebar.selectbox("Select Status", df['Voter_Status'].unique(), index=df['Voter_Status'].unique().tolist().index('ACT'))
        selected_race = st.sidebar.multiselect("Select Race", df['Race'].unique(), default=df['Race'].unique())
        selected_gender = st.sidebar.multiselect("Select Gender", df['Gender'].unique(), default=df['Gender'].unique())
        selected_age_ranges = st.sidebar.multiselect("Select Age Ranges", ["18-28", "29-40", "41-55", "56+"], default=["18-28", "29-40", "41-55", "56+"])
        
        # Filter dataframe based on selected filters
        filtered_df = df[(df['Race'].isin(selected_race)) & 
                         (df['Gender'].isin(selected_gender)) & 
                         (df['Age_Range'].isin(selected_age_ranges)) & 
                         (df['Voter_Status'] == selected_status)]
        
        # Prepare data for treemap
        treemap_data = filtered_df.groupby(['Race', 'Gender', 'Party']).size().reset_index(name='Count')
        
        # Create treemap
        fig = px.treemap(treemap_data, path=['Race', 'Gender', 'Party'], values='Count', 
                         color='Count', color_continuous_scale='viridis', 
                         title='Voter Counts by Race, Gender, and Party')
        
        # Update layout
        fig.update_layout(margin=dict(t=50, l=0, r=0, b=0))
        
        # Display treemap
        st.plotly_chart(fig)

if __name__ == "__main__":
    main()
