import streamlit as st
from snowflake.snowpark.functions import col

# -------------------- UI --------------------
st.title("Customize Your Smoothie! 🥤")
st.write("Choose the fruits you want in your custom Smoothie!")

name_on_order = st.text_input("Name on Smoothie:")

if name_on_order:
    st.write("The name on Smoothie will be:", name_on_order)

# ---------------- Snowflake Connection ----------------
cnx = st.connection("snowflake")
session = cnx.session()

# Fetch fruit options
fruit_df = (
    session.table("smoothies.public.fruit_options")
    .select(col("FRUIT_NAME"))
    .to_pandas()
)

# ---------------- Ingredients Selection ----------------
ingredients_list = st.multiselect(
    "Choose up to 5 ingredients:",
    fruit_df["FRUIT_NAME"].tolist(),
    max_selections=5
)

# ---------------- Order Submit ----------------
if ingredients_list and name_on_order:
    ingredients_string = ", ".join(ingredients_list)

    submit = st.button("Submit Order")

    if submit:
        insert_stmt = """
            INSERT INTO smoothies.public.orders (ingredients, name_on_order)
            VALUES (%s, %s)
        """
        session.sql(insert_stmt, params=[ingredients_string, name_on_order]).collect()

        st.success(f"Your Smoothie is ordered, {name_on_order}! ✅")

elif ingredients_list and not name_on_order:
    st.warning("Please enter a name for your Smoothie.")
