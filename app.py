import streamlit as st
import pandas as pd
import os
from datetime import datetime
import plotly.express as px



# Logo centré
col1, col2, col3 = st.columns([1.5, 2, 1])
with col2:
    st.image("logo.png", width=200)

st.markdown(
    """<style>
    h1 {
        font-family: "calibri", serif;
        color: #f7dc6f;
        text-align: center;
        margin-bottom: 1rem;
    }
    </style>
    """,
    unsafe_allow_html=True
)

# Fichiers
matrice_path = "matrice.xlsx"
historique_path = "historique_adherents.xlsx"
#df_recompenses = pd.read_excel("matricecons.xlsx")
recompense_path = "matricecons.xlsx"


#df_recompenses = pd.read_excel("matricecons.ods", engine="odf")


#matrice
df_matrice = pd.read_excel(matrice_path, sheet_name="Feuil2")
df_matrice.columns = df_matrice.columns.str.strip()
#df_recompenses = pd.read_excel(recompense_path)
df_recompenses = pd.read_excel(recompense_path)
options = dict(zip(df_recompenses["Récompense"], df_recompenses["Coût en points"]))


# Créer historique if not
if not os.path.exists(historique_path):
    pd.DataFrame(columns=["Date", "Nom", "Activité", "Abonnement", "Fréquence", "Situation", "Points", "Points restants"]).to_excel(historique_path, index=False)

# side bar
#page = st.sidebar.selectbox("📋 Menu", ["Ajouter des points", "Historique des adhérents"])
#page = st.sidebar.selectbox("📋 Menu", ["Ajouter des points", "Historique des adhérents", "Consommer des points"])
page = st.sidebar.selectbox("📋 Menu", ["Ajouter des points", "Historique des adhérents", "Consommer des points", "📈 Tableau de bord"])


