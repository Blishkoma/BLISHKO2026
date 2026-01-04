import streamlit as st
import pandas as pd
from github import Github
from io import StringIO
from datetime import date, datetime
import pytz

# --- 1. CONFIGURATION & DESIGN SYSTEM (DARK APPLE PRO) ---
st.set_page_config(page_title="2026 Focus", page_icon="🎯", layout="centered")

# CSS STRICT POUR FORCER LE CONTRASTE (PARDONNEZ LE BLANC SUR BLANC)
st.markdown("""
    <style>
    /* Fond Noir Absolu */
    .stApp {
        background-color: #000000 !important;
    }
    
    /* Titres et Textes en Blanc */
    h1, h2, h3, p, div, span, label {
        color: #FFFFFF !important;
        font-family: -apple-system, BlinkMacSystemFont, sans-serif !important;
    }
    
    /* La "Bulle" (Carte) */
    .apple-card {
        background-color: #1C1C1E; /* Gris très sombre Apple */
        border-radius: 18px;
        padding: 20px;
        margin-bottom: 20px;
        border: 1px solid #333;
    }
    
    /* Inputs (Champs de texte) */
    .stNumberInput input, .stTextInput input {
        background-color: #2C2C2E !important;
        color: white !important;
        border-radius: 10px;
    }
    
    /* Le Toggle (Interrupteur) - Customisation */
    div[data-testid="stCheckbox"] label {
        font-weight: bold;
        font-size: 18px;
    }
    
    /* Bouton "Plus de précision" */
    .small-btn {
        font-size: 12px;
        color: #0A84FF !important; /* Bleu Apple */
        text-decoration: none;
        cursor: pointer;
    }
    
    /* Messages d'erreur/succès */
    .stAlert {
        background-color: #2C2C2E;
        color: white;
    }
    </style>
    """, unsafe_allow_html=True)

# --- 2. BACKEND (GITHUB) ---
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
            return repo, None, pd.DataFrame(columns=["Date", "XP", "Phone", "Weight", "PnL", "Note"])
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

# --- 3. GESTION DE NAVIGATION ---
if 'page' not in st.session_state:
    st.session_state.page = 'home'
    st.session_state.detail_view = None # Pour savoir quel graph afficher

def go_home():
    st.session_state.page = 'home'
    st.session_state.detail_view = None

def go_detail(category):
    st.session_state.page = 'detail'
    st.session_state.detail_view = category

# --- INIT ---
repo, contents, df = get_data()
today_obj = datetime.now(pytz.timezone('Europe/Paris'))
is_friday = (today_obj.weekday() == 4) # 4 = Vendredi

# ==========================================
# PAGE DÉTAILS (GRAPHIQUES)
# ==========================================
if st.session_state.page == 'detail':
    st.button("← Retour", on_click=go_home)
    category = st.session_state.detail_view
    
    st.title(f"Historique : {category}")
    
    if df is not None and not df.empty:
        # Configuration des graphs selon la catégorie
        if category == "Poids":
            if "Weight" in df.columns:
                st.line_chart(df.set_index("Date")["Weight"])
                st.info("Rappel : La pesée se fait uniquement le vendredi.")
        
        elif category == "Téléphone":
            if "Phone" in df.columns:
                st.bar_chart(df.set_index("Date")["Phone"])
                st.caption("Barre idéale : En dessous de 3h")

        elif category == "Finance":
            if "PnL" in df.columns:
                st.line_chart(df.set_index("Date")["PnL"])
    else:
        st.warning("Pas encore assez de données pour afficher les courbes.")

