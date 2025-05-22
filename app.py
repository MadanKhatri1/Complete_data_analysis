import numpy as np
import pandas as pd
import streamlit as st
import matplotlib.pyplot as plt


st.set_page_config(layout="wide",page_title="Startup Funding Analysis",page_icon=":money_with_wings:")
# Initialize session state for button and investor
if 'show_investor_details' not in st.session_state:
    st.session_state.show_investor_details = False
if 'selected_investor' not in st.session_state:
    st.session_state.selected_investor = None

# Load the data
df = pd.read_csv('data/cleaned_data.csv')

# Standardize column names
df.columns = [
    'Date',
    'Startup Name',
    'Vertical',
    'SubVertical',
    'City Location',
    'Investors',
    'Round',
    'Amount',
    'Startup Names',
    'Industries',
    'Funding Rounds',
    'Investment Amount',
    'Valuation',
    'Number of Investors',
    'Country',
    'Year Founded',
    'Growth Rate (%)'
]

df['Date']=pd.to_datetime(df['Date'], dayfirst=True,errors='coerce')
df['Year']=df['Date'].dt.year

# Process unique startups
unique_items = []
for column in ['Startup Name', 'Startup Names']:
    unique_items.extend([str(x) for x in df[column].dropna().unique().tolist() if x is not None])
sorted_unique_items = sorted(unique_items)

# Process investors, skipping first two
investors = sorted(
    set(
        investor.strip()
        for investor in df['Investors'].dropna().str.split(',').explode()
        if investor.strip()
    )
)[2:] or ['No investors available']


def load_overall_analysis():
    # st.title("Overall Analysis")
    def convert_to_np(dollar):
        npr=dollar*136
        return npr/10000000

    st.write("Amount is in Crores")
    df['Investment Amount']=df['Investment Amount'].apply(convert_to_np)
    df['Investment Amount'].sort_values(ascending=False)
    
    column1,column2,column3=st.columns(3)   
    
    with column1:
        st.subheader("Most Invested Field")
        df1 = pd.read_csv("data/global_data.csv")
        df2 = pd.read_csv("data/startup_funding_india.csv")

        # Standardize amount columns
        if 'Amount in USD' in df2.columns:
            df2.rename(columns={'Amount in USD': 'Investment Amount (USD)'}, inplace=True)

        # Convert amount columns to numeric, handling comma-separated values
        df1['Investment Amount (USD)'] = pd.to_numeric(df1['Investment Amount (USD)'].astype(str).str.replace(',', ''), errors='coerce')
        df2['Investment Amount (USD)'] = pd.to_numeric(df2['Investment Amount (USD)'].astype(str).str.replace(',', ''), errors='coerce')

        df1['Field'] = df1['Industry']  # For the global data
        df2['Field'] = df2['Industry Vertical']  # For the India data

        data = pd.concat([df1, df2], axis=0)

        most_invseted_field=data.groupby('Field')['Investment Amount (USD)'].sum().sort_values(ascending=False)
        
        st.metric(label="Most Invested Field",value=most_invseted_field.index[0])
        st.metric(label="It's Investment Amount",value=str(most_invseted_field[1])+" Cr")
        
    
    with column2:
        st.subheader("Most Invested Country")
        df2['City']=df2['City  Location']
        df1['City']=df1['Country']
        data=pd.concat([df1,df2],axis=0)
        
        most_invested_country=data.groupby('City')['Investment Amount (USD)'].sum().sort_values(ascending=False)
        
        st.metric(label="Most Invested Country",value=most_invested_country.index[0])
        
        st.metric(label="It's Investment Amount",value=str(most_invested_country[1])+" Cr")
        
        
    with column3:
        st.subheader("Most Invested Startup")
        # st.dataframe(data['Startup Name'][5000:])
        most_invested_startup=data.groupby('Startup Name')['Investment Amount (USD)'].sum().sort_values(ascending=False)
        
        st.metric(label="Most Invested Startup",value=most_invested_startup.index[0])
        st.metric(label="It's Investment Amount",value=str(most_invested_startup[1])+" Cr")
        
    col1,col2=st.columns(2)
    
    with col1:
        st.header("Overall Startup Funded by Year")
        overall_trend=df1.groupby(df1['Year Founded'])['Startup Name'].count()
        plt.figure(figsize=(10, 6))
        plt.plot(overall_trend.index, overall_trend.values, marker='o')  # Line plot with markers
        plt.title('Number of Startups Founded by Year')
        plt.xlabel('Year Founded')
        plt.ylabel('Number of Startups')
        plt.grid(True)

        # Display the plot in Streamlit
        st.pyplot(plt)
    
    with col2:
        st.header("Startup Funded by Country")
        dfr1=pd.read_csv("data/global_data.csv")
        dfr2=pd.read_csv("data/startup_funding_india.csv")
        dfr2['City/Country']=dfr2['City  Location']
        dfr1['City/Country']=dfr1['Country']
        dfr=pd.concat([dfr1,dfr2],axis=0)

        country_investment=dfr.groupby("City/Country")['Investment Amount (USD)'].sum().sort_values(ascending=False).head(10)
        plt.figure(figsize=(10, 6))
        plt.bar(country_investment.index, country_investment.values)
        plt.title('Investment Amount by Country')
        plt.xlabel('Country')
        plt.ylabel('Investment Amount (USD)')
        plt.grid(True)
        st.pyplot(plt)
        
        
        
        
