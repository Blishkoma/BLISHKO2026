import streamlit as st
import pandas as pd
from github import Github
from io import StringIO
from datetime import date, datetime
import pytz

# --- 1. CONFIGURATION & CSS "APPLE DARK" ---
st.set_page_config(page_title="2026 Focus", page_icon="🎯", layout="centered")

st.markdown("""
    <style>
    /* FOND NOIR TOTAL */
    .stApp { background-color: #000000 !important; }
    
    /* TEXTES */
    h1, h2, h3, p, span, div { 
        color: #FFFFFF !important; 
        font-family: -apple-system, sans-serif !important; 
    }

    /* LE "JOYSTICK" (TOGGLE) EN GÉANT */
    /* On agrandit physiquement le bouton switch pour qu'il soit massif */
    div[data-testid="stCheckbox"] {
        transform: scale(1.8); /* Agrandissement X1.8 */
        margin-left: 10px;
        margin-top: 10px;
    }
    div[data-testid="stCheckbox"] label {
        display: none; /* On cache le petit texte à côté du switch car on met le titre au dessus */
    }

    /* CARTE TYPE IOS */
    .ios-card {
        background-color: #1C1C1E;
        border-radius: 20px;
        padding: 25px;
        margin-bottom: 25px;
        border: 1px solid #333;
    }

    /* INPUTS TYPE IOS */
    .stNumberInput input {
        background-color: #2C2C2E !important;
        color: white !important;
        border-radius: 10px !important;
        text-align: center;
        font-size: 20px;
        font-weight: bold;
    }
    
    /* ONGLETS (TABS) */
    button[data-baseweb="tab"] {
        font-size: 20px !important;
        font-weight: bold !important;
    }
    </style>
    """, unsafe_allow_html=True)

# --- 2. GESTION GITHUB (CONNEXION) ---
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
            # Création du DataFrame avec toutes les colonnes nécessaires pour les courbes
            return repo, None, pd.DataFrame(columns=["Date", "XP", "Phone", "Weight", "PnL", "Twitch"])
    except:
        return None, None, None

def save_data(repo, contents, df, new_row):
    df = pd.concat([df, pd.DataFrame([new_row])], ignore_index=True)
    csv = df.to_csv(index=False)
    if contents:
        repo.update_file(contents.path, "Update", csv, contents.sha)
    else:
        repo.create_file("data_2026.csv", "Init", csv)
    return df

# --- 3. INITIALISATION ---
repo, contents, df = get_data()
tz = pytz.timezone('Europe/Paris')
today_obj = datetime.now(tz)
is_friday = (today_obj.weekday() == 4)

st.title("2026 FOCUS")
st.write(f"*{today_obj.strftime('%d %B %Y')}*")

# --- 4. NAVIGATION PAR ONGLETS ---
tab_journal, tab_vision = st.tabs(["📝 JOURNAL DU JOUR", "📈 VISION & COURBES"])

