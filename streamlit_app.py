import requests
import streamlit as st
from snowflake.snowpark.functions import col

# -------------------- UI --------------------
st.title("Customize Your Smoothie! 🥤")
st.write("Choose the fruits you want in your custom Smoothie!")

name_on_order = st.text_input("Name on Smoothie:")

# ---------------- Snowflake Connection ----------------
cnx = st.connection("snowflake")
session = cnx.session()

# ---------------- Fetch Fruit Options (FRUIT_NAME + SEARCH_ON) ----------------
fruit_df = (
    session.table("SMOOTHIES.PUBLIC.FRUIT_OPTIONS")
    .select(col("FRUIT_NAME"), col("SEARCH_ON"))
    .to_pandas()
)

# ---------------- Multiselect ----------------
ingredients_list = st.multiselect(
    "Choose up to 5 ingredients:",
    fruit_df["FRUIT_NAME"].tolist(),
    max_selections=5
)

# ---------------- Submit Order Button ----------------
submit = st.button("Submit Order")

if submit:
    if not name_on_order:
        st.warning("Please enter a name for your Smoothie.")
    elif not ingredients_list:
        st.warning("Please select at least one ingredient.")
    else:
        # IMPORTANT: space-separated (NO commas)
        ingredients_string = " ".join(ingredients_list)

        session.sql(
            """
            INSERT INTO SMOOTHIES.PUBLIC.ORDERS (NAME_ON_ORDER, INGREDIENTS)
            VALUES (%s, %s)
            """,
            params=[name_on_order, ingredients_string]
        ).collect()

        st.success(f"Your Smoothie is ordered, {name_on_order}! ✅")

# ---------------- Smoothie Nutrition Info ----------------
st.header("🥗 Smoothie Nutrition Info")

if ingredients_list:
    for fruit_chosen in ingredients_list:

        search_on = fruit_df.loc[
            fruit_df["FRUIT_NAME"] == fruit_chosen,
            "SEARCH_ON"
        ].iloc[0]

        st.subheader(f"{fruit_chosen} Nutrition Information")

        if not search_on:
            st.warning(f"Sorry, {fruit_chosen} is not in our database.")
            continue

        response = requests.get(
            f"https://my.smoothiefroot.com/api/fruit/{search_on}"
        )

        if response.status_code == 200:
            st.dataframe(response.json(), use_container_width=True)
        else:
            st.warning(f"Sorry, {fruit_chosen} is not in our database.")
