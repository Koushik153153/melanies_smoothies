# Import python packages
import streamlit as st
from snowflake.snowpark.functions import col

# Write directly to the app
st.title("Customize Your Smoothie! 🥤")
st.write("Choose the fruits you want in your custom Smoothie!")

# Name input
name_on_order = st.text_input("Name on Smoothie:")
st.write("The name on Smoothie will be:", name_on_order)

# Snowflake connection (SnIS way)
cnx = st.connection("snowflake")
session = cnx.session()

# Get fruit options from Snowflake
fruit_df = session.table("smoothies.public.fruit_options").select(col("FRUIT_NAME"))

# ✅ Convert Snowpark DF → Python list
fruit_list = [row["FRUIT_NAME"] for row in fruit_df.collect()]

# Multiselect with max selections
ingredients_list = st.multiselect(
    "Choose up to 5 ingredients:",
    fruit_list,
    max_selections=5
)

# Build ingredients string
ingredients_string = ""
if ingredients_list:
    for fruit in ingredients_list:
        ingredients_string += fruit + " "

# Submit button
time_to_insert = st.button("Submit Order")

# Insert into Snowflake
if time_to_insert and ingredients_list:

    insert_stmt = f"""
        INSERT INTO smoothies.public.orders (ingredients, name_on_order)
        VALUES ('{ingredients_string}', '{name_on_order}')
    """

    session.sql(insert_stmt).collect()

    st.success(f"Your Smoothie is ordered, {name_on_order}!", icon="✅")
