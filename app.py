import streamlit as st
import pandas as pd
from github import Github
from io import StringIO
from datetime import date, datetime
import pytz

# --- 1. CONFIGURATION & DESIGN DARK MODE ---
st.set_page_config(page_title="2026 Focus", page_icon="🎯", layout="centered")

st.markdown("""
    <style>
    /* FORCE LE FOND NOIR */
    .stApp { background-color: #000000 !important; }
    
    /* TEXTES EN BLANC */
    h1, h2, h3, p, label, div, span { color: #FFFFFF !important; font-family: sans-serif !important; }
    
    /* CARTES INDIVIDUELLES (BULLES) */
    .task-card {
        background-color: #1C1C1E;
        border-radius: 18px;
        padding: 20px;
        margin-bottom: 20px;
        border: 1px solid #333;
    }
    
    /* BOUTON TOGGLE (PERSONNALISATION) */
    div[data-testid="stCheckbox"] label {
        font-size: 16px;
        font-weight: bold;
        color: #4CAF50 !important; /* Vert pour l'action */
    }
    
    /* INPUTS */
    .stNumberInput input { background-color: #2C2C2E !important; color: white !important; }
    </style>
    """, unsafe_allow_html=True)

# --- 2. GESTION GITHUB ---
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
            return repo, None, pd.DataFrame(columns=["Date", "XP"])
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

# --- 3. INIT & VARIABLES ---
repo, contents, df = get_data()
today_obj = datetime.now(pytz.timezone('Europe/Paris'))
is_friday = (today_obj.weekday() == 4)

# Header
st.markdown("<h1>2026 Focus</h1>", unsafe_allow_html=True)
st.caption(today_obj.strftime('%A %d %B'))

# Message erreur si pas connecté
if repo is None:
    st.error("⚠️ Problème connexion GitHub (Secrets)")

# --- 4. LES 9 BULLES (CARTES SÉPARÉES) ---
# On utilise un formulaire pour tout valider d'un coup ou sauvegarder l'état
# Mais ici on va garder l'esprit "Dashboard" avec sauvegarde globale

# 1️⃣ TÉLÉPHONE
st.markdown('<div class="task-card">', unsafe_allow_html=True)
st.markdown("### 📵 Téléphone (< 3h)")
phone_val = st.number_input("Heures aujourd'hui", 0.0, 24.0, 3.0, 0.5, key="in_phone")
valid_phone = st.toggle("Glisser pour valider Téléphone", key="t_phone")
st.markdown('</div>', unsafe_allow_html=True)

# 2️⃣ SCOLAIRE
st.markdown('<div class="task-card">', unsafe_allow_html=True)
st.markdown("### 🎓 Travail Scolaire")
st.write("Le travail du jour a été fait sérieusement ?")
valid_school = st.toggle("Glisser pour valider Scolaire", key="t_school")
st.markdown('</div>', unsafe_allow_html=True)

# 3️⃣ INVESTISSEMENT (PnL)
st.markdown('<div class="task-card">', unsafe_allow_html=True)
st.markdown("### 💰 Investissements")
pnl_val = st.number_input("Gains/Pertes du jour (€)", step=1.0, key="in_pnl")
valid_invest = st.toggle("Glisser pour valider Invest", key="t_invest")
st.markdown('</div>', unsafe_allow_html=True)

# 4️⃣ TWITCH
st.markdown('<div class="task-card">', unsafe_allow_html=True)
st.markdown("### 👾 Twitch")
subs_val = st.number_input("Nombre d'abonnés", 11, 100000, 11, 1, key="in_subs")
valid_twitch = st.toggle("Glisser pour valider Action Twitch", key="t_twitch")
st.markdown('</div>', unsafe_allow_html=True)

# 5️⃣ PRIÈRE
st.markdown('<div class="task-card">', unsafe_allow_html=True)
st.markdown("### 🙏 Prière")
st.write("Connexion spirituelle effectuée ?")
valid_pray = st.toggle("Glisser pour valider Prière", key="t_pray")
st.markdown('</div>', unsafe_allow_html=True)

# 6️⃣ SPORT & POIDS
st.markdown('<div class="task-card">', unsafe_allow_html=True)
st.markdown("### 🦍 Sport (Muscu)")
st.write("20 Pompes x2 + 60 Barre")
if is_friday:
    weight_val = st.number_input("⚖️ Poids du Vendredi (kg)", 40.0, 150.0, 70.0, 0.1, key="in_weight")
else:
    st.info("🔒 Pesée uniquement le Vendredi")
    weight_val = 0.0
valid_sport = st.toggle("Glisser pour valider Sport", key="t_sport")
st.markdown('</div>', unsafe_allow_html=True)

# 7️⃣ HYGIÈNE
st.markdown('<div class="task-card">', unsafe_allow_html=True)
st.markdown("### 🧹 Hygiène & Chambre")
st.write("Chambre rangée, hygiène irréprochable ?")
valid_clean = st.toggle("Glisser pour valider Hygiène", key="t_clean")
st.markdown('</div>', unsafe_allow_html=True)

# 8️⃣ BUDGET (Argent)
st.markdown('<div class="task-card">', unsafe_allow_html=True)
st.markdown("### 💸 Gestion Argent")
st.write("Aucune dépense inutile aujourd'hui ?")
valid_money = st.toggle("Glisser pour valider Budget", key="t_money")
st.markdown('</div>', unsafe_allow_html=True)

# 9️⃣ LECTURE
st.markdown('<div class="task-card">', unsafe_allow_html=True)
st.markdown("### 📖 Lecture")
st.write("Lecture quotidienne effectuée ?")
valid_read = st.toggle("Glisser pour valider Lecture", key="t_read")
st.markdown('</div>', unsafe_allow_html=True)

# --- BOUTON FINAL ---
st.markdown("<br><br>", unsafe_allow_html=True)

# Calcul XP
tasks = [valid_phone, valid_school, valid_invest, valid_twitch, valid_pray, valid_sport, valid_clean, valid_money, valid_read]
score_xp = int((sum(tasks) / 9) * 100)

if st.button("💾 ENREGISTRER MA JOURNÉE", type="primary", use_container_width=True):
    if repo:
        today_str = str(date.today())
        
        # Vérif doublon
        if not df.empty and today_str in df["Date"].values:
            st.warning("⚠️ Tu as déjà enregistré aujourd'hui. (Les données seront écrasées/ajoutées)")
        
        new_row = {
            "Date": today_str,
            "XP": score_xp,
            "Phone": phone_val,
            "PnL": pnl_val,
            "Subs": subs_val,
            "Weight": weight_val,
            # On pourrait sauver le détail de chaque booléen si tu veux, 
            # mais pour l'instant on garde l'essentiel
            "Note": "RAS"
        }
        
        save_data(repo, contents, df, new_row)
        st.balloons()
        st.success(f"Journée validée ! Score: {score_xp}%")
