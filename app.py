import streamlit as st
import pandas as pd
from github import Github
from io import StringIO
from datetime import date, datetime
import pytz

# --- 1. CONFIGURATION & DESIGN SYSTEM (STYLE IOS) ---
st.set_page_config(page_title="Focus 2026", page_icon="", layout="centered")

# CSS AVANCÉ POUR LE LOOK "APPLE"
st.markdown("""
    <style>
    /* Fond gris clair style iOS */
    .stApp {
        background-color: #F2F2F7;
    }
    
    /* Carte style Widget iOS */
    .ios-card {
        background-color: #FFFFFF;
        border-radius: 22px;
        padding: 20px;
        margin-bottom: 15px;
        box-shadow: 0 4px 12px rgba(0,0,0,0.05);
        transition: transform 0.1s;
    }
    .ios-card:active {
        transform: scale(0.98);
    }
    
    /* Titres */
    h1 {
        font-family: -apple-system, BlinkMacSystemFont, sans-serif;
        font-weight: 800;
        color: #000000;
        font-size: 32px !important;
        margin-bottom: 5px;
    }
    h3 {
        font-family: -apple-system, sans-serif;
        font-weight: 600;
        color: #1C1C1E;
        margin: 0;
        padding: 0;
    }
    p {
        color: #8E8E93;
        font-family: -apple-system, sans-serif;
    }

    /* Boutons custom pour ressembler à des liens iOS */
    .stButton > button {
        border-radius: 12px;
        font-weight: 600;
        border: none;
        background-color: #007AFF; /* Apple Blue */
        color: white;
    }
    
    /* Barre de progression style Santé */
    .stProgress > div > div > div > div {
        background-color: #34C759; /* Apple Green */
        border-radius: 10px;
    }
    </style>
    """, unsafe_allow_html=True)

# --- 2. FONCTIONS BACKEND (GITHUB) ---
def get_data():
    try:
        token = st.secrets["GITHUB_TOKEN"]
        repo_name = st.secrets["REPO_NAME"]
        g = Github(token)
        repo = g.get_repo(repo_name)
        try:
            contents = repo.get_contents("data_2026.csv")
            df = pd.read_csv(StringIO(contents.decoded_content.decode("utf-8")))
            return repo, contents, df
        except:
            return repo, None, pd.DataFrame(columns=["Date", "XP", "Phone", "Weight", "Finance_PnL", "Note"])
    except Exception as e:
        return None, None, None # Renvoie None si erreur secrets

def save_data(repo, contents, df, new_data):
    # Mise à jour du DataFrame
    df = pd.concat([df, pd.DataFrame([new_data])], ignore_index=True)
    csv_content = df.to_csv(index=False)
    
    if contents:
        repo.update_file(contents.path, "Daily Update", csv_content, contents.sha)
    else:
        repo.create_file("data_2026.csv", "Init Data", csv_content)
    return df

# --- 3. GESTION DE L'ÉTAT (NAVIGATION) ---
# C'est ici qu'on gère "quelle page est affichée"
if 'page' not in st.session_state:
    st.session_state.page = 'home'
if 'inputs' not in st.session_state:
    st.session_state.inputs = {}

def navigate_to(page_name):
    st.session_state.page = page_name

# Chargement données
repo, contents, df = get_data()

