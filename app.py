import streamlit as st
import pandas as pd
from github import Github
from io import StringIO
from datetime import date
import random

# --- CONFIGURATION DU SITE ---
st.set_page_config(page_title="BLISKO MINDSET", page_icon="🦍", layout="wide")

# --- CITATIONS (1 par jour) ---
QUOTES = [
    "La discipline, c'est choisir entre ce que tu veux maintenant et ce que tu veux le plus.",
    "On a deux vies. La deuxième commence quand on réalise qu'on n'en a qu'une. - Confucius",
    "Le succès n'est pas final, l'échec n'est pas fatal : c'est le courage de continuer qui compte.",
    "Fais-le. Si tu as peur, fais-le avec la peur.",
    "Ton niveau de réussite ne dépassera jamais ton niveau de développement personnel.",
    "Ne compte pas les jours, fais en sorte que les jours comptent.",
    "La douleur de la discipline pèse des grammes, la douleur du regret pèse des tonnes.",
]
random.seed(date.today().toordinal()) # La citation change chaque jour, pas à chaque reload
quote_du_jour = random.choice(QUOTES)

# --- CSS PERSONNALISÉ (DESIGN ÉPURÉ) ---
st.markdown("""
    <style>
    .main-title { font-size: 60px !important; font-weight: 800; color: #FFFFFF; text-align: center; margin-bottom: 0px;}
    .quote { font-style: italic; color: #AAAAAA; text-align: center; margin-bottom: 30px; }
    .metric-card { background-color: #262730; padding: 15px; border-radius: 10px; border: 1px solid #444; }
    .stProgress > div > div > div > div { background-color: #4CAF50; }
    </style>
    """, unsafe_allow_html=True)

# --- FONCTIONS GITHUB ---
def get_github_data():
    try:
        token = st.secrets["GITHUB_TOKEN"]
        repo_name = st.secrets["REPO_NAME"]
        g = Github(token)
        repo = g.get_repo(repo_name)
        file_path = "data_2026.csv"
        try:
            contents = repo.get_contents(file_path)
            df = pd.read_csv(StringIO(contents.decoded_content.decode("utf-8")))
            return repo, contents, df
        except:
            return repo, None, pd.DataFrame(columns=["Date", "XP", "Phone_Hours", "Weight", "Twitch", "PnL", "Note"])
    except:
        return None, None, pd.DataFrame()

def save_to_github(repo, contents, df, new_row):
    df = pd.concat([df, pd.DataFrame([new_row])], ignore_index=True)
    csv_content = df.to_csv(index=False)
    file_path = "data_2026.csv"
    if contents:
        repo.update_file(contents.path, "Update", csv_content, contents.sha)
    else:
        repo.create_file(file_path, "Init", csv_content)
    return df

# --- INTERFACE ---
st.markdown('<div class="main-title">BLISKO MINDSET</div>', unsafe_allow_html=True)
st.markdown(f'<div class="quote">“ {quote_du_jour} ”</div>', unsafe_allow_html=True)

repo, contents, df_history = get_github_data()

# --- 1. ZONE DE PROGRÈS GLOBALE ---
xp_today = 0
total_goals = 8 # Nombre total d'objectifs

# --- 2. LES SECTIONS ---

# >>> SECTION PHYSIQUE <<<
st.subheader("🦍 PHYSIQUE & SANTÉ")
c1, c2, c3 = st.columns(3)

with c1:
    st.markdown("**⚖️ Suivi Poids (Objectif : Athlétique)**")
    # Pour 1m76, fourchette indicative
    current_weight = st.number_input("Poids du jour (kg)", min_value=40.0, max_value=120.0, step=0.1, value=70.0)
    if not df_history.empty and "Weight" in df_history.columns:
        last_w = df_history.iloc[-1]["Weight"]
        delta_w = current_weight - last_w
        st.metric("Évolution", f"{current_weight} kg", f"{delta_w:.1f} kg", delta_color="off")
    
    with st.expander("📈 Voir ma courbe de poids"):
        if not df_history.empty:
            st.line_chart(df_history.set_index("Date")["Weight"])
        else:
            st.info("Pas encore de données.")

