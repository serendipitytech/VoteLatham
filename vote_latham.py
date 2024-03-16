import streamlit as st
import pandas as pd
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
    
    # Display table for count breakdown by race, gender, age range, and party
    if df is not None:
        # Replace race codes with race names
        df['Race'] = df['Race'].map(race_mapping)
        
        # Convert birth date to datetime
        df['Birth_Date'] = pd.to_datetime(df['Birth_Date'], errors='coerce')
        
        # Calculate age and age range
        df['Age'] = df['Birth_Date'].apply(calculate_age)
        df['Age_Range'] = df['Age'].apply(categorize_age)
        
        # Sidebar filters
        logo_url = "https://serendipitytech.s3.amazonaws.com/public/votelatham.png"
        st.sidebar.image(logo_url, width=300)
        st.sidebar.subheader("Filters")
        selected_status = st.sidebar.selectbox("Select Status", df['Voter_Status'].unique(), index=df['Voter_Status'].unique().tolist().index('ACT'))
        selected_race = st.sidebar.multiselect("Select Race", df['Race'].unique(), default=df['Race'].unique())
        selected_gender = st.sidebar.multiselect("Select Gender", df['Gender'].unique(), default=df['Gender'].unique())
        selected_age_ranges = st.sidebar.multiselect("Select Age Ranges", ["18-28", "29-40", "41-55", "56+"], default=["18-28", "29-40", "41-55", "56+"])
        
        # Dynamic elections selector with a maximum of 4 selections
        date_columns = [col for col in df.columns if col[0].isdigit()]
        default_selection = ['11/08/2022_GEN', '11/03/2020_GEN', '08/23/2022_PRI', '08/18/2020_PRI']
        selected_elections = st.sidebar.multiselect("Select Elections (Max 4)", date_columns, default=default_selection, key="elections")
        st.sidebar.write("This filter only applies to the voter history counts table")
        
        
        # Filter dataframe based on selected filters
        filtered_df = df[df['Race'].isin(selected_race) & df['Gender'].isin(selected_gender) & df['Age_Range'].isin(selected_age_ranges) & (df['Voter_Status'] == selected_status)]
        
        # Display table for count breakdown by race, gender, and party
        st.header("Voter Counts by Race, Gender, and Party")
        pivot_df = pd.pivot_table(filtered_df, index=['Race', 'Gender'], columns='Party', values='Voter_ID', aggfunc='count', fill_value=0)
        pivot_df['Total'] = pivot_df.sum(axis=1)
        pivot_df_sorted = pivot_df.sort_index(level=[0, 1])  # Sort by Race and Gender
        st.table(pivot_df_sorted)
        st.write('<style>tr:hover {background-color: #5aclee;}</style>', unsafe_allow_html=True)
        
        
        # Count of voters who voted in 0, 1, 2, 3, or all of the selected elections
        election_counts = {}
        for index, row in filtered_df.iterrows():
            key = (row['Race'], row['Gender'])
            if key not in election_counts:
                election_counts[key] = [0] * 5  # Initialize count to 0 for all elections
            count = sum(1 for election in selected_elections if row[election] in ['A', 'E', 'Y'])
            election_counts[key][count] += 1
        
        # Create DataFrame from election counts
        election_counts_df = pd.DataFrame(election_counts).T
        election_counts_df.index.names = ['Race', 'Gender']
        election_counts_df.columns = ['0 Elections', '1 Election', '2 Elections', '3 Elections', '4 Elections']
        
        # Sort the DataFrame by index
        election_counts_df_sorted = election_counts_df.sort_index(level=[0, 1])
        
        # Display DataFrame
        st.header("Voter History Counts")
        election_counts_df_sorted = election_counts_df.sort_index(level=[0, 1])
        st.table(election_counts_df_sorted)
        st.write('<style>tr:hover {background-color:#5ac1ee;}</style>', unsafe_allow_html=True)

if __name__ == "__main__":
    main()
