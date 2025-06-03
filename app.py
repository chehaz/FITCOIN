import streamlit as st
import pandas as pd
import os
from datetime import datetime

st.set_page_config(page_title="FitCoin", layout="centered")

# Logo centré
col1, col2, col3 = st.columns([1, 2, 1])
with col2:
    st.image("logo.png", width=350)


st.markdown(
    """<style>
    @media screen and (max-width: 768px) {
        .block-container {
            padding-left: 1rem !important;
            padding-right: 1rem !important;
        }
        h1 {
        font-size: 1.5rem !important;
        text-align: center !important;
        color: #f7dc6f !important;
        font-family: Calibri, sans-serif !important;
        margin-bottom: 1rem;
    }
    .title-centered {
        text-align: center;
        color: #f7dc6f;
        font-family: Calibri, sans-serif;
        font-size: 1.5rem;
        margin-bottom: 1.5rem;
    }
        .custom-title {
        font-family: 'Calibri', sans-serif;
        font-size: 2rem;
        color: #f7dc6f;
        text-align: center;
        margin-top: 1rem;
        margin-bottom: 1.5rem;
    }
        label, .stTextInput>div>div, .stSelectbox>div>div {
            font-size: 0.9rem !important;
        }
    }
    </style>
    """,
    unsafe_allow_html=True
)

# Fichiers
matrice_path = "matrice.xlsx"
historique_path = "historique_adherents.xlsx"

# Chargement matrice
df_matrice = pd.read_excel(matrice_path, sheet_name="Feuil2")
df_matrice.columns = df_matrice.columns.str.strip()

# Nettoyage des valeurs NaN
for col in ["Activité", "Abonnement", "frequence", "Situation"]:
    df_matrice[col] = df_matrice[col].fillna("")

# Créer fichier historique si besoin
if not os.path.exists(historique_path):
    pd.DataFrame(columns=["Date", "Nom", "Activité", "Abonnement", "Fréquence", "Situation", "Points", "Points restants"]).to_excel(historique_path, index=False)

# Menu
page = st.sidebar.selectbox("📋 Menu", ["Ajouter des points", "Historique des adhérents"])

if page == "Ajouter des points":
   # st.title("Attribution de Points")
    st.markdown("<h1>Attribution de Points</h1>", unsafe_allow_html=True)
    

    nom = st.text_input("Nom de l'adhérent")
    points = 0
    situation = None
    points_restants = 0

    # Activité (supprimer doublons)
    Activité_options = ["-- Sélectionner --"] + sorted(df_matrice["Activité"].unique())
    Activité_options = list(dict.fromkeys(Activité_options))  # supprime doublons tout en gardant l'ordre
    Activité = st.selectbox("Activité", Activité_options)

    if Activité != "-- Sélectionner --":
        df_Activité = df_matrice[df_matrice["Activité"] == Activité]
        abonnement_options = ["-- Sélectionner --"] + sorted(df_Activité["Abonnement"].unique())
        abonnement = st.selectbox("Abonnement", abonnement_options)

        if abonnement != "-- Sélectionner --":
            df_abonnement = df_Activité[df_Activité["Abonnement"] == abonnement]
            freqs = sorted([f for f in df_abonnement["frequence"].unique() if f.strip()])

            if freqs:
                frequence_options = ["-- Sélectionner --"] + freqs
                frequence = st.selectbox("Fréquence", frequence_options)
            else:
                frequence = ""

            if frequence != "-- Sélectionner --":
                df_frequence = df_abonnement[df_abonnement["frequence"] == frequence] if frequence else df_abonnement
                situations_disponibles = df_frequence["Situation"].dropna().unique()

                if len([s for s in situations_disponibles if s.strip()]) > 0:
                    situation_options = ["-- Sélectionner --"] + sorted([s for s in situations_disponibles if s.strip()])
                    situation = st.selectbox("Situation", situation_options)
                else:
                    situation = ""

                match = df_frequence if not situation else df_frequence[df_frequence["Situation"] == situation]

                if not match.empty:
                    points = int(match.iloc[0]["Points"])
                    points_restants = st.number_input("➕ Points restants de l'adhérent", min_value=0, step=1)

                    if situation.lower() != "interruption":
                        points += points_restants
                    else:
                        points_restants = 0

                    st.success(f"✅ {points} points seront attribués à {nom}.")
                #else:
                   # st.warning("⚠️ Aucune correspondance trouvée dans la matrice.")

    # Bouton de validation
    if st.button("Attribuer les points"):
        if (
            nom and
            Activité != "-- Sélectionner --" and
            abonnement != "-- Sélectionner --" and
            (frequence != "-- Sélectionner --" or not freqs)
        ):
            nouvelle_entree = pd.DataFrame([{
                "Date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "Nom": nom,
                "Activité": Activité,
                "Abonnement": abonnement,
                "Fréquence": frequence,
                "Situation": situation,
                "Points": points,
                "Points restants": points_restants
            }])
            historique_df = pd.read_excel(historique_path)
            historique_df = pd.concat([historique_df, nouvelle_entree], ignore_index=True)
            historique_df.to_excel(historique_path, index=False)
            st.success("👍 Points enregistrés avec succès !")
        else:
            st.error("❌ Merci de remplir tous les champs avant de valider.")

elif page == "Historique des adhérents":
    st.title("🕓 Historique des Points")
    historique_df = pd.read_excel(historique_path)

    historique_df["Date"] = pd.to_datetime(historique_df["Date"], errors='coerce')

   # nom_filtre = st.text_input("🔍 Filtrer par nom")
    nom_filtre = st.text_input("🔍 Filtrer par nom").strip()
    
    Activité_filtre = st.selectbox("🏋️ Filtrer par Activité", ["Tous"] + sorted(historique_df["Activité"].dropna().unique()))

    min_date = historique_df["Date"].min().date() if not historique_df["Date"].isna().all() else datetime.today().date()
    max_date = historique_df["Date"].max().date() if not historique_df["Date"].isna().all() else datetime.today().date()

    date_filtre = st.date_input(
        "📅 Filtrer par date",
        value=(min_date, max_date),
        min_value=min_date,
        max_value=max_date
    )

    filtré = historique_df.copy()

    if nom_filtre:
        filtré = filtré[filtré["Nom"].str.contains(nom_filtre, case=False, na=False)]
    if Activité_filtre != "Tous":
        filtré = filtré[filtré["Activité"] == Activité_filtre]

    if isinstance(date_filtre, tuple) and len(date_filtre) == 2:
        start_date, end_date = date_filtre
        filtré = filtré[
            (filtré["Date"] >= pd.to_datetime(start_date)) &
            (filtré["Date"] <= pd.to_datetime(end_date))
        ]

    st.dataframe(filtré, use_container_width=True)

    with open(historique_path, "rb") as f:
        st.download_button(
            label="📥 Télécharger l'historique (.xlsx)",
            data=f,
            file_name="historique_adherents.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
