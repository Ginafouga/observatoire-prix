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
    "Sucre (1kg)": 900,
    "Huile (1L)": 1500,
    "Pain": 200,
    "Lait (1L)": 1200
}

# 3. INITIALISATION DU CHARGEMENT DES DONNÉES
def charger_donnees():
    if os.path.exists("prix_data.csv"):
        return pd.read_csv("prix_data.csv")
    return pd.DataFrame(columns=["Date", "Produit", "Prix", "Ville"])

df = charger_donnees()

# --- SYSTÈME D'AUTHENTIFICATION CENTRALISÉ ---

# On utilise st.session_state pour garder la connexion active
if 'authentifie' not in st.session_state:
    st.session_state['authentifie'] = False

if not st.session_state['authentifie']:
    # PAGE DE CONNEXION PRINCIPALE
    st.title("🔐 Accès à l'Observatoire des Prix")
    st.write("Veuillez vous identifier pour accéder à la plateforme.")
    
    with st.container():
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            form_login = st.form("login_form")
            user = form_login.text_input("Identifiant")
            pwd = form_login.text_input("Mot de passe", type="password")
            submit = form_login.form_submit_button("Se connecter")
            
            if submit:
                if user == "admin" and pwd == "1234":
                    st.session_state['authentifie'] = True
                    st.success("Connexion réussie ! Chargement...")
                    st.rerun() # Recharge la page pour passer à la suite
                else:
                    st.error("Identifiants incorrects.")
    st.stop() # Arrête l'exécution ici tant qu'on n'est pas connecté

# --- CONTENU ACCESSIBLE APRÈS CONNEXION ---

st.sidebar.success(f"Connecté : Administrateur")
menu = st.sidebar.selectbox("Navigation", ["📝 Collecte des données", "📊 Analyse Graphique", "🏠 Accueil"])

if menu == "📝 Collecte des données":
    st.header("📝 Formulaire de Saisie")
    with st.form("form_saisie"):
        col1, col2 = st.columns(2)
        with col1:
            produit = st.selectbox("Sélectionner le produit", list(SEUILS.keys()))
            prix = st.number_input("Prix constaté (FCFA)", min_value=0, step=25)
        with col2:
            ville = st.text_input("Quartier / Ville de relevé")
            date = st.date_input("Date du relevé", datetime.now())

        if prix > SEUILS.get(produit, 10000) and prix > 0:
            st.warning(f"⚠️ ALERTE : Le prix dépasse le seuil ({SEUILS[produit]} FCFA) !")

        if st.form_submit_button("Enregistrer la donnée"):
            nouvelle_donnee = pd.DataFrame([[date, produit, prix, ville]], columns=["Date", "Produit", "Prix", "Ville"])
            df = pd.concat([df, nouvelle_donnee], ignore_index=True)
            df.to_csv("prix_data.csv", index=False)
            st.success("✅ Donnée enregistrée !")

elif menu == "📊 Analyse Graphique":
    st.header("📈 Visualisation des Tendances")
    if df.empty:
        st.warning("Aucune donnée disponible.")
    else:
        st.plotly_chart(px.bar(df, x="Produit", y="Prix", color="Produit", title="Prix par produit"), use_container_width=True)
        st.subheader("📋 Historique complet")
        st.dataframe(df, use_container_width=True)

elif menu == "🏠 Accueil":
    st.title("🏙️ Accueil - Observatoire")
    st.subheader("Étudiante : Georgine Fouga | Matricule : 24G2137")
    st.info("Vous êtes maintenant connecté au système de gestion des prix.")
    if st.button("Se déconnecter"):
        st.session_state['authentifie'] = False
        st.rerun()