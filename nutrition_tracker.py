import streamlit as st
import pandas as pd
import os
import json
from datetime import date

LOG_FILE = "nutrition_log.csv"
GOALS_FILE = "goals.json"
GYM_FILE = "gym_routine.txt"

# ---------- Data handling ----------

def load_data():
    if os.path.exists(LOG_FILE):
        df = pd.read_csv(LOG_FILE)
        df["date"] = pd.to_datetime(df["date"]).dt.date
        df["calories"] = df["calories"].astype(float)
        df["protein"] = df["protein"].astype(float)
        return df
    else:
        return pd.DataFrame(
            columns=["date", "meal_type", "food", "calories", "protein", "notes"]
        )

def save_data(df):
    df.to_csv(LOG_FILE, index=False)

def load_goals():
    if os.path.exists(GOALS_FILE):
        try:
            with open(GOALS_FILE, "r") as f:
                data = json.load(f)
            cal = float(data.get("calorie_goal", 2000))
            prot = float(data.get("protein_goal", 180))
            return cal, prot
        except Exception:
            return 2000.0, 180.0
    else:
        return 2000.0, 180.0

def save_goals(calorie_goal, protein_goal):
    data = {
        "calorie_goal": float(calorie_goal),
        "protein_goal": float(protein_goal),
    }
    with open(GOALS_FILE, "w") as f:
        json.dump(data, f)

def load_gym_routine():
    if os.path.exists(GYM_FILE):
        with open(GYM_FILE, "r") as f:
            return f.read()
    return ""

def save_gym_routine(text):
    with open(GYM_FILE, "w") as f:
        f.write(text)

# ---------- Page + Theme ----------

st.set_page_config(
    page_title="Nutrition & Gym Tracker",
    page_icon="💪",
    layout="wide"
)