if page == "Ajouter des points":
    st.title("Attribution de Points")
    nom = st.text_input("Nom de l'adhérent")
    points = 0
    situation = None
    points_restants = 0

    Activité_options = ["-- Sélectionner --"] + sorted(df_matrice["Activité"].dropna().unique())
    Activité = st.selectbox("Activité", Activité_options)

    if Activité != "-- Sélectionner --":
        df_Activité = df_matrice[df_matrice["Activité"] == Activité]
        abonnement_options = ["-- Sélectionner --"] + sorted(df_Activité["Abonnement"].dropna().unique())
        abonnement = st.selectbox("Abonnement", abonnement_options)

        if abonnement != "-- Sélectionner --":
            df_abonnement = df_Activité[df_Activité["Abonnement"] == abonnement]

            # Gérer la fréquence seulement si elle existe
            freqs = df_abonnement["frequence"].dropna().unique()
            if len([f for f in freqs if str(f).strip()]) > 0:
                frequence_options = ["-- Sélectionner --"] + sorted([f for f in freqs if str(f).strip()])
                frequence = st.selectbox("Fréquence", frequence_options)
            else:
                frequence = None

            if frequence is None or frequence != "-- Sélectionner --":
                df_frequence = df_abonnement if frequence is None else df_abonnement[df_abonnement["frequence"] == frequence]

                # Gérer la situation seulement si elle existe
                situations = df_frequence["Situation"].dropna().unique()
                if len([s for s in situations if str(s).strip()]) > 0:
                    situation_options = ["-- Sélectionner --"] + sorted([s for s in situations if str(s).strip()])
                    situation = st.selectbox("Situation", situation_options)
                else:
                    situation = None

                if situation is None or situation != "-- Sélectionner --":
                    match = df_frequence if situation is None else df_frequence[df_frequence["Situation"] == situation]

                    if not match.empty:
                        points = int(match.iloc[0]["Points"])
                        points_restants = st.number_input("➕ Points restants de l'adhérent", min_value=0, step=1)

                        if situation is None or situation.lower() != "interruption":
                            points += points_restants
                        else:
                            points_restants = 0

                        st.success(f"✅ {points} points seront attribués à {nom}.")
                    else:
                        st.warning("⚠️ Aucune correspondance trouvée dans la matrice.")


    # Bouton de validation
    if st.button("Attribuer les points"):
        if (
            nom and
            Activité != "-- Sélectionner --" and
            abonnement != "-- Sélectionner --" and
            frequence != "-- Sélectionner --" and
            situation != "-- Sélectionner --"
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

    # date
    historique_df["Date"] = pd.to_datetime(historique_df["Date"], errors='coerce')

    # Filtres
    nom_filtre = st.text_input("🔍 Filtrer par nom")
    Activité_filtre = st.selectbox("🏋️ Filtrer par Activité", ["Tous"] + sorted(historique_df["Activité"].dropna().unique()))

    # cal
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
        filtré = filtré[(filtré["Date"].dt.date >= start_date) & (filtré["Date"].dt.date <= end_date)]

    st.dataframe(filtré, use_container_width=True)

    # Bouton de téléchargement
    with open(historique_path, "rb") as f:
        st.download_button(
            label="📥 Télécharger l'historique (.xlsx)",
            data=f,
            file_name="historique_adherents.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )

elif page == "Consommer des points":
    st.title("💳 Consommation de Points")

    historique_df = pd.read_excel(historique_path)
    historique_df["Date"] = pd.to_datetime(historique_df["Date"], errors='coerce')

    noms = sorted(historique_df["Nom"].dropna().unique())
    nom_choisi = st.selectbox("👤 Sélectionner un adhérent", ["-- Sélectionner --"] + list(noms))

    if nom_choisi != "-- Sélectionner --":
        adherent_data = historique_df[historique_df["Nom"] == nom_choisi]
        total_points = adherent_data["Points"].sum()
        total_consommés = adherent_data.get("Points consommés", pd.Series([0]*len(adherent_data))).sum()
        solde = total_points - total_consommés

        st.info(f"💰 Solde actuel : **{solde} points**")

        try:
            df_recompenses = pd.read_excel(recompense_path)
            options = dict(zip(df_recompenses["Récompense"], df_recompenses["Coût en points"]))
        except Exception as e:
            st.error(f"Erreur lors de la lecture des récompenses : {e}")
            options = {}

        if options:
            choix = st.selectbox("🎁 Choisir une récompense", ["-- Sélectionner --"] + list(options.keys()))
            if choix != "-- Sélectionner --":
                coût = options[choix]
                if coût > solde:
                    st.error("❌ Solde insuffisant pour cette récompense.")
                else:
                    if st.button("✅ Confirmer la consommation"):
                        nouvelle_ligne = {
                            "Date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                            "Nom": nom_choisi,
                            "Activité": "Récompense",
                            "Abonnement": "",
                            "Fréquence": "",
                            "Situation": "Consommation",
                            "Points": 0,
                            "Points restants": solde - coût,
                            "Récompense": choix,
                            "Points consommés": coût
                        }

                        for col in ["Récompense", "Points consommés"]:
                            if col not in historique_df.columns:
                                historique_df[col] = None

                        historique_df = pd.concat([historique_df, pd.DataFrame([nouvelle_ligne])], ignore_index=True)
                        historique_df.to_excel(historique_path, index=False)

                        st.success(f"🎉 {choix} attribué à {nom_choisi}. Nouveau solde : {solde - coût} points.")



elif page == "📈 Tableau de bord":
    st.title("📊 Tableau de bord de consommation")

    historique_df = pd.read_excel(historique_path)
    historique_df["Date"] = pd.to_datetime(historique_df["Date"], errors='coerce')

    # S'assurer que les colonnes existent
    for col in ["Récompense", "Points consommés"]:
        if col not in historique_df.columns:
            historique_df[col] = None

    consommations = historique_df[historique_df["Récompense"].notna() & historique_df["Points consommés"].notna()]

    if not consommations.empty:
        st.subheader("🎁 Répartition des récompenses")
        reward_counts = consommations["Récompense"].value_counts().reset_index()
        reward_counts.columns = ["Récompense", "Nombre"]

        fig_pie = px.pie(
            reward_counts,
            names="Récompense",
            values="Nombre",
            title="Répartition des consommations"
        )
        st.plotly_chart(fig_pie)

        st.subheader("📆 Points consommés par mois")
        consommations["Mois"] = consommations["Date"].dt.to_period("M").astype(str)
        monthly = consommations.groupby("Mois")["Points consommés"].sum().reset_index()

        fig_bar = px.bar(
            monthly,
            x="Mois",
            y="Points consommés",
            title="Points consommés par mois",
            text="Points consommés"
        )
        fig_bar.update_traces(textposition='outside')
        st.plotly_chart(fig_bar)

    else:
        st.info("ℹ️ Aucune consommation enregistrée pour le moment.")
