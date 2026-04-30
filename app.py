import streamlit as st
import pandas as pd
import plotly.express as px
import os
from datetime import datetime

# 1. CONFIGURATION DE LA PAGE
st.set_page_config(page_title="Observatoire - GEORGINE FOUGA - 24G2137", layout="wide")

# 2. SEUILS D'ALERTE
SEUILS = {
    "Riz (1kg)": 800,
    "Huile (1L)": 1500,
    "Sucre (1kg)": 900,
    "Pain": 200
}

# 3. CHARGEMENT DES DONNÉES
def charger_donnees():
    if os.path.exists("prix_data.csv"):
        df_load = pd.read_csv("prix_data.csv")
        # S'assurer que la colonne Qualité existe si on ouvre un vieux fichier
        if "Qualite" not in df_load.columns:
            df_load["Qualite"] = "Non précisée"
        return df_load
    return pd.DataFrame(columns=["Date", "Produit", "Prix", "Ville", "Qualite"])

df = charger_donnees()

# --- INITIALISATION DES ÉTATS (Session State) ---
if 'authentifie' not in st.session_state:
    st.session_state['authentifie'] = False
if 'vue_publique' not in st.session_state:
    st.session_state['vue_publique'] = False

# --- PAGE D'ACCUEIL / LOGIN ---
if not st.session_state['authentifie'] and not st.session_state['vue_publique']:
    st.title(" Observatoire Urbain des Prix")
    
    col1, col2 = st.columns(2)
    with col1:
        st.info("###  Espace Administration ")
        user_select = st.selectbox("Choisir l'identifiant", ["---", "admin"])
        pwd_select = st.selectbox("Choisir le mot de passe", ["---", "1234"])
        if st.button("Connexion"):
            if user_select == "admin" and pwd_select == "1234":
                st.session_state['authentifie'] = True
                st.rerun()
            else:
                st.error("Veuillez sélectionner 'admin' et '1234'.")
    with col2:
        st.success("###  Rapport Public")
        if st.button("Consulter les graphiques "):
            st.session_state['vue_publique'] = True
            st.rerun()
    st.stop()

# --- BARRE LATÉRALE ---
st.sidebar.title("Navigation")
options = [" Collecte des données", " Analyse Graphique"] if st.session_state['authentifie'] else [" Analyse Graphique"]
menu = st.sidebar.selectbox("Menu", options)

if st.sidebar.button(" Déconnexion / Retour"):
    st.session_state['authentifie'] = False
    st.session_state['vue_publique'] = False
    st.rerun()

# --- CONTENU DES PAGES ---

if menu == "Collecte des données":
    st.header(" Saisie avec Qualité Perçue")
    with st.form("form_saisie"):
        col_a, col_b = st.columns(2)
        with col_a:
            p = st.selectbox("Produit", list(SEUILS.keys()))
            pr = st.number_input("Prix constaté (FCFA)", min_value=0, step=25)
            v = st.text_input("Quartier ou Ville")
        with col_b:
            d = st.date_input("Date du relevé", datetime.now())
            # NOUVELLE SECTION : Qualité
            qual = st.select_slider("Qualité perçue du produit", 
                                    options=["Mauvaise", "Moyenne", "Bonne", "Excellente"],
                                    value="Bonne")
        
        if pr > SEUILS.get(p, 10000) and pr > 0:
            st.error(f"⚠️ ALERTE : Prix élevé ({pr} FCFA) !")
            
        if st.form_submit_button("Enregistrer le relevé"):
            nouvelle_ligne = pd.DataFrame([[d, p, pr, v, qual]], columns=["Date", "Produit", "Prix", "Ville", "Qualite"])
            df = pd.concat([df, nouvelle_ligne], ignore_index=True)
            df.to_csv("prix_data.csv", index=False)
            st.success("Donnée enregistrée avec l'indice de qualité !")

elif menu == " Analyse Graphique":
    st.header(" Analyses et Qualité")
    if df.empty:
        st.warning("Aucune donnée.")
    else:
        # Graphique 1 : Prix par produit
        fig1 = px.bar(df, x="Produit", y="Prix", color="Qualite", 
                      title="Répartition des prix par produit et par qualité",
                      color_discrete_map={"Excellente": "green", "Bonne": "blue", "Moyenne": "orange", "Mauvaise": "red"})
        st.plotly_chart(fig1, use_container_width=True)
        
        # Graphique 2 : Analyse de la qualité
        fig2 = px.pie(df, names="Qualite", title="Proportion des niveaux de qualité constatés")
        st.plotly_chart(fig2, use_container_width=True)

        st.subheader(" Tableau récapitulatif")
        st.dataframe(df, use_container_width=True)