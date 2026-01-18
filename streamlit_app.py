import streamlit as st
import requests
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

# ---------------- Fetch Fruit Options (CHANGE 3) ----------------
fruit_df = (
    session.table("SMOOTHIES.PUBLIC.FRUIT_OPTIONS")
    .select(col("FRUIT_NAME"), col("SEARCH_ON"))
    .to_pandas()
)

# ---------------- Ingredients Selection (CHANGE 4) ----------------
ingredients_list = st.multiselect(
    "Choose up to 5 ingredients:",
    fruit_df["FRUIT_NAME"].tolist(),
    max_selections=5
)

# ---------------- Validation ----------------
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
            "SMOOTHIES.PUBLIC.ORDERS"
        )

        st.success(f"Your Smoothie is ordered, {name_on_order}! ✅")

# ---------------- Smoothie Nutrition Info (CHANGE 5) ----------------
st.header("🥗 Smoothie Nutrition Info")

for fruit_chosen in ingredients_list:
    search_term = fruit_df.loc[
        fruit_df["FRUIT_NAME"] == fruit_chosen,
        "SEARCH_ON"
    ].values[0]

    st.subheader(f"{fruit_chosen} Nutrition Information")

    try:
        response = requests.get(
            f"https://my.smoothiefroot.com/api/fruit/{search_term}"
        )

        if response.status_code == 200:
            st.dataframe(response.json(), use_container_width=True)
        else:
            st.warning(f"Sorry, {fruit_chosen} is not in our database.")

    except Exception:
        st.error(f"Could not fetch data for {fruit_chosen}")
