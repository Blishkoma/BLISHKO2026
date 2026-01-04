import streamlit as st
import pandas as pd
from datetime import date
import os

# --- CONFIGURATION DU SITE ---
st.set_page_config(page_title="2026: MINDSET", page_icon="🔥", layout="centered")

# --- CSS POUR LE STYLE ---
st.markdown("""
    <style>
    .stProgress > div > div > div > div { background-color: #00FF00; }
    .big-font { font-size:20px !important; font-weight: bold; }
    </style>
    """, unsafe_allow_html=True)

# --- TITRE ---
st.title("🔥 2026: MODE GUERRIER")
st.write(f"**Date :** {date.today().strftime('%d/%m/%Y')}")
st.divider()

# --- FORMULAIRE DES OBJECTIFS ---
st.header("1. La Discipline Quotidienne")

col1, col2 = st.columns(2)

with col1:
    st.markdown("### 🧠 ESPRIT & BUSINESS")
    q1 = st.checkbox("📱 Téléphone < 3h")
    q2 = st.checkbox("📚 Travail Scolaire Fait")
    q3 = st.checkbox("📖 Lecture (au moins 1 page)")
    q4 = st.checkbox("💰 Pas de dépenses inutiles")
    q5 = st.checkbox("📈 Check Investissements (Heure fixe)")

with col2:
    st.markdown("### ⚔️ CORPS & ÂME")
    q6 = st.checkbox("🙏 Prière du Jour")
    q7 = st.checkbox("🏋️‍♂️ 20 Pompes x2 (Matin/Soir)")
    q8 = st.checkbox("💪 60 Reps Barre Muscu")
    q9 = st.checkbox("🧹 Chambre Rangée & Hygiène")
    q10 = st.checkbox("🎮 Twitch: Stream ou Amélioration")

# --- SECTION FINANCE & TWITCH ---
st.divider()
st.header("2. Tracking Chiffré")
c1, c2 = st.columns(2)
with c1:
    invest_pnl = st.number_input("💰 Profit/Perte Invest du jour (€)", step=1.0)
with c2:
    twitch_subs = st.number_input("👾 Nombre Abonnés Twitch", min_value=11, step=1)

# --- CALCUL DU SCORE ---
liste_res = [q1, q2, q3, q4, q5, q6, q7, q8, q9, q10]
score = sum(liste_res)
total = len(liste_res)
xp_percent = int((score / total) * 100)

# --- AFFICHAGE RESULTAT ---
st.divider()
st.subheader(f"Niveau du jour : {xp_percent}%")
st.progress(xp_percent / 100)

if xp_percent == 100:
    st.success("👑 MASTERCLASS. Tu as tout validé.")
    st.balloons()
elif xp_percent >= 80:
    st.info("🔥 Grosse journée. Continue.")
elif xp_percent >= 50:
    st.warning("⚠️ Peut mieux faire. Ne lâche pas.")
else:
    st.error("💀 Reprends-toi. Demain on écrase tout.")

# --- SYSTEME DE SAUVEGARDE (PROVISOIRE) ---
# Note pour l'utilisateur : Sur Streamlit Cloud, ce fichier CSV s'effacera au redémarrage.
# La prochaine étape sera de connecter Google Sheets.
if st.button("💾 SAUVEGARDER MA JOURNÉE"):
    st.toast("Données enregistrées (Session temporaire)", icon="✅")
    st.write("📝 *Note : Pour garder l'historique à vie, nous devrons connecter Google Sheets à l'étape suivante.*")
