import streamlit as st
from snowflake.snowpark.functions import col

st.title("Customize Your Smoothie! 🥤")
st.write("Choose the fruits you want in your custom Smoothie!")

name_on_order = st.text_input("Name on Smoothie:")
st.write("The name on Smoothie will be:", name_on_order)

# Snowflake connection (SnIS-compatible)
cnx = st.connection("snowflake")
session = cnx.session()

my_dataframe = session.table("smoothies.public.fruit_options") \
                      .select(col("FRUIT_NAME")) \
                      .to_pandas()

ingredients_list = st.multiselect(
    "Choose up to 5 ingredients:",
    my_dataframe["FRUIT_NAME"].tolist(),
    max_selections=5
)

if ingredients_list:
    ingredients_string = " ".join(ingredients_list)

    if st.button("Submit Order"):
        insert_stmt = f"""
            INSERT INTO smoothies.public.orders (ingredients, name_on_order)
            VALUES ('{ingredients_string}', '{name_on_order}')
        """
        session.sql(insert_stmt).collect()
        st.success(f"Your Smoothie is ordered, {name_on_order}! ✅")
