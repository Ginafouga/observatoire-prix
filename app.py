import streamlit as st
import pandas as pd
import os
from datetime import datetime
import plotly.express as px

# Configuration de la page
st.set_page_config(page_title="Observatoire des Prix", layout="wide")
st.title("📊 Smart City : Observatoire des Prix du Marché")

# Fichier de stockage
DATA_FILE = "prix_marche.csv"

def load_data():
    if os.path.exists(DATA_FILE):
        return pd.read_csv(DATA_FILE)
    return pd.DataFrame(columns=["Date", "Produit", "Prix", "Quartier", "Qualité"])

data = load_data()

# --- MENU LATÉRAL ---
menu = st.sidebar.selectbox("Navigation", ["Collecte de données", "Analyse Descriptive"])

if menu == "Collecte de données":
    st.header("🛒 Formulaire de collecte")
    with st.form("form_prix"):
        col1, col2 = st.columns(2)
        with col1:
            produit = st.selectbox("Produit", ["Riz (1kg)", "Huile (1L)", "Sucre (1kg)", "Pain"])
            prix = st.number_input("Prix constaté (FCFA)", min_value=0, step=25)
        with col2:
            quartier = st.selectbox("Quartier", ["Nsam", "Nkoabang", "Mokolo", "Nsimeyong"])
            qualite = st.slider("Qualité perçue (1=Bas, 5=Excellent)", 1, 5, 3)
        submit = st.form_submit_button("Enregistrer la donnée")
        
        if submit:
            new_row = {"Date": datetime.now().strftime("%Y-%m-%d"), "Produit": produit, "Prix": prix, "Quartier": quartier, "Qualité": qualite}
            data = pd.concat([data, pd.DataFrame([new_row])], ignore_index=True)
            data.to_csv(DATA_FILE, index=False)
            st.success("Donnée enregistrée avec succès !")

elif menu == "Analyse Descriptive":
    st.header("📈 Analyse des tendances")
    if data.empty:
        st.warning("Aucune donnée disponible. Ajoutez des prix dans l'onglet Collecte.")
    else:
        # Indicateurs
        c1, c2, c3 = st.columns(3)
        c1.metric("Total Relevés", len(data))
        c2.metric("Prix Moyen", f"{data['Prix'].mean():.0f} FCFA")
        c3.metric("Quartier le plus actif", data['Quartier'].mode()[0])
        
        st.divider()
        
        # Graphiques
        col_left, col_right = st.columns(2)
        with col_left:
            st.subheader("Prix par Produit")
            fig1 = px.bar(data.groupby("Produit")["Prix"].mean().reset_index(), x="Produit", y="Prix", color="Produit")
            st.plotly_chart(fig1, use_container_width=True)
        with col_right:
            st.subheader("Distribution par Quartier")
            fig2 = px.box(data, x="Quartier", y="Prix", color="Quartier")
            st.plotly_chart(fig2, use_container_width=True)