with c2:
    st.markdown("**⚔️ Entraînement**")
    check_pompes = st.checkbox("20 Pompes x2 (Matin/Soir)")
    check_barre = st.checkbox("60 Reps Barre Muscu")
    if check_pompes: xp_today += 1
    if check_barre: xp_today += 1

with c3:
    st.markdown("**🧹 Hygiène de vie**")
    check_clean = st.checkbox("Chambre Rangée & Hygiène")
    if check_clean: xp_today += 1

st.divider()

# >>> SECTION DIGITAL & MENTAL <<<
st.subheader("🧠 DIGITAL & MINDSET")
d1, d2 = st.columns(2)

with d1:
    st.markdown("**📱 Détox Téléphone**")
    phone_time = st.number_input("Temps d'écran (Heures)", min_value=0.0, step=0.1, help="Combien d'heures aujourd'hui ?")
    
    # Calcul temps gagné (Base 3h)
    time_saved = 3.0 - phone_time
    if time_saved > 0:
        st.success(f"✅ Tu as gagné {time_saved}h de vie aujourd'hui !")
        xp_today += 1 # Valide le point si < 3h
    else:
        st.error(f"❌ Tu as perdu {abs(time_saved)}h bêtement.")
    
    with st.expander("📊 Voir mon historique téléphone"):
        if not df_history.empty and "Phone_Hours" in df_history.columns:
            st.bar_chart(df_history.set_index("Date")["Phone_Hours"])
            st.caption("La ligne rouge imaginaire est à 3h.")

with d2:
    st.markdown("**📚 Développement**")
    check_school = st.checkbox("Travail Scolaire (Sérieux)")
    check_read = st.checkbox("Lecture (Chaque jour)")
    check_pray = st.checkbox("Prière / Méditation")
    
    if check_school: xp_today += 1
    if check_read: xp_today += 1
    if check_pray: xp_today += 1

st.divider()

# >>> SECTION BUSINESS <<<
st.subheader("💸 EMPIRE & FINANCE")
b1, b2 = st.columns(2)

with b1:
    twitch_subs = st.number_input("👾 Abonnés Twitch", value=11)
    check_twitch_work = st.checkbox("Action Twitch faite (Stream/Amélioration)")
    if check_twitch_work: xp_today += 1

with b2:
    pnl = st.number_input("💰 PnL Investissements (€)", step=1.0, help="Gains ou pertes du jour")
    check_invest = st.checkbox("Check Finance fait (Heure précise)")
    if check_invest: xp_today += 0 # Bonus, ne compte pas forcément dans l'XP pour ne pas bloquer si pas de trade

# --- CALCUL DU SCORE FINAL ---
# On normalise sur 100%
final_score = int((xp_today / 8) * 100) # 8 tâches principales comptent pour l'XP
if final_score > 100: final_score = 100

st.divider()
st.markdown(f"<h2 style='text-align: center;'>NIVEAU DU JOUR : {final_score}%</h2>", unsafe_allow_html=True)
st.progress(final_score / 100)
note = st.text_area("📝 Note personnelle du jour (Idées, Victoires, Leçons)")

# --- BOUTON SAVE ---
if st.button("💾 ENREGISTRER MA JOURNÉE"):
    if repo:
        today = str(date.today())
        if not df_history.empty and today in df_history["Date"].values:
            st.warning("Tu as déjà enregistré aujourd'hui.")
        else:
            new_data = {
                "Date": today, 
                "XP": final_score, 
                "Phone_Hours": phone_time,
                "Weight": current_weight,
                "Twitch": twitch_subs, 
                "PnL": pnl, 
                "Note": note
            }
            save_to_github(repo, contents, df_history, new_data)
            st.balloons()
            st.success("Données sauvegardées ! Demain on fait mieux.")
    else:
        st.error("Erreur de connexion GitHub.")

# --- FOOTER ---
st.caption("Taille: 1m76 | Age: 18 | Objectif: Sommet")
