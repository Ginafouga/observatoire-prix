import streamlit as st
import pandas as pd
import plotly.express as px
import os
from datetime import datetime

# 1. CONFIGURATION DE LA PAGE (Le titre dans l'onglet du navigateur)
st.set_page_config(page_title="Observatoire - GEORGINE FOUGA - 24G2137", layout="wide")

# 2. SEUILS D'ALERTE (Paramètres pour l'amélioration "Alerte de prix")
SEUILS = {
    "Riz (1kg)": 800,
    "Sucre (1kg)": 900,
    "Huile (1L)": 1500,
    "Pain": 200,
    "Lait (1L)": 1200
}

# 3. BARRE LATÉRALE : AUTHENTIFICATION (Amélioration "Sécurité")
st.sidebar.title(" Accès Restreint")
st.sidebar.markdown(f"**Application :** fouga-fouga-georgine-24g2137")
st.sidebar.markdown("---")
utilisateur = st.sidebar.text_input("Identifiant")
mot_de_passe = st.sidebar.text_input("Mot de passe", type="password")

# Vérification des identifiants (admin / 1234)
est_connecte = (utilisateur == "admin" and mot_de_passe == "1234")

if est_connecte:
    st.sidebar.success(f"Connecté : {utilisateur}")
else:
    st.sidebar.info("Identifiants de test : admin / 1234")

st.sidebar.markdown("---")
menu = st.sidebar.selectbox("Menu Principal", [" Accueil", " Collecte des données", " Analyse Graphique"])

# 4. LOGIQUE DE CHARGEMENT DES DONNÉES
def charger_donnees():
    if os.path.exists("prix_data.csv"):
        return pd.read_csv("prix_data.csv")
    return pd.DataFrame(columns=["Date", "Produit", "Prix", "Ville"])

df = charger_donnees()

# --- NAVIGATION ---

if menu == "🏠 Accueil":
    st.title("🏙️ Observatoire Urbain des Prix")
    st.subheader("Étudiante : Georgine Fouga | Matricule : 24G2137")
    st.write("---")
    st.write("Bienvenue sur la plateforme de suivi des prix du marché en temps réel.")
    st.info("Cette application permet de collecter et d'analyser les variations de prix des produits de première nécessité.")
    st.image("https://streamlit.io/images/brand/streamlit-logo-secondary-colormark-darktext.png", width=200)

elif menu == "Collecte des données":
    st.header("Formulaire de Saisie")
    
    if not est_connecte:
        st.error("Accès refusé. Vous devez être connecté pour saisir des données.")
        st.warning("Veuillez entrer vos identifiants dans la barre latérale à gauche.")
    else:
        with st.form("form_saisie"):
            col1, col2 = st.columns(2)
            with col1:
                produit = st.selectbox("Sélectionner le produit", list(SEUILS.keys()))
                prix = st.number_input("Prix constaté (FCFA)", min_value=0, step=25)
            with col2:
                ville = st.text_input("Quartier / Ville de relevé")
                date = st.date_input("Date du relevé", datetime.now())

            # --- LOGIQUE D'ALERTE (Amélioration) ---
            if prix > SEUILS.get(produit, 10000) and prix > 0:
                st.warning(f" ALERTE : Le prix de {prix} FCFA est anormalement élevé (Seuil : {SEUILS[produit]} FCFA) !")

            bouton_valider = st.form_submit_button("Enregistrer la donnée")

            if bouton_valider:
                nouvelle_donnee = pd.DataFrame([[date, produit, prix, ville]], columns=["Date", "Produit", "Prix", "Ville"])
                df = pd.concat([df, nouvelle_donnee], ignore_index=True)
                df.to_csv("prix_data.csv", index=False)
                st.success("Donnée enregistrée avec succès !")

elif menu == "Analyse Graphique":
    st.header(" Visualisation des Tendances")
    
    if df.empty:
        st.warning("Aucune donnée disponible pour le moment. Allez dans 'Collecte' pour en ajouter.")
    else:
        # Graphique 1 : Prix moyen par produit
        fig_bar = px.bar(df, x="Produit", y="Prix", color="Produit", title="Comparaison des prix par produit")
        st.plotly_chart(fig_bar, use_container_width=True)
        
        # Graphique 2 : Dispersion des prix
        fig_scatter = px.scatter(df, x="Date", y="Prix", color="Produit", title="Historique des relevés")
        st.plotly_chart(fig_scatter, use_container_width=True)

        st.subheader(" Tableau récapitulatif")
        st.dataframe(df, use_container_width=True)