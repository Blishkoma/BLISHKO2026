import streamlit as st
import pandas as pd
from github import Github
from io import StringIO
from datetime import datetime, date
import pytz # Pour l'heure de Paris

# --- CONFIGURATION DU SITE ---
st.set_page_config(page_title="2026: LEGACY", page_icon="🦍", layout="wide")

# --- STYLE CSS PREMIUM ---
st.markdown("""
    <style>
    /* Gros titre */
    .main-title { font-size: 50px !important; font-weight: 800; color: #ffffff; text-align: center; margin-top: -20px; }
    /* Sous-titre citation */
    .quote { font-size: 18px; font-style: italic; color: #FFD700; text-align: center; margin-bottom: 20px; opacity: 0.8; }
    /* Compte à rebours */
    .countdown { font-size: 25px; font-weight: bold; color: #FF4B4B; text-align: center; background-color: #262730; padding: 10px; border-radius: 10px; border: 1px solid #444; margin-bottom: 30px;}
    /* Métriques */
    div[data-testid="stMetricValue"] { font-size: 24px; color: #4CAF50; }
    </style>
    """, unsafe_allow_html=True)

# --- FONCTIONS GITHUB ---
def get_github_data():
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
            return repo, None, pd.DataFrame(columns=["Date", "XP", "Phone", "Weight", "Twitch", "PnL", "Note"])
    except:
        return None, None, pd.DataFrame()

def save_to_github(repo, contents, df, new_row):
    df = pd.concat([df, pd.DataFrame([new_row])], ignore_index=True)
    csv_content = df.to_csv(index=False)
    if contents:
        repo.update_file(contents.path, "Update", csv_content, contents.sha)
    else:
        repo.create_file("data_2026.csv", "Init", csv_content)
    return df

# --- VARIABLES & TEMPS (PARIS) ---
paris_tz = pytz.timezone('Europe/Paris')
now = datetime.now(paris_tz)
end_of_year = datetime(2027, 1, 1, tzinfo=paris_tz) # Objectif fin 2026
delta = end_of_year - now

# --- CITATIONS TOURNANTES (Basé sur le jour de l'année) ---
quotes_db = [
    "La discipline est mère du succès. - Eschyle",
    "Ce n'est pas parce que c'est difficile que nous n'osons pas, c'est parce que nous n'osons pas que c'est difficile. - Sénèque",
    "Un gagnant est un rêveur qui n'abandonne jamais. - Nelson Mandela",
    "La seule façon de faire du bon travail est d'aimer ce que vous faites. - Steve Jobs",
    "Ils ne savaient pas que c'était impossible, alors ils l'ont fait. - Mark Twain",
    "Le succès, c'est tomber sept fois, se relever huit. - Proverbe Japonais",
    "Votre temps est limité, ne le gâchez pas en menant une existence qui n'est pas la vôtre. - Steve Jobs"
]
# Choix de la citation basé sur le numéro du jour (1-365) pour que ça change chaque jour
quote_idx = int(now.strftime("%j")) % len(quotes_db)
quote_du_jour = quotes_db[quote_idx]

# --- HEADER ---
st.markdown('<div class="main-title">BLISHKO MINDSET</div>', unsafe_allow_html=True)
st.markdown(f'<div class="quote">“ {quote_du_jour} ”</div>', unsafe_allow_html=True)
st.markdown(f'<div class="countdown">⏳ TEMPS RESTANT 2026 : {delta.days} Jours, {delta.seconds//3600} Heures</div>', unsafe_allow_html=True)

# Connexion Données
repo, contents, df = get_github_data()
xp_score = 0

# --- NAVIGATION ONGLETS ---
tab1, tab2, tab3 = st.tabs(["🦍 PHYSIQUE", "🧠 MENTAL & DIGITAL", "💸 EMPIRE & FINANCE"])

