import requests
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

# ---------------- Fetch Fruit Options (FRUIT_NAME + SEARCH_ON) ----------------
fruit_df = (
    session.table("SMOOTHIES.PUBLIC.FRUIT_OPTIONS")
    .select(col("FRUIT_NAME"), col("SEARCH_ON"))
    .to_pandas()
)

# ---------------- Multiselect (user-friendly) ----------------
ingredients_list = st.multiselect(
    "Choose up to 5 ingredients:",
    fruit_df["FRUIT_NAME"].tolist(),
    max_selections=5
)

# ---------------- Smoothie Nutrition Info ----------------
st.header("🥗 Smoothie Nutrition Info")

for fruit_chosen in ingredients_list:
    # Lookup SEARCH_ON value
    search_term = fruit_df.loc[
        fruit_df["FRUIT_NAME"] == fruit_chosen,
        "SEARCH_ON"
    ].values[0]

    st.subheader(f"{fruit_chosen} Nutrition Information")

    response = requests.get(
        f"https://my.smoothiefroot.com/api/fruit/{search_term}"
    )

    if response.status_code == 200:
        st.dataframe(response.json(), use_container_width=True)
    else:
        st.warning(f"Sorry, {fruit_chosen} is not in our database.")
