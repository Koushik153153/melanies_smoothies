import streamlit as st
import requests
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

# ---------------- Fetch Fruit Options ----------------
fruit_df = (
    session.table("SMOOTHIES.PUBLIC.FRUIT_OPTIONS")
    .select(col("FRUIT_NAME"))
    .to_pandas()
)

# ---------------- Ingredients Selection ----------------
ingredients_list = st.multiselect(
    "Choose up to 5 ingredients:",
    fruit_df["FRUIT_NAME"].tolist(),
    max_selections=5
)

# ---------------- Nutrition Info ----------------
st.header("🥗 Smoothie Nutrition Info")

for fruit_chosen in ingredients_list:
    st.subheader(fruit_chosen)

    try:
        response = requests.get(
            f"https://my.smoothieroot.com/api/fruit/{fruit_chosen.lower()}"
        )

        if response.status_code == 200:
            st.dataframe(response.json(), use_container_width=True)
        else:
            st.warning(f"No nutrition data found for {fruit_chosen}")

    except Exception:
        st.error(f"Could not fetch data for {fruit_chosen}")
