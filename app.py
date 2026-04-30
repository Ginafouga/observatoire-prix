import streamlit as st
import pandas as pd
import plotly.express as px
import os
from datetime import datetime

# 1. CONFIGURATION DE LA PAGE
st.set_page_config(page_title="Observatoire - GEORGINE FOUGA - 24G2137", layout="wide")

# 2. SEUILS D'ALERTE POUR LES PRODUITS
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
        # Vérification des colonnes pour éviter les erreurs
        if "Qualite" not in df_load.columns:
            df_load["Qualite"] = "Bonne"
        return df_load
    return pd.DataFrame(columns=["Date", "Produit", "Prix", "Ville", "Qualite"])

df = charger_donnees()

# --- INITIALISATION DE L'ÉTAT DE CONNEXION ---
if 'authentifie' not in st.session_state:
    st.session_state['authentifie'] = False
if 'vue_publique' not in st.session_state:
    st.session_state['vue_publique'] = False

# --- PAGE D'ACCUEIL / LOGIN ---
if not st.session_state['authentifie'] and not st.session_state['vue_publique']:
    st.title("Observatoire Urbain des Prix")
    
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.info("###  Espace Administration")
        # Menus déroulants pour faciliter la connexion du prof
        user_select = st.selectbox("Choisir l'identifiant", ["---", "admin"])
        pwd_select = st.selectbox("Choisir le mot de passe", ["---", "1234"])
        
        if st.button("Connexion"):
            if user_select == "admin" and pwd_select == "1234":
                st.session_state['authentifie'] = True
                st.rerun()
            else:
                st.error("Sélectionnez les bons identifiants.")

    with col2:
        st.success("###  Rapport Public")
        st.write("Accès limité à la visualisation des graphiques uniquement.")
        if st.button("Consulter les graphiques en mode invité "):
            st.session_state['vue_publique'] = True
            st.rerun()
    st.stop()

# --- BARRE LATÉRALE DE NAVIGATION ---
st.sidebar.title("Navigation")

if st.session_state['authentifie']:
    st.sidebar.success(" Mode : Administrateur")
    # L'administrateur a accès à TOUT (Collecte ET Graphes)
    options = [" Collecte des données", " Analyse Graphique"]
else:
    st.sidebar.warning(" Mode : Consultation Publique")
    # Le public ne voit que les graphiques
    options = [" Analyse Graphique"]

menu = st.sidebar.selectbox("Menu", options)

st.sidebar.markdown("---")
if st.sidebar.button(" Déconnexion / Retour Accueil"):
    st.session_state['authentifie'] = False
    st.session_state['vue_publique'] = False
    st.rerun()

# --- LOGIQUE DES PAGES ---

if menu == " Collecte des données":
    st.header(" Saisie de nouveaux relevés (Admin)")
    with st.form("form_saisie"):
        col_1, col_2 = st.columns(2)
        with col_1:
            p = st.selectbox("Produit", list(SEUILS.keys()))
            pr = st.number_input("Prix constaté (FCFA)", min_value=0, step=25)
            v = st.text_input("Ville / Quartier")
        with col_2:
            d = st.date_input("Date du relevé", datetime.now())
            # NOUVELLE SECTION : QUALITÉ PERÇUE
            qual = st.select_slider("Qualité perçue du produit", 
                                    options=["Mauvaise", "Moyenne", "Bonne", "Excellente"],
                                    value="Bonne")
        
        # Alerte de prix
        if pr > SEUILS.get(p, 10000) and pr > 0:
            st.error(f"⚠️ ALERTE : Le prix saisi dépasse le seuil normal ({SEUILS[p]} FCFA) !")
            
        if st.form_submit_button("Enregistrer la donnée"):
            nouvelle_ligne = pd.DataFrame([[d, p, pr, v, qual]], columns=["Date", "Produit", "Prix", "Ville", "Qualite"])
            df = pd.concat([df, nouvelle_ligne], ignore_index=True)
            df.to_csv("prix_data.csv", index=False)
            st.success(f"Donnée enregistrée avec succès !")

elif menu == " Analyse Graphique":
    st.header("Analyses Graphiques et Tendances")
    if df.empty:
        st.warning("La base de données est vide. Ajoutez des données en mode Admin.")
    else:
        # Affichage des graphiques
        c1, c2 = st.columns(2)
        with c1:
            # Graphique prix et qualité
            fig_bar = px.bar(df, x="Produit", y="Prix", color="Qualite", 
                            title="Prix moyens et Qualité perçue",
                            color_discrete_map={"Excellente": "#2ca02c", "Bonne": "#1f77b4", "Moyenne": "#ff7f0e", "Mauvaise": "#d62728"})
            st.plotly_chart(fig_bar, use_container_width=True)
        with c2:
            # Répartition de la qualité
            fig_pie = px.pie(df, names="Qualite", title="Proportion des niveaux de qualité")
            st.plotly_chart(fig_pie, use_container_width=True)
        
        st.subheader("Tableau récapitulatif des données")
        st.dataframe(df, use_container_width=True)