# Soft theme styling
st.markdown(
    """
    <style>
    .stApp {
        background: radial-gradient(circle at top left, #eef2ff 0, #fdf2ff 40%, #ffffff 100%);
        font-family: -apple-system, BlinkMacSystemFont, system-ui, sans-serif;
    }

    [data-testid="stSidebar"] {
        background-color: #ffffff !important;
        border-right: 1px solid rgba(148, 163, 184, 0.3);
    }

    .card {
        background-color: #ffffff;
        padding: 1rem 1.2rem;
        border-radius: 1rem;
        box-shadow: 0 6px 18px rgba(15, 23, 42, 0.08);
        margin-bottom: 1rem;
        border: 1px solid rgba(148, 163, 184, 0.25);
    }
    .card-title {
        font-size: 0.8rem;
        font-weight: 600;
        color: #6366f1;
        text-transform: uppercase;
        letter-spacing: 0.12em;
        margin-bottom: 0.25rem;
    }
    .card-main {
        font-size: 1.6rem;
        font-weight: 700;
        color: #111827;
        margin-bottom: 0.15rem;
    }
    .card-sub {
        font-size: 0.9rem;
        color: #6b7280;
    }

    .pill-ok {
        display: inline-block;
        padding: 0.2rem 0.6rem;
        border-radius: 999px;
        background-color: #dcfce7;
        color: #15803d;
        font-size: 0.75rem;
        font-weight: 600;
    }
    .pill-warn {
        display: inline-block;
        padding: 0.2rem 0.6rem;
        border-radius: 999px;
        background-color: #fee2e2;
        color: #b91c1c;
        font-size: 0.75rem;
        font-weight: 600;
    }

    .form-card {
        background: linear-gradient(135deg, #eef2ff, #fdf2ff);
        padding: 1rem 1.2rem;
        border-radius: 1rem;
        border: 1px solid rgba(129, 140, 248, 0.4);
        box-shadow: 0 4px 14px rgba(129, 140, 248, 0.3);
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# ---------- Load data ----------

df = load_data()
default_cal_goal, default_prot_goal = load_goals()

# ---------- Sidebar: mode + goals ----------

st.sidebar.title("🏠 Menu")
page = st.sidebar.radio("Go to:", ["Nutrition", "Gym notebook"])

st.sidebar.markdown("---")
st.sidebar.title("🎯 Daily Targets")

# Use float for value and step to avoid mixed type error
calorie_goal = st.sidebar.number_input(
    "Calorie goal (kcal)",
    value=float(default_cal_goal),
    step=50.0
)
protein_goal = st.sidebar.number_input(
    "Protein goal (g)",
    value=float(default_prot_goal),
    step=5.0
)

# Persist goals every time (tiny file, no issue)
save_goals(calorie_goal, protein_goal)

st.sidebar.markdown("---")
st.sidebar.write("Focus on **showing up daily**, not perfection.")

# ---------- NUTRITION PAGE ----------

if page == "Nutrition":
    st.markdown("## 💪 Nutrition Check-In")
    st.write("Treat this like data collection for an experiment: simple, consistent, honest.")

    # ----- Log a meal -----

    st.markdown("### 🥗 Log a meal")

    with st.container():
        st.markdown('<div class="form-card">', unsafe_allow_html=True)
        with st.form(key="log_meal"):
            col1, col2 = st.columns(2)

            with col1:
                entry_date = st.date_input("Date", value=date.today())
                meal_type = st.selectbox(
                    "Meal type",
                    ["Breakfast", "Lunch", "Snack", "Dinner", "Other"]
                )
                food = st.text_input("Food / Drink")
            with col2:
                calories = st.number_input("Calories (kcal)", min_value=0.0, step=10.0)
                protein = st.number_input("Protein (g)", min_value=0.0, step=1.0)
                notes = st.text_area("Notes (optional)", height=80)

            submitted = st.form_submit_button("Add entry ✅")

            if submitted:
                if food.strip() == "":
                    st.warning("Please add at least a name for the item.")
                else:
                    # Allow 0 calories and 0 protein (e.g., americano)
                    new_row = {
                        "date": entry_date,
                        "meal_type": meal_type,
                        "food": food.strip(),
                        "calories": calories,
                        "protein": protein,
                        "notes": notes.strip(),
                    }
                    df = pd.concat([df, pd.DataFrame([new_row])], ignore_index=True)
                    save_data(df)
                    st.success("Logged. One more data point ✅")
        st.markdown("</div>", unsafe_allow_html=True)

    # ----- Daily summary -----

    st.markdown("### 📅 Today’s summary")

    selected_date = st.date_input("View date", value=date.today(), key="summary_date")
    today_df = df[df["date"] == selected_date]

    total_cals = float(today_df["calories"].sum()) if not today_df.empty else 0.0
    total_protein = float(today_df["protein"].sum()) if not today_df.empty else 0.0

    cal_diff = total_cals - float(calorie_goal)
    prot_diff = total_protein - float(protein_goal)

    cal_status = "Under target" if cal_diff <= 0 else "Over target"
    prot_status = "Under target" if prot_diff <= 0 else "Over target"

    cal_pill_class = "pill-ok" if cal_diff <= 0 else "pill-warn"
    prot_pill_class = "pill-ok" if prot_diff >= 0 else "pill-warn"

    col_a, col_b, col_c = st.columns(3)

    with col_a:
        st.markdown(
            f"""
            <div class="card">
                <div class="card-title">Calories</div>
                <div class="card-main">{int(total_cals)} kcal</div>
                <div class="card-sub">
                    Goal: {int(calorie_goal)} kcal<br>
                    <span class="{cal_pill_class}">{cal_status}</span>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with col_b:
        st.markdown(
            f"""
            <div class="card">
                <div class="card-title">Protein</div>
                <div class="card-main">{int(total_protein)} g</div>
                <div class="card-sub">
                    Goal: {int(protein_goal)} g<br>
                    <span class="{prot_pill_class}">{prot_status}</span>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with col_c:
        pct = (total_cals / float(calorie_goal) * 100) if calorie_goal > 0 else 0
        st.markdown(
            f"""
            <div class="card">
                <div class="card-title">Calorie goal completion</div>
                <div class="card-main">{pct:.1f}%</div>
                <div class="card-sub">
                    Aim for **most days** near 100%, not perfection.
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    st.write("#### Meals logged for this day")
    if today_df.empty:
        st.info("No entries for this date yet. Log one above to get started.")
    else:
        st.dataframe(today_df.sort_values(["date", "meal_type"]))

    # ----- History / trends -----

    st.markdown("### 📊 History")

    if df.empty:
        st.info("No data yet. Once you log a few days, your trends will appear here.")
    else:
        daily = df.groupby("date", as_index=False)[["calories", "protein"]].sum()
        st.write("Daily totals:")
        st.dataframe(daily.sort_values("date", ascending=False))

        st.write("Calories over time:")
        st.line_chart(daily.set_index("date")["calories"])

        st.write("Protein over time:")
        st.line_chart(daily.set_index("date")["protein"])

# ---------- GYM NOTEBOOK PAGE ----------

else:
    st.markdown("## 🏋️‍♂️ Gym routine notebook")
    st.write("Use this as a simple place to store and update your current programs.")

    if "gym_text" not in st.session_state:
        st.session_state["gym_text"] = load_gym_routine()

    st.markdown("### Current routine")
    st.text_area(
        "Edit your routine below:",
        key="gym_text",
        height=400,
    )

    if st.button("Save routine 💾"):
        save_gym_routine(st.session_state["gym_text"])
        st.success("Routine saved.")
