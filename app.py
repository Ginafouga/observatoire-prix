import streamlit as st
import pandas as pd
import plotly.express as px
import os
from datetime import datetime

#1. CONFIGURATION DE LA PAGE
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
    st.title("🏙️ Observatoire Urbain des Prix")
    
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.info("### 🔐 Espace Administration")
        with st.form("login_form"):
            user = st.text_input("Identifiant")
            pwd = st.text_input("Mot de passe", type="password")
            if st.form_submit_button("Se connecter pour ajouter des données"):
                if user == "admin" and pwd == "1234":
                    st.session_state['authentifie'] = True
                    st.rerun()
                else:
                    st.error("Identifiants incorrects.")

    with col2:
        st.success("### 📊 Rapport Public")
        st.write("Vous pouvez consulter les analyses graphiques sans vous connecter.")
        if st.button("Consulter les graphiques maintenant ➡️"):
            st.session_state['vue_publique'] = True
            st.rerun()
    st.stop()

# --- BARRE LATÉRALE ---
st.sidebar.title("Navigation")
if st.session_state['authentifie']:
    st.sidebar.success("Mode : Administrateur")
    options = ["📝 Collecte des données", "📊 Analyse Graphique"]
else:
    st.sidebar.warning("Mode : Consultation Publique")
    options = ["📊 Analyse Graphique"]

menu = st.sidebar.selectbox("Menu", options)

if st.sidebar.button("Retour à l'accueil / Déconnexion"):
    st.session_state['authentifie'] = False
    st.session_state['vue_publique'] = False
    st.rerun()

# --- CONTENU DES PAGES ---

if menu == "📝 Collecte des données":
    st.header("📝 Saisie de nouveaux relevés")
    with st.form("form_saisie"):
        p = st.selectbox("Produit", list(SEUILS.keys()))
        pr = st.number_input("Prix (FCFA)", min_value=0)
        v = st.text_input("Ville/Quartier")
        d = st.date_input("Date", datetime.now())
        
        if pr > SEUILS.get(p, 10000) and pr > 0:
            st.error(f"⚠️ Alerte Prix Élevé ! (Seuil : {SEUILS[p]} FCFA)")
            
        if st.form_submit_button("Enregistrer"):
            nouvelle_ligne = pd.DataFrame([[d, p, pr, v]], columns=["Date", "Produit", "Prix", "Ville"])
            df = pd.concat([df, nouvelle_ligne], ignore_index=True)
            df.to_csv("prix_data.csv", index=False)
            st.success("Donnée ajoutée !")

elif menu == "📊 Analyse Graphique":
    st.header("📈 Analyse des tendances des prix")
    if df.empty:
        st.warning("Aucune donnée à afficher.")
    else:
        fig = px.bar(df, x="Produit", y="Prix", color="Produit", title="Moyenne des prix collectés")
        st.plotly_chart(fig, use_container_width=True)
        st.subheader("Données brutes")
        st.dataframe(df, use_container_width=True)