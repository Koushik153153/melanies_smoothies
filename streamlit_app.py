import requests
import streamlit as st
from snowflake.snowpark.functions import col
from snowflake.snowpark import Row

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

# ---------------- Validation Messages ----------------
if ingredients_list and not name_on_order:
    st.warning("Please enter a name for your Smoothie.")

elif name_on_order and not ingredients_list:
    st.warning("Please select at least one ingredient.")

# ---------------- Submit Order ----------------
elif ingredients_list and name_on_order:
    ingredients_string = ", ".join(ingredients_list)

    if st.button("Submit Order"):
        new_order_df = session.create_dataframe(
            [
                Row(
                    NAME_ON_ORDER=name_on_order,
                    INGREDIENTS=ingredients_string
                )
            ]
        )

        new_order_df.write.mode("append").save_as_table(
            "SMOOTHIES.PUBLIC.ORDERS",
            column_order="name"
        )

        st.success(f"Your Smoothie is ordered, {name_on_order}! ✅")

st.header("🥗 Smoothie Nutrition Info")

smoothieroot_response = requests.get(
    "https://my.smoothieroot.com/api/fruit/watermelon"
)

st.text(smoothieroot_response)

