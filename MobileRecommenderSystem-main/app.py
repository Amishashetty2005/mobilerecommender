import streamlit as st
import pickle
import pandas as pd
import random
from src.remove_ import remove

st.set_page_config(page_title="Mobile Recommender System", page_icon="📲", layout="wide")

# -------------------------------------------------------------
# LOAD DATA
# -------------------------------------------------------------
df = pickle.load(open('src/model/dataframe.pkl', 'rb'))
similarity = pickle.load(open('src/model/similarity.pkl', 'rb'))

remove()

# -------------------------------------------------------------
# CLEAN PRICE COLUMN
# -------------------------------------------------------------
df["price"] = df["price"].astype(str)
df["price"] = df["price"].str.replace("₹", "", regex=False)
df["price"] = df["price"].str.replace(",", "", regex=False)
df["price"] = df["price"].astype(int)

# -------------------------------------------------------------
# RECOMMENDATION FUNCTIONS
# -------------------------------------------------------------
def fetch_IMG(i):
    return df["imgURL"].iloc[i]

def recommend_same_series(selected_mobile):
    brand = selected_mobile.split()[0]  # REDMI, SAMSUNG, VIVO etc.
    series_df = df[df["name"].str.contains(brand)]
    
    # Best rating
    best_rating = series_df.sort_values("ratings", ascending=False).iloc[0]
    
    # Best value (rating per price)
    series_df = series_df.copy()
    series_df["value_metric"] = series_df["ratings"] / series_df["price"]
    best_value = series_df.sort_values("value_metric", ascending=False).iloc[0]
    
    return best_rating, best_value

def recommend_other_brands(selected_mobile):
    brand = selected_mobile.split()[0]
    other_df = df[~df["name"].str.contains(brand)]
    
    # Take top 10 similar by ratings
    other_df = other_df.sort_values("ratings", ascending=False).head(10)
    
    names = list(other_df["name"])
    imgs = list(other_df["imgURL"])
    ratings = list(other_df["ratings"])
    prices = list(other_df["price"])
    
    return names, imgs, ratings, prices

# -------------------------------------------------------------
# UI
# -------------------------------------------------------------
st.title("📱 Mobile Recommender System")
st.markdown("Choose a phone and get the best suggestions instantly! 🔥")

mobiles = df["name"].values
selected_mobile = st.selectbox("Select Mobile Name", mobiles)

if st.button("Recommend"):

    # ---------------- BEST IN SERIES ----------------
    best_rating, best_value = recommend_same_series(selected_mobile)

    st.markdown("---")
    st.markdown(f"## ⭐ BEST OPTIONS IN {selected_mobile.split()[0]} SERIES")
    st.markdown("### Compare by Rating and Value")

    colA, colB = st.columns(2)
    with colA:
        st.image(best_rating["imgURL"], use_container_width=True)
        st.markdown(
            f"### 🔥 Top Rating\n**{best_rating['name']}**  \n"
            f"⭐ Rating: **{best_rating['ratings']}**  \n"
            f"💰 Price: **₹{best_rating['price']}**"
        )
    with colB:
        st.image(best_value["imgURL"], use_container_width=True)
        st.markdown(
            f"### 💸 Best Value\n**{best_value['name']}**  \n"
            f"⭐ Rating: **{best_value['ratings']}**  \n"
            f"💰 Price: **₹{best_value['price']}**"
        )

    st.info(
        f"📌 **Why these are recommended?**  \n"
        f"- For **best rating**, choose **{best_rating['name']}**  \n"
        f"- For **best value**, choose **{best_value['name']}**"
    )

    # ---------------- OTHER BRANDS ----------------
    names, imgs, ratings, prices = recommend_other_brands(selected_mobile)

    st.markdown("---")
    st.markdown("## 🔍 Other Brands You Might Like")
    
    for i in range(len(names)):
        col = st.columns(1)
        with col[0]:
            st.image(imgs[i], use_container_width=True)
            st.markdown(
                f"**{names[i]}**  \n"
                f"⭐ Ratings: {ratings[i]}  \n"
                f"💰 Price: ₹{prices[i]}"
            )

st.markdown("---")
st.markdown("> Made with ❤️ by Kavana")