# ==========================================
# PAGE D'ACCUEIL (LES BULLES)
# ==========================================
else:
    st.markdown("<h1>2026 Focus</h1>", unsafe_allow_html=True)
    st.markdown(f"<p style='opacity:0.7;'>{today_obj.strftime('%A %d %B')}</p>", unsafe_allow_html=True)

    if repo is None:
        st.error("❌ Erreur GitHub : Vérifie tes secrets !")

    # --- VARIABLES DE SAUVEGARDE ---
    # On initialise les valeurs par défaut
    if 'val_phone' not in st.session_state: st.session_state.val_phone = 3.0
    if 'val_weight' not in st.session_state: st.session_state.val_weight = 0.0
    if 'val_pnl' not in st.session_state: st.session_state.val_pnl = 0.0

    # ----------------------------------------------------
    # BULLE 1 : TÉLÉPHONE (Logique de temps gagné)
    # ----------------------------------------------------
    st.markdown('<div class="apple-card">', unsafe_allow_html=True)
    col1, col2 = st.columns([4, 1])
    with col1:
        st.markdown("### 📵 Détox Téléphone")
    with col2:
        if st.button("📊", key="detail_phone"): go_detail("Téléphone")

    st.write("Temps d'écran aujourd'hui (Heures) :")
    phone_input = st.number_input("Heures", min_value=0.0, max_value=24.0, step=0.1, key="input_phone", label_visibility="collapsed")
    
    # Logique de validation
    if phone_input > 0:
        temps_gagne = 16 - phone_input # Base de 16h éveillé
        if temps_gagne > 0:
            st.caption(f"✨ Tu as récupéré {temps_gagne:.1f}h de vie.")
        toggle_phone = st.toggle("Valider la journée sans écran", key="toggle_phone")
    else:
        st.warning("⚠️ Rentre ton temps d'écran pour valider.")
        toggle_phone = False
    st.markdown('</div>', unsafe_allow_html=True)


    # ----------------------------------------------------
    # BULLE 2 : PHYSIQUE & POIDS (Bloqué Vendredi)
    # ----------------------------------------------------
    st.markdown('<div class="apple-card">', unsafe_allow_html=True)
    col1, col2 = st.columns([4, 1])
    with col1:
        st.markdown("### 🦍 Physique & Poids")
    with col2:
        if st.button("📊", key="detail_weight"): go_detail("Poids")

    # SECTION MUSCU (Toujours visible)
    st.markdown("**Action du jour**")
    toggle_sport = st.toggle("20 Pompes x2 + 60 Barre", key="toggle_sport")
    
    st.divider()

    # SECTION POIDS (Logique Vendredi)
    st.markdown("**Pesée Hebdomadaire**")
    if is_friday:
        weight_input = st.number_input("Poids ce vendredi (kg)", min_value=0.0, step=0.1, key="input_weight")
        if weight_input > 0:
            st.success("✅ Poids enregistré pour la courbe.")
        else:
            st.error("⚠️ C'est vendredi : Rentre ton poids !")
    else:
        st.info(f"🔒 Pesée verrouillée. Prochaine pesée : Vendredi.")
        weight_input = 0.0 # Valeur par défaut si pas vendredi
    st.markdown('</div>', unsafe_allow_html=True)


    # ----------------------------------------------------
    # BULLE 3 : FINANCE (Input obligatoire)
    # ----------------------------------------------------
    st.markdown('<div class="apple-card">', unsafe_allow_html=True)
    col1, col2 = st.columns([4, 1])
    with col1:
        st.markdown("### 💸 Finance & Invest")
    with col2:
        if st.button("📊", key="detail_finance"): go_detail("Finance")

    st.write("Résultat du jour (PnL €) :")
    pnl_input = st.number_input("PnL", step=1.0, key="input_pnl", label_visibility="collapsed")
    
    # Logique : On ne valide pas si c'est à 0 sans confirmation (optionnel, mais mieux pour la rigueur)
    toggle_finance = st.toggle("Valider gestion finance", key="toggle_finance")
    st.markdown('</div>', unsafe_allow_html=True)
    
    
    # ----------------------------------------------------
    # BULLE 4 : SPIRITUEL (Simple)
    # ----------------------------------------------------
    st.markdown('<div class="apple-card">', unsafe_allow_html=True)
    st.markdown("### 🧠 Esprit (Prière & Lecture)")
    toggle_spirit = st.toggle("Actions spirituelles effectuées", key="toggle_spirit")
    st.markdown('</div>', unsafe_allow_html=True)


    # ==========================================
    # BOUTON FINAL DE SAUVEGARDE
    # ==========================================
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Calcul du XP (Simplifié : 1 point par Toggle activé)
    xp_score = 0
    if toggle_phone: xp_score += 25
    if toggle_sport: xp_score += 25
    if toggle_finance: xp_score += 25
    if toggle_spirit: xp_score += 25

    if st.button("💾 SAUVEGARDER MA JOURNÉE", type="primary", use_container_width=True):
        if repo:
            # Vérification : Si c'est vendredi et poids = 0, on bloque ? 
            # Pour l'instant on laisse passer mais on sauvegarde 0.
            
            today_str = str(date.today())
            
            # On vérifie si déjà fait
            if not df.empty and today_str in df["Date"].values:
                st.toast("⚠️ Déjà enregistré aujourd'hui !", icon="⚠️")
            else:
                new_data = {
                    "Date": today_str,
                    "XP": xp_score,
                    "Phone": phone_input,
                    "Weight": weight_input, # Sera 0 si pas vendredi
                    "PnL": pnl_input,
                    "Note": ""
                }
                save_data(repo, contents, df, new_data)
                st.balloons()
                st.success(f"Journée validée ! Score : {xp_score}%")