# --- PAGE 1 : DASHBOARD (ACCUEIL) ---
if st.session_state.page == 'home':
    
    # En-tête Date
    today = date.today().strftime("%A %d %B")
    st.markdown(f"<h1>Aujourd'hui</h1><p>{today}</p>", unsafe_allow_html=True)

    if repo is None:
        st.error("⚠️ Erreur de connexion GitHub. Vérifie tes 'Secrets' sur Streamlit Cloud.")
    
    # Barre de progression globale (Résumé)
    xp_global = st.session_state.inputs.get('xp_temp', 0)
    st.progress(xp_global / 100)
    
    st.markdown("---")

    # --- CARTE 1 : FINANCE (La grosse bulle) ---
    with st.container():
        st.markdown('<div class="ios-card">', unsafe_allow_html=True)
        col_icon, col_text, col_action = st.columns([1, 4, 1])
        with col_icon:
            st.markdown("💸")
        with col_text:
            st.markdown("<h3>Finance & Empire</h3>", unsafe_allow_html=True)
            last_pnl = df.iloc[-1]['Finance_PnL'] if (df is not None and not df.empty and 'Finance_PnL' in df.columns) else 0
            st.caption(f"Dernier PnL: {last_pnl} €")
        with col_action:
            if st.button(" Ouvrir ", key="btn_finance"):
                navigate_to('finance')
                st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)

    # --- CARTE 2 : PHYSIQUE ---
    with st.container():
        st.markdown('<div class="ios-card">', unsafe_allow_html=True)
        col_icon, col_text, col_action = st.columns([1, 4, 1])
        with col_icon:
            st.markdown("🦍")
        with col_text:
            st.markdown("<h3>Physique & Santé</h3>", unsafe_allow_html=True)
            st.caption("Pompes, Barre, Poids...")
        with col_action:
            if st.button(" Ouvrir ", key="btn_physique"):
                navigate_to('physique')
                st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)

    # --- CARTE 3 : MENTAL (Prière, Lecture) ---
    with st.container():
        st.markdown('<div class="ios-card">', unsafe_allow_html=True)
        col_icon, col_text, col_action = st.columns([1, 4, 1])
        with col_icon:
            st.markdown("🧠")
        with col_text:
            st.markdown("<h3>Mental & Spirituel</h3>", unsafe_allow_html=True)
            st.caption("Prière, Lecture, Digital...")
        with col_action:
            if st.button(" Ouvrir ", key="btn_mental"):
                navigate_to('mental')
                st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)

    # BOUTON FINAL SAUVEGARDE
    st.markdown("<br>", unsafe_allow_html=True)
    if st.button("✅  CLÔTURER MA JOURNÉE", type="primary", use_container_width=True):
        if repo:
            # Récupération des données stockées en session
            pnl = st.session_state.inputs.get('pnl', 0)
            weight = st.session_state.inputs.get('weight', 70)
            phone = st.session_state.inputs.get('phone', 3)
            
            # Calcul XP (Simplifié : 1 point par section validée)
            # Tu pourras affiner ce calcul
            xp = 100 # Placeholder pour l'instant
            
            new_row = {
                "Date": str(date.today()),
                "XP": xp,
                "Phone": phone,
                "Weight": weight,
                "Finance_PnL": pnl,
                "Note": "RAS"
            }
            save_data(repo, contents, df, new_row)
            st.balloons()
            st.success("Journée enregistrée.")

# --- PAGE 2 : DÉTAIL FINANCE ---
elif st.session_state.page == 'finance':
    st.button("← Retour", on_click=lambda: navigate_to('home'))
    st.markdown("<h1>💰 Finance</h1>", unsafe_allow_html=True)
    
    # Input
    st.markdown('<div class="ios-card">', unsafe_allow_html=True)
    st.write("**Résultat du jour (€)**")
    pnl_input = st.number_input("Plus-value / Moins-value", step=1.0)
    st.session_state.inputs['pnl'] = pnl_input
    
    # Validation glissante (Toggle)
    st.write("")
    is_done = st.toggle("Valider la gestion financière", key="toggle_finance")
    st.markdown('</div>', unsafe_allow_html=True)

    # Graphique
    if df is not None and not df.empty and 'Finance_PnL' in df.columns:
        st.markdown("### 📈 Courbe PnL")
        st.line_chart(df.set_index("Date")["Finance_PnL"])

# --- PAGE 3 : DÉTAIL PHYSIQUE ---
elif st.session_state.page == 'physique':
    st.button("← Retour", on_click=lambda: navigate_to('home'))
    st.markdown("<h1>🦍 Physique</h1>", unsafe_allow_html=True)
    
    st.markdown('<div class="ios-card">', unsafe_allow_html=True)
    st.write("**Poids du corps (kg)**")
    w_input = st.number_input("Poids", value=70.0, step=0.1)
    st.session_state.inputs['weight'] = w_input
    
    st.divider()
    
    # Toggles (Glisser pour valider)
    t1 = st.toggle("20 Pompes x2")
    t2 = st.toggle("60 Reps Barre")
    t3 = st.toggle("Hygiène Impeccable")
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Graphique Poids
    if df is not None and not df.empty and 'Weight' in df.columns:
        st.markdown("### ⚖️ Courbe de Poids")
        st.line_chart(df.set_index("Date")["Weight"])

# --- PAGE 4 : DÉTAIL MENTAL ---
elif st.session_state.page == 'mental':
    st.button("← Retour", on_click=lambda: navigate_to('home'))
    st.markdown("<h1>🧠 Mental</h1>", unsafe_allow_html=True)

    st.markdown('<div class="ios-card">', unsafe_allow_html=True)
    st.write("**Temps d'écran (Heures)**")
    ph_input = st.number_input("Heures", value=3.0, step=0.1)
    st.session_state.inputs['phone'] = ph_input
    
    if ph_input < 3:
        st.success("✨ Temps gagné : " + str(round(3-ph_input, 1)) + "h")
    else:
        st.error("⚠️ Temps perdu : " + str(round(ph_input-3, 1)) + "h")
    
    st.divider()
    
    t_pray = st.toggle("Prière du jour")
    t_read = st.toggle("Lecture terminée")
    st.markdown('</div>', unsafe_allow_html=True)

