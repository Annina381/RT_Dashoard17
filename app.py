
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

st.set_page_config(layout="wide")

st.title("Eine Analyse von Artikeln von RT")

# -------------------------------------------------------------------
# Daten laden
# -------------------------------------------------------------------
@st.cache_data
def load_data():
    dataset_url = "https://github.com/polcomm-passau/computational_methods_python/raw/refs/heads/main/RT_D_Small.xlsx"
    df = pd.read_excel(dataset_url)
    df["date"] = pd.to_datetime(df["date"])
    return df

df = load_data()

reaction_columns = ["haha", "like", "wow", "angry", "sad", "love", "hug"]
engagement_columns = ["shares", "comments_num"]
all_metrics_columns = reaction_columns + engagement_columns

# -------------------------------------------------------------------
# Sidebar: Filter
# -------------------------------------------------------------------
st.sidebar.header("Filter")

search_term = st.sidebar.text_input("Suchbegriff", "grün")

st.sidebar.markdown("---")
st.sidebar.write("Anzahl aller Posts:", len(df))

# Filterbedingung
if search_term:
    search_condition = (
        df["text"].fillna("").str.contains(search_term, case=False, na=False)
        | df["fulltext"].fillna("").str.contains(search_term, case=False, na=False)
    )
else:
    search_condition = pd.Series([False] * len(df), index=df.index)

filtered_df_with_term = df[search_condition]
filtered_df_without_term = df[~search_condition]

# -------------------------------------------------------------------
# Kennzahlen oben anzeigen
# -------------------------------------------------------------------
col_a, col_b, col_c = st.columns(3)
with col_a:
    st.metric("Posts mit Suchbegriff", len(filtered_df_with_term))
with col_b:
    st.metric("Posts ohne Suchbegriff", len(filtered_df_without_term))
with col_c:
    perc = (len(filtered_df_with_term) / len(df) * 100) if len(df) > 0 else 0
    st.metric("Anteil mit Suchbegriff (%)", f"{perc:.1f}")

# -------------------------------------------------------------------
# Tabs für Layout
# -------------------------------------------------------------------
tab_time, tab_metrics, tab_data = st.tabs(
    ["📈 Zeitverlauf", "📊 Metriken", "📄 Daten"]
)

# -------------------------------------------------------------------
# Tab 1: Zeitverlauf
# -------------------------------------------------------------------
with tab_time:
    if not search_term:
        st.info("Bitte gib einen Suchbegriff in der Sidebar ein, um den Zeitverlauf zu sehen.")
    else:
        total_posts_per_day = df["date"].value_counts().sort_index()

        if not filtered_df_with_term.empty:
            filtered_posts_per_day = filtered_df_with_term["date"].value_counts().sort_index()

            # Prozent pro Tag
            percentage_per_day = (filtered_posts_per_day / total_posts_per_day) * 100
            percentage_per_day = percentage_per_day.fillna(0)

            st.subheader(f"Prozentualer Anteil der Artikel mit '{search_term}' im Zeitverlauf")

            fig, ax = plt.subplots(figsize=(12, 4))
            ax.plot(
                percentage_per_day.index,
                percentage_per_day.values,
                marker="o",
                linestyle="-",
                color="skyblue",
            )
            ax.set_title(f'Prozentualer Anteil der Posts pro Tag mit "{search_term}"')
            ax.set_xlabel("Datum")
            ax.set_ylabel("Anteil (%)")
            ax.grid(True, linestyle="--", alpha=0.4)
            ax.tick_params(axis="x", rotation=45)
            plt.tight_layout()
            st.pyplot(fig)
        else:
            st.warning(
                f"Keine Artikel gefunden, die '{search_term}' im Text oder Fulltext enthalten."
            )

# -------------------------------------------------------------------
# Tab 2: Metriken
# -------------------------------------------------------------------
with tab_metrics:
    st.subheader("Vergleich der durchschnittlichen Metriken")

    col1, col2, col3 = st.columns(3)

    # --- Links: Artikel mit Suchbegriff ---
    with col1:
        st.markdown(f"### Artikel mit '{search_term}'")
        if not filtered_df_with_term.empty:
            st.metric("Anzahl", len(filtered_df_with_term))
            mean_metrics_with_term = (
                filtered_df_with_term[all_metrics_columns].mean().round(2)
            )
            st.dataframe(mean_metrics_with_term.to_frame("Mittelwert"))
        else:
            st.info("Keine passenden Artikel gefunden.")

    # --- Mitte: Artikel ohne Suchbegriff ---
    with col2:
        st.markdown(f"### Artikel ohne '{search_term}'")
        if not filtered_df_without_term.empty:
            st.metric("Anzahl", len(filtered_df_without_term))
            mean_metrics_without_term = (
                filtered_df_without_term[all_metrics_columns].mean().round(2)
            )
            st.dataframe(mean_metrics_without_term.to_frame("Mittelwert"))
        else:
            st.info(
                "Alle Artikel enthalten den Suchbegriff oder es wurde kein Suchbegriff eingegeben."
            )

    # --- Rechts: Unterschiede ---
    with col3:
        st.markdown("### Unterschied (mit − ohne Suchbegriff)")
        if (
            search_term
            and not filtered_df_with_term.empty
            and not filtered_df_without_term.empty
        ):
            differences = mean_metrics_with_term - mean_metrics_without_term

            # Farben nach Vorzeichen
            colors = ["red" if x > 0 else "green" for x in differences.values]

            fig_diff, ax_diff = plt.subplots(figsize=(6, 4))
            sns.barplot(
                x=differences.values, y=differences.index, ax=ax_diff, palette=colors
            )
            ax_diff.set_title("Unterschiede der durchschnittlichen Metriken")
            ax_diff.set_xlabel("Differenz (mit − ohne)")
            ax_diff.set_ylabel("Metrik")
            ax_diff.grid(axis="x", linestyle="--", alpha=0.7)
            plt.tight_layout()
            st.pyplot(fig_diff)
        else:
            st.info(
                "Gib einen Suchbegriff ein und stelle sicher, "
                "dass es sowohl Artikel mit als auch ohne diesen Begriff gibt."
            )

# -------------------------------------------------------------------
# Tab 3: Daten
# -------------------------------------------------------------------
with tab_data:
    st.subheader("Originale Daten")

    view_choice = st.radio(
        "Welche Daten anzeigen?",
        ("Alle", "Nur mit Suchbegriff", "Nur ohne Suchbegriff"),
        horizontal=True,
    )

    if view_choice == "Alle":
        st.dataframe(df.head(100))
    elif view_choice == "Nur mit Suchbegriff":
        st.dataframe(filtered_df_with_term.head(100))
    else:
        st.dataframe(filtered_df_without_term.head(100))