# =======================================================
# ONGLET 1 : LE JOURNAL (ACTIONS)
# =======================================================
with tab_journal:
    
    # 📱 TÉLÉPHONE
    st.markdown('<div class="ios-card">', unsafe_allow_html=True)
    st.write("### 📵 DÉTOX TÉLÉPHONE")
    phone_val = st.number_input("Heures d'écran", 0.0, 24.0, 3.0, 0.5, key="phone_in")
    
    # Calcul temps gagné
    if phone_val > 0:
        vie_gagnee = 16 - phone_val
        st.caption(f"Temps de vie réel : {vie_gagnee}h")
    
    col_t1, col_t2 = st.columns([4, 1])
    with col_t1: st.write("**Valider (-3h)**")
    with col_t2: t_phone = st.toggle("Validate Phone", key="t_phone")
    st.markdown('</div>', unsafe_allow_html=True)

    # 🦍 SPORT & POIDS
    st.markdown('<div class="ios-card">', unsafe_allow_html=True)
    st.write("### 🦍 SPORT & CORPS")
    st.write("20 Pompes x2 + 60 Barre")
    
    # Poids (Seulement le vendredi)
    if is_friday:
        st.write("⚖️ **Pesée du Vendredi**")
        weight_val = st.number_input("Poids (kg)", 0.0, 150.0, 70.0, 0.1, key="weight_in")
    else:
        st.caption("🔒 Pesée verrouillée (Attendre Vendredi)")
        weight_val = 0.0 # On met 0 pour ne pas fausser le graphique

    col_s1, col_s2 = st.columns([4, 1])
    with col_s1: st.write("**Valider Séance**")
    with col_s2: t_sport = st.toggle("Validate Sport", key="t_sport")
    st.markdown('</div>', unsafe_allow_html=True)

    # 💰 FINANCE
    st.markdown('<div class="ios-card">', unsafe_allow_html=True)
    st.write("### 💸 EMPIRE & FINANCE")
    pnl_val = st.number_input("PnL du Jour (€)", step=1.0, key="pnl_in")
    
    col_f1, col_f2 = st.columns([4, 1])
    with col_f1: st.write("**Valider Check Finance**")
    with col_f2: t_finance = st.toggle("Validate Finance", key="t_finance")
    st.markdown('</div>', unsafe_allow_html=True)

    # 👾 TWITCH
    st.markdown('<div class="ios-card">', unsafe_allow_html=True)
    st.write("### 👾 TWITCH")
    twitch_val = st.number_input("Nombre Abonnés", 0, 1000000, 11, 1, key="twitch_in")
    
    col_tw1, col_tw2 = st.columns([4, 1])
    with col_tw1: st.write("**Valider Action**")
    with col_tw2: t_twitch = st.toggle("Validate Twitch", key="t_twitch")
    st.markdown('</div>', unsafe_allow_html=True)

    # 🧠 MINDSET (Prière, Lecture, etc.)
    st.markdown('<div class="ios-card">', unsafe_allow_html=True)
    st.write("### 🧠 MINDSET & DISCIPLINE")
    
    c1, c2 = st.columns([4, 1])
    with c1: st.write("🙏 Prière Effectuée")
    with c2: t_pray = st.toggle("Prière", key="t_pray")
    
    st.markdown("---")
    
    c3, c4 = st.columns([4, 1])
    with c3: st.write("📖 Lecture Effectuée")
    with c4: t_read = st.toggle("Lecture", key="t_read")
    
    st.markdown("---")
    
    c5, c6 = st.columns([4, 1])
    with c5: st.write("🎓 Travail Scolaire")
    with c6: t_school = st.toggle("School", key="t_school")
    
    st.markdown("---")

    c7, c8 = st.columns([4, 1])
    with c7: st.write("🧹 Chambre & Hygiène")
    with c8: st.write(""); t_clean = st.toggle("Clean", key="t_clean")
    st.markdown('</div>', unsafe_allow_html=True)

    # --- BOUTON SAUVEGARDE ---
    st.write("")
    if st.button("💾 ENREGISTRER MA JOURNÉE", type="primary", use_container_width=True):
        if repo:
            # Calcul Score
            items = [t_phone, t_sport, t_finance, t_twitch, t_pray, t_read, t_school, t_clean]
            xp = int((sum(items)/len(items))*100)
            
            today_str = str(date.today())
            
            # Vérif si déjà fait
            if not df.empty and today_str in df["Date"].values:
                st.toast("⚠️ Mise à jour de la journée...", icon="🔄")
                # Optionnel: logique pour écraser la ligne existante, ici on ajoute simple
            
            new_row = {
                "Date": today_str,
                "XP": xp,
                "Phone": phone_val,
                "Weight": weight_val,
                "PnL": pnl_val,
                "Twitch": twitch_val
            }
            save_data(repo, contents, df, new_row)
            st.success(f"Sauvegardé ! XP du jour : {xp}%")
        else:
            st.error("Erreur de connexion GitHub")

# =======================================================
# ONGLET 2 : LA VISION (LES COURBES)
# =======================================================
with tab_vision:
    st.header("📈 Mes Statistiques")
    
    if df is not None and not df.empty:
        # Conversion Date pour tri
        df["Date"] = pd.to_datetime(df["Date"])
        df = df.sort_values("Date")
        
        # 1. GRAPHIQUE DISCIPLINE (XP)
        st.write("### 🔥 Discipline Générale (%)")
        st.line_chart(df.set_index("Date")["XP"])
        
        # 2. GRAPHIQUE FINANCE
        st.write("### 💰 PnL Investissements (€)")
        st.bar_chart(df.set_index("Date")["PnL"])
        
        # 3. GRAPHIQUE POIDS
        st.write("### 🦍 Évolution Poids (kg)")
        # On filtre pour ne pas afficher les jours à 0 (jours sans pesée)
        df_weight = df[df["Weight"] > 10] 
        if not df_weight.empty:
            st.line_chart(df_weight.set_index("Date")["Weight"])
        else:
            st.info("Rentre ton poids un vendredi pour voir la courbe.")
            
        # 4. GRAPHIQUE TÉLÉPHONE
        st.write("### 📵 Temps d'écran (Heures)")
        st.bar_chart(df.set_index("Date")["Phone"])
        st.caption("Objectif : Rester bas.")
        
        # 5. GRAPHIQUE TWITCH
        st.write("### 👾 Abonnés Twitch")
        st.line_chart(df.set_index("Date")["Twitch"])
        
    else:
        st.warning("Aucune donnée enregistrée pour le moment. Remplis ton journal dans le premier onglet !")
