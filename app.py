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
        return pd.read_csv("prix_data.csv")
    return pd.DataFrame(columns=["Date", "Produit", "Prix", "Ville"])

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
        # Menus déroulants pour faciliter la connexion
        user_select = st.selectbox("Choisir l'identifiant", ["---", "admin"])
        pwd_select = st.selectbox("Choisir le mot de passe", ["---", "1234"])
        
        if st.button("Connexion"):
            if user_select == "admin" and pwd_select == "1234":
                st.session_state['authentifie'] = True
                st.rerun()
            else:
                st.error("Veuillez sélectionner 'admin' et '1234' pour vous connecter.")

    with col2:
        st.success("###  Rapport Public")
        st.write("Accès limité aux graphiques pour consultation uniquement.")
        if st.button("Consulter les graphiques "):
            st.session_state['vue_publique'] = True
            st.rerun()
    st.stop()

# --- BARRE LATÉRALE DE NAVIGATION ---
st.sidebar.title("Navigation")

if st.session_state['authentifie']:
    st.sidebar.success(" Connecté : Administrateur")
    # L'administrateur a accès aux deux fonctionnalités
    options = ["Collecte des données", " Analyse Graphique"]
else:
    st.sidebar.warning("Mode : Consultation Publique")
    # Le public n'a accès qu'aux graphiques
    options = [" Analyse Graphique"]

menu = st.sidebar.selectbox("Menu de l'application", options)

st.sidebar.markdown("---")
if st.sidebar.button(" Déconnexion / Retour Accueil"):
    st.session_state['authentifie'] = False
    st.session_state['vue_publique'] = False
    st.rerun()

# --- LOGIQUE DES PAGES ---

if menu == "Collecte des données":
    st.header(" Saisie de nouveaux relevés de prix")
    with st.form("form_saisie"):
        p = st.selectbox("Produit", list(SEUILS.keys()))
        pr = st.number_input("Prix constaté (FCFA)", min_value=0, step=25)
        v = st.text_input("Quartier ou Ville")
        d = st.date_input("Date du relevé", datetime.now())
        
        # Alerte si le prix dépasse le seuil défini
        if pr > SEUILS.get(p, 10000) and pr > 0:
            st.error(f"⚠️ ALERTE PRIX : Ce prix semble élevé ! (Seuil conseillé : {SEUILS[p]} FCFA)")
            
        if st.form_submit_button("Enregistrer dans la base"):
            nouvelle_ligne = pd.DataFrame([[d, p, pr, v]], columns=["Date", "Produit", "Prix", "Ville"])
            df = pd.concat([df, nouvelle_ligne], ignore_index=True)
            df.to_csv("prix_data.csv", index=False)
            st.success(f"Le relevé pour {p} a été enregistré avec succès !")

elif menu == " Analyse Graphique":
    st.header("Analyses et Tendances des Prix")
    if df.empty:
        st.warning("Aucune donnée disponible. Connectez-vous en mode Admin pour ajouter des relevés.")
    else:
        # Affichage des graphiques côte à côte
        c1, c2 = st.columns(2)
        with c1:
            fig_bar = px.bar(df, x="Produit", y="Prix", color="Produit", title="Comparaison des prix")
            st.plotly_chart(fig_bar, use_container_width=True)
        with c2:
            fig_scatter = px.scatter(df, x="Date", y="Prix", color="Produit", title="Historique des relevés")
            st.plotly_chart(fig_scatter, use_container_width=True)
        
        st.subheader(" Liste complète des prix enregistrés")
        st.dataframe(df, use_container_width=True)