# >>> ONGLET 1: PHYSIQUE <<<
with tab1:
    col1, col2 = st.columns(2)
    with col1:
        st.info("📉 **Tracking Poids** (Obj: 75kg Athlétique)")
        weight = st.number_input("Poids du jour (kg)", value=70.0, step=0.1, format="%.1f")
        
        # Petit calcul de variation si données existent
        if not df.empty and "Weight" in df.columns:
            last_w = df.iloc[-1]["Weight"]
            diff = weight - last_w
            if diff < 0: st.caption(f"📉 Perte de {abs(diff):.1f}kg depuis la dernière fois")
            elif diff > 0: st.caption(f"📈 Prise de {diff:.1f}kg depuis la dernière fois")
            
    with col2:
        st.write("**Training du jour**")
        q_pompes = st.checkbox("🔥 20 Pompes x2 (Matin/Soir)")
        q_barre = st.checkbox("💪 60 Reps Barre Muscu")
        q_clean = st.checkbox("🧹 Hygiène & Chambre Clean")
    
    if q_pompes: xp_score += 1
    if q_barre: xp_score += 1
    if q_clean: xp_score += 1

# >>> ONGLET 2: MENTAL <<<
with tab2:
    col_m1, col_m2 = st.columns(2)
    with col_m1:
        st.warning("📵 **Guerre contre le scroll**")
        phone_hours = st.number_input("Temps d'écran (Heures)", value=3.0, step=0.1)
        
        # Calcul impact de vie
        limit = 3.0
        saved = limit - phone_hours
        if saved > 0:
            st.success(f"✅ Tu as gagné {saved:.1f}h de vie pour toi !")
            xp_score += 1 # Point gagné
        else:
            st.error(f"❌ Tu as perdu {abs(saved):.1f}h.")
            
    with col_m2:
        st.write("**Nourriture de l'esprit**")
        q_read = st.checkbox("📖 Lecture (Min 10 pages)")
        q_pray = st.checkbox("🙏 Prière / Méditation")
        q_school = st.checkbox("🎓 Travail Scolaire (Deep Work)")
        
    if q_read: xp_score += 1
    if q_pray: xp_score += 1
    if q_school: xp_score += 1

# >>> ONGLET 3: BUSINESS <<<
with tab3:
    col_b1, col_b2 = st.columns(2)
    with col_b1:
        st.metric("Abonnés Twitch", "Objectif: Sommet")
        twitch_subs = st.number_input("Nombre actuel", value=11, step=1)
        q_twitch = st.checkbox("👾 Action Twitch (Stream ou Amélioration)")
    
    with col_b2:
        st.metric("Investissement", "Suivi Quotidien")
        pnl = st.number_input("💰 Gains/Pertes du jour (€)", step=1.0)
        q_invest = st.checkbox("📊 Check Finance fait (Heure fixe)")
        q_budget = st.checkbox("🚫 0 Dépense inutile")

    if q_twitch: xp_score += 1
    if q_budget: xp_score += 1
    # Check finance est un bonus neutre (ne penalise pas l'xp mais nécessaire pour la discipline)

# --- SCORE FINAL & SAVE ---
st.divider()
final_xp = int((xp_score / 8) * 100) # 8 Tâches principales comptent pour l'XP
if final_xp > 100: final_xp = 100

c_score, c_btn = st.columns([2, 1])

with c_score:
    st.write(f"### 🛡️ NIVEAU DU JOUR : {final_xp}%")
    st.progress(final_xp / 100)

with c_btn:
    note = st.text_input("Note rapide du jour")
    if st.button("💾 SAUVEGARDER MA JOURNÉE", type="primary"):
        if repo:
            today_str = str(date.today())
            if not df.empty and today_str in df["Date"].values:
                st.toast("⚠️ Déjà enregistré aujourd'hui !", icon="⚠️")
            else:
                new_data = {
                    "Date": today_str,
                    "XP": final_xp,
                    "Phone": phone_hours,
                    "Weight": weight,
                    "Twitch": twitch_subs,
                    "PnL": pnl,
                    "Note": note
                }
                save_to_github(repo, contents, df, new_data)
                st.balloons()
                st.toast("✅ Données sécurisées !", icon="🔥")
        else:
            st.error("Problème de connexion GitHub.")

# --- HISTORIQUE GRAPHIQUE (Dans un expander pour rester épuré) ---
st.markdown("---")
with st.expander("📊 Voir mes statistiques et courbes"):
    if not df.empty:
        st.write("### Évolution XP")
        st.line_chart(df.set_index("Date")["XP"])
        
        c_h1, c_h2 = st.columns(2)
        with c_h1:
            st.write("### ⚖️ Poids")
            st.line_chart(df.set_index("Date")["Weight"])
        with c_h2:
            st.write("### 📱 Temps d'écran")
            st.bar_chart(df.set_index("Date")["Phone"])
    else:
        st.info("Sauvegarde ta première journée pour voir les graphiques !")

