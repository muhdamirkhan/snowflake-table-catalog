#from turtle import onclick
import streamlit as st
import snowflake.connector
import pandas as pd
#import streamlit.components.v1 as components
st.set_page_config(layout="wide")
# Initialize connection.
# Uses st.experimental_singleton to only run once.


@st.cache_resource
def init_connection():
    return snowflake.connector.connect(**st.secrets["snowflake"])

conn = init_connection()
cur = conn.cursor()

# Perform query.
# Uses st.experimental_memo to only rerun when the query changes or after 10 min.

@st.cache_data(ttl=600)
def run_query(query):
    with conn.cursor() as cur:
        cur.execute(query)

        dat = cur.fetchall()
        df = pd.DataFrame(dat, columns=[col[0] for col in cur.description])
        return df


df = run_query("""select * from INDICATORS.PUBLIC.CBSA_OVERALL_DATA""")

queried_data = df
location_list = queried_data['CBSA_NAME'].unique().tolist()
selected_locs = st.multiselect(label='Please choose a CBSA here', options=location_list)

if selected_locs == []:
    st.info('Data loading complete, lease select the CBSAs you need')

else:
    df_list = []
    for i in selected_locs:
        selected_data = queried_data[queried_data['CBSA_NAME'] == i]
        df_list.append(selected_data)
    
    df = pd.concat(df_list)

    column_names=df.columns

    # st.write(column_names)
    
    st.subheader("Output data")
    st.dataframe(df, use_container_width=True)

@st.cache_data
def convert_df(df):
    # IMPORTANT: Cache the conversion to prevent computation on every rerun
    return df.to_csv().encode('utf-8')

csv = convert_df(df)

st.download_button(
    label="Download data as CSV",
    data=csv,
    file_name='large_df.csv',
    mime='text/csv',
)
st.warning('All data will be downloaded if no option selected!')
    