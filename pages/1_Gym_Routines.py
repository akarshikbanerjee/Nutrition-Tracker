import streamlit as st
import pandas as pd
import os

GYM_FILE = "gym_data.csv"

def load_gym_data():
    if os.path.exists(GYM_FILE):
        df = pd.read_csv(GYM_FILE)
        return df
    else:
        return pd.DataFrame({"routine": []})

def save_gym_data(df):
    df.to_csv(GYM_FILE, index=False)

st.set_page_config(page_title="Gym Routine", page_icon="🏋️")

st.title("🏋️ Your Gym Routine Library")

df = load_gym_data()

st.markdown("### Add or update your gym routine")

routine_text = st.text_area(
    "Paste your routine here:",
    height=300,
    placeholder="Write or paste your workout routine here..."
)

if st.button("Save Routine"):
    df = pd.DataFrame({"routine": [routine_text]})
    save_gym_data(df)
    st.success("Routine saved!")

st.markdown("---")
st.markdown("### Your current saved routine:")

df = load_gym_data()

if df.empty or df["routine"][0].strip() == "":
    st.info("No routine saved yet.")
else:
    st.code(df["routine"][0])
