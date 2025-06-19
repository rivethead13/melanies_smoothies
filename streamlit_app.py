import streamlit as st
from snowflake.snowpark.functions import col
import requests
import pandas as pd

st.title(":cup_with_straw: Customize Your Smoothie :cup_with_straw:")
st.write("Choose the fruits you want in your custom Smoothie")

name_on_order = st.text_input('Name on Smoothie')
st.write("The name on the Smoothie will be:", name_on_order)

# Connect to Snowflake
cnx = st.connection("snowflake")
session = cnx.session()

# Load and cache fruit options
@st.cache_data
def load_fruit_options():
    df = session.table("smoothies.public.fruit_options").select(col('FRUIT_NAME'), col('SEARCH_ON'))
    return df.to_pandas()

pd_df = load_fruit_options()

# Use Pandas dataframe for multiselect options
fruit_options = pd_df['FRUIT_NAME'].tolist()
ingredients_list = st.multiselect(
    "Choose up to 5 ingredients",
    fruit_options,
    max_selections=5
)

ingredients_string += fruit_chosen + ' ' 

if ingredients_list:
    for fruit_chosen in ingredients_list:
        st.subheader(f"{fruit_chosen} Nutrition Information")
        search_on = pd_df.loc[pd_df['FRUIT_NAME'] == fruit_chosen, 'SEARCH_ON'].iloc[0]
        smoothiefroot_response = requests.get(f"https://my.smoothiefroot.com/api/fruit/{search_on}")
        st.dataframe(data=smoothiefroot_response.json(), use_container_width=True)

time_to_insert = st.button('Submit Order')

if time_to_insert:
    if not name_on_order or not ingredients_list:
        st.error("Please enter a name and select at least one ingredient.")
    else:
        my_insert_stmt = f"""
            INSERT INTO smoothies.public.orders(ingredients, name_on_order)
            VALUES ('{ingredients_string}', '{name_on_order}')
        """
        try:
            session.sql(my_insert_stmt).collect()
            st.success(f'Your Smoothie is ordered! {name_on_order}', icon="✅")
        except Exception as e:
            st.error(f"An error occurred: {e}")