# Investor details function with exact matching
def investor_details(investor):
    st.title(investor)
    st.subheader("Most Recent Investments")

    # Prepare data (ensure types are correct, this might be redundant if done globally but safe)
    # df['Date'] = pd.to_datetime(df['Date'], errors='coerce') # Already done globally with dayfirst=True
    df['Amount'] = pd.to_numeric(df['Amount'], errors='coerce').fillna(0)

    # Filter for the selected investor ONCE
    investor_df_filtered = df[df['Investors'].str.split(',', expand=True).apply(
        lambda x: x.str.strip().eq(investor), axis=1
    ).any(axis=1)]

    # Display Most Recent Investments table
    recent_investments_df = investor_df_filtered[
        ['Date', 'Startup Name', 'Vertical', 'City Location', 'Round', 'Amount']
    ].sort_values(by='Date', ascending=False)

    st.write("Amount is in Crores")
    if not recent_investments_df.empty:
        st.dataframe(recent_investments_df.head())
    else:
        st.write("No recent investments found for this investor.")
        st.dataframe(pd.DataFrame(
            columns=['Date', 'Startup Name', 'Vertical', 'City Location', 'Round', 'Amount']
        ))

    st.subheader("Biggest Investment Analysis")
    col1, col2 = st.columns(2) # Using conventional col1, col2

    with col1: # Pie chart for Vertical distribution
        if not investor_df_filtered.empty:
            vertical_sums = investor_df_filtered[investor_df_filtered['Amount'] > 0].groupby('Vertical')['Amount'].sum().sort_values(ascending=False)
            if not vertical_sums.empty:
                top_4 = vertical_sums.head(4)
                others_sum = vertical_sums.iloc[4:].sum()
                if others_sum > 0:
                    top_4_with_others = pd.concat([top_4, pd.Series(others_sum, index=['Others'], name='Amount')])
                else:
                    top_4_with_others = top_4

                fig_pie, ax_pie = plt.subplots()
                colors = plt.cm.Paired(range(len(top_4_with_others)))
                explode_values = [0.1 if idx == len(top_4_with_others) - 1 and 'Others' in top_4_with_others.index else 0 for idx in range(len(top_4_with_others))]
                ax_pie.pie(
                    top_4_with_others,
                    labels=top_4_with_others.index,
                    autopct=lambda p: f'{p:.1f}%' if p > 5 else '',
                    startangle=90,
                    colors=colors,
                    explode=explode_values
                )
                ax_pie.set_title(f'Investment Distribution by Vertical') # Investor name already in main title
                ax_pie.axis('equal')
                st.pyplot(fig_pie)
            else:
                st.write("No vertical investment data found.")
        else:
            st.write("No investment data for this investor.")


    with col2: # Bar chart for top investments by Startup Name
        if not investor_df_filtered.empty:
            big_df = investor_df_filtered.groupby('Startup Name').agg(
                {'Amount': 'sum', 'Date': 'max'}
            ).sort_values(by='Amount', ascending=False)

            if not big_df.empty:
                big_df_top5 = big_df.head()
                fig_bar_startup, ax_bar_startup = plt.subplots()
                ax_bar_startup.bar(big_df_top5.index, big_df_top5['Amount'])
                ax_bar_startup.set_xticklabels(big_df_top5.index, rotation=45, ha="right")
                ax_bar_startup.set_ylabel('Amount in Crores')
                ax_bar_startup.set_title(f'Top Startups by Investment Amount')
                plt.tight_layout()
                st.pyplot(fig_bar_startup)
                # Display dataframe for this section below the plot if needed
                # st.dataframe(big_df.head()) # Moved this display further down
            else:
                st.write("No startup investment data found.")
        else:
            st.write("No investment data for this investor.") # Redundant if already handled above col1

    # Display DataFrame for biggest investments (by startup)
    if not investor_df_filtered.empty:
        big_df_for_table = investor_df_filtered.groupby('Startup Name').agg(
            {'Amount': 'sum', 'Date': 'max'}
        ).sort_values(by='Amount', ascending=False)
        if not big_df_for_table.empty:
            st.write("Top Investments by Startup:")
            st.dataframe(big_df_for_table.head())
        # else: # Covered by check on big_df above for the plot
            # st.write("No investment data found for this investor.")
            # st.dataframe(pd.DataFrame(columns=['Date', 'Startup Name','Amount'])) # Redundant empty frame
    # else: # Covered by initial check on investor_df_filtered

    # Show Full Raw Data Checkbox
    if st.checkbox("Show Full raw data for this investor"):
        st.write("Raw data for this investor:")
        raw_data_cols = ['Date', 'Startup Name', 'Vertical', 'City Location', 'Investors', 'Round', 'Amount'] # More comprehensive
        if not investor_df_filtered.empty:
            st.dataframe(investor_df_filtered[raw_data_cols])
        else:
            st.write("No data found for this investor.")

    st.subheader(f"Further Analysis for {investor}") # General subheader for city and year plots

    # Use conventional column names: column1, column2
    column_city, column_year = st.columns(2)

    with column_city:
        st.markdown("##### Investments by City")
        if not investor_df_filtered.empty:
            # Ensure 'Year' column exists if needed here, though it's used for the year plot
            # df['Year'] = df['Date'].dt.year # This should be done globally once
            city_data = investor_df_filtered.groupby('City Location')['Amount'].sum().sort_values(ascending=False).head(10) # Top 10 cities

            if not city_data.empty:
                fig_city, ax_city = plt.subplots(figsize=(10, 6))
                ax_city.bar(city_data.index, city_data.values)
                ax_city.set_title(f'Investment Distribution by City (Top 10)')
                ax_city.set_ylabel('Amount in Crores')
                ax_city.set_xticklabels(city_data.index, rotation=45, ha="right")
                plt.tight_layout()
                st.pyplot(fig_city)
            else:
                st.write(f"No city investment data found for {investor}.")
        else:
            st.write(f"No investment data for {investor} to analyze by city.")

    with column_year:
        st.markdown("##### Investments Over Years")
        if not investor_df_filtered.empty:
            # df['Year'] = df['Date'].dt.year # This must be available from global scope
            year_data = investor_df_filtered.groupby('Year')['Amount'].sum()

            if not year_data.empty and year_data.index.notna().any(): # Ensure there are non-NA years
                fig_year, ax_year = plt.subplots(figsize=(10, 6))
                year_data.plot(kind='line', ax=ax_year, marker='o') # Line plot is common for time series
                ax_year.set_title(f'Investment Trend Over Years')
                ax_year.set_ylabel('Total Amount in Crores')
                ax_year.set_xlabel('Year')
                ax_year.set_xticks(year_data.index.dropna().astype(int)) 
                ax_year.tick_params(axis='x', rotation=45)
                plt.grid(True, linestyle='--', alpha=0.7)
                plt.tight_layout()
                st.pyplot(fig_year)
            else:
                st.write(f"No yearly investment data (or valid years) found for {investor}.")
        else:
            st.write(f"No investment data for {investor} to analyze by year.")

# Main app logic
st.write("NOTE: The dataset used in this project contains some generic identifiers (e.g., Startup_4541, Startup_4542) for startup companies instead of their actual names.")


st.sidebar.title("Startup Funding Analysis")


option = st.sidebar.selectbox('Select One', ['Overall Analysis', 'Investor'])


if option == 'Overall Analysis':
    st.title('Overall Analysis')
    
    
    
    btn0=st.sidebar.button("Show Overall Analysis")
    
    if btn0:
        load_overall_analysis()

elif option == 'Startup':
    st.sidebar.selectbox('Select StartUp', sorted_unique_items)
    btn1 = st.sidebar.button("Find Startup Details")
    st.title('Startup Analysis')

else:
    st.title('Investor Analysis')
    investor = st.sidebar.selectbox('Select Investor', investors)
    btn2 = st.sidebar.button("Find Investor Details")

    # Update session state when button is clicked
    if btn2:
        st.session_state.show_investor_details = True
        st.session_state.selected_investor = investor

    # Always show investor details if the button was previously clicked
    if st.session_state.show_investor_details and st.session_state.selected_investor:
        investor_details(st.session_state.selected_investor)