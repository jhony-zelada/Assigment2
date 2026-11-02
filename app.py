import os

import pandas as pd
import plotly.express as px
import streamlit as st

from labeler import label_comment

# ---- Settings ----------------------------------------------------------
TITLE = "RoadGuard Car Insurance"
LOGO = "logo.png"
CSV_FILE = "feedback.csv"
FEATURES = ["price", "coverage", "quality of service", "other"]
COLORS = {
    "price":              "#F58518",
    "coverage":           "#4C78A8",
    "quality of service": "#2BB38A",
    "other":              "#B0B0B0",
}
LOW_RATING = 2
REQUIRED_COLS = ["comment", "rating", "feature"]
# ------------------------------------------------------------------------


def load_feedback(path: str) -> pd.DataFrame:
    """Read feedback.csv and return it with the current schema.

    Handles legacy files written by the old positive/negative labeler:
    - renames `label` -> `feature`
    - adds any missing required column
    - maps any unknown feature to "other"
    - coerces rating to a number
    """
    if not os.path.exists(path):
        return pd.DataFrame(columns=REQUIRED_COLS)

    try:
        raw = pd.read_csv(path)
    except pd.errors.EmptyDataError:
        return pd.DataFrame(columns=REQUIRED_COLS)

    raw = raw.rename(columns={"label": "feature"})  # legacy pizza schema

    for col in REQUIRED_COLS:
        if col not in raw.columns:
            raw[col] = pd.NA
    raw = raw[REQUIRED_COLS].copy()

    raw["comment"] = raw["comment"].astype("string")
    raw["rating"]  = pd.to_numeric(raw["rating"], errors="coerce")
    raw["feature"] = (raw["feature"].fillna("other").astype("string")
                                      .str.strip().str.lower())
    raw.loc[~raw["feature"].isin(FEATURES), "feature"] = "other"

    # Drop fully blank rows (a half-written CSV from a killed process).
    raw = raw.dropna(subset=["comment", "rating"], how="all").reset_index(drop=True)
    return raw


st.set_page_config(page_title=TITLE, page_icon=LOGO, layout="wide")
if os.path.exists(LOGO):
    st.image(LOGO, width=120)
st.title(TITLE)
st.caption("Returning customers tell us why they came back. "
           "The app labels the reason and the owner analyzes it later.")

# ---- Sidebar: maintenance ---------------------------------------------
with st.sidebar:
    st.header("Maintenance")
    if st.button("🗑️ Start fresh (delete feedback.csv)", use_container_width=True):
        if os.path.exists(CSV_FILE):
            os.remove(CSV_FILE)
        st.success("feedback.csv deleted. The app now starts from an empty table.")
        st.rerun()
    st.caption("Use this if the CSV was created by an previous analysis.")

# ---- Load ------------------------------------------------------------------
df = load_feedback(CSV_FILE)

tab_customer, tab_owner = st.tabs(
    ["Returning customer: share your reason", "Owner: analyze the reasons"]
)

# ---- Customer tab ----------------------------------------------------------
with tab_customer:
    st.subheader("Why did you come back to us?")
    st.caption(
        "One short sentence is enough — for example, "
        "\"your premium was the cheapest I found this year\"."
    )
    with st.form("feedback_form", clear_on_submit=True):
        comment = st.text_area("Your reason")
        stars = st.feedback("stars")
        submitted = st.form_submit_button("Send")

    if submitted:
        if not comment.strip() or stars is None:
            st.error("Please write a short reason and choose a star rating.")
        else:
            feature = label_comment(comment.strip())
            row = pd.DataFrame([{
                "comment": comment.strip(),
                "rating":  stars + 1,
                "feature": feature,
            }])
            # Append to the normalized table and write it back.
            updated = pd.concat([df, row], ignore_index=True)
            updated.to_csv(CSV_FILE, index=False)
            df = load_feedback(CSV_FILE)
            st.success("Thank you — that helps us serve you better.")
            st.caption(f"Filed under: **{feature}**")

# ---- Owner tab -------------------------------------------------------------
with tab_owner:
    if df.empty:
        st.info("No feedback yet. Switch to the customer tab to add the first reason.")
    else:
        flag = (df["feature"] == "other") | (df["rating"] <= LOW_RATING)

        real = df[df["feature"] != "other"]
        if not real.empty:
            top_feature = real["feature"].value_counts().idxmax()
            top_share   = real["feature"].value_counts(normalize=True).iloc[0]
        else:
            top_feature, top_share = "other", 0.0

        st.subheader("What makes customers come back?")
        m1, m2, m3, m4 = st.columns(4)
        m1.metric("Reasons", len(df))
        m2.metric("Top reason", f"{top_feature} ({top_share:.0%})")
        m3.metric("Average stars", f"{df['rating'].mean():.1f}")
        m4.metric("Read carefully", int(flag.sum()),
                  help="Unclassified reasons, or a rating of 2 or less.")

        col1, col2 = st.columns(2)

        with col1:
            st.caption("Reasons by feature")
            counts = (df["feature"].value_counts()
                        .rename_axis("feature").reset_index(name="count"))
            fig = px.bar(counts, x="feature", y="count", color="feature", text="count",
                         color_discrete_map=COLORS,
                         category_orders={"feature": FEATURES})
            fig.update_layout(showlegend=False, xaxis_title=None, yaxis_title="Reasons")
            st.plotly_chart(fig, use_container_width=True)

        with col2:
            st.caption("Average stars by feature")
            avg = df.groupby("feature")["rating"].mean().round(1).reset_index()
            fig = px.bar(avg, x="feature", y="rating", color="feature", text="rating",
                         color_discrete_map=COLORS, range_y=[0, 5],
                         category_orders={"feature": FEATURES})
            fig.update_layout(showlegend=False, xaxis_title=None, yaxis_title="Average stars")
            st.plotly_chart(fig, use_container_width=True)

        st.caption("Reasons by feature and star rating")
        by = df.groupby(["rating", "feature"]).size().reset_index(name="count")
        fig = px.bar(by, x="rating", y="count", color="feature",
                     color_discrete_map=COLORS,
                     category_orders={"feature": FEATURES})
        fig.update_layout(xaxis_title="Stars", yaxis_title="Reasons", legend_title_text=None)
        st.plotly_chart(fig, use_container_width=True)

        st.subheader("Read these carefully")
        st.caption(
            "Either the comment could not be classified, or the customer gave "
            "2 stars or fewer — worth a follow-up even though they came back."
        )
        st.dataframe(df[flag], hide_index=True, use_container_width=True)

        with st.expander("All feedback"):
            st.dataframe(df, hide_index=True, use_container_width=True)
        st.download_button("Download CSV", df.to_csv(index=False),
                           file_name="feedback.csv")
        st.caption("On the free Streamlit Cloud, the saved file can disappear "
                   "when the app restarts. Download your CSV to keep it.")
