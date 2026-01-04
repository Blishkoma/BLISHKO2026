import streamlit as st
import pandas as pd
from github import Github
from io import StringIO
from datetime import date

# --- CONFIGURATION ---
st.set_page_config(page_title="2026: FOCUS", page_icon="🎯", layout="centered")

# --- DESIGN ÉPURÉ ---
st.markdown("""
    <style>
    .big-title { font-size: 40px !important; font-weight: bold; text-align: center; margin-bottom: 0px; }
    .subtitle { font-size: 18px; text-align: center; color: #888; margin-bottom: 20px; }
    .stProgress > div > div > div > div { background-color: #4CAF50; }
    .metric-box { background-color: #f0f2f6; padding: 10px; border-radius: 10px; text-align: center; color: black; font-weight: bold;}
    </style>
    """, unsafe_allow_html=True)

# --- FONCTIONS GITHUB (Pour la sauvegarde) ---
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
            return repo, None, pd.DataFrame(columns=["Date", "Score", "Phone", "Weight", "Twitch", "Note"])
    except:
        return None, None, pd.DataFrame()

def save_data(repo, contents, df, new_row):
    df = pd.concat([df, pd.DataFrame([new_row])], ignore_index=True)
    csv = df.to_csv(index=False)
    if contents:
        repo.update_file(contents.path, "Update", csv, contents.sha)
    else:
        repo.create_file("data_2026.csv", "Init", csv)
    return df

# --- DÉBUT DE L'INTERFACE ---

# On prépare un espace vide en haut pour le Score (on le remplira à la fin du code)
header_placeholder = st.container()

# Connexion aux données
repo, contents, df = get_data()

# --- LES ONGLETS (Navigation simple) ---
t1, t2, t3 = st.tabs(["🦍 PHYSIQUE", "🧠 MENTAL", "💸 EMPIRE"])

# Variables pour le score
total_objectifs = 8 
objectifs_attains = 0

# >>> ONGLET 1 : PHYSIQUE <<<
with t1:
    st.write("### ⚖️ Mon Corps")
    # Poids
    weight = st.number_input("Poids du jour (kg)", value=70.0, step=0.1)
    if not df.empty and "Weight" in df.columns:
        diff = weight - df.iloc[-1]["Weight"]
        st.caption(f"Variation: {diff:+.1f} kg")

    st.write("### ⚔️ Discipline Physique")
    c1 = st.checkbox("🔥 20 Pompes x2 (Matin/Soir)")
    c2 = st.checkbox("💪 60 Reps Barre Muscu")
    c3 = st.checkbox("🧹 Chambre Clean & Hygiène")
    
    if c1: objectifs_attains += 1
    if c2: objectifs_attains += 1
    if c3: objectifs_attains += 1

# >>> ONGLET 2 : MENTAL <<<
with t2:
    st.write("### 📵 Temps de Vie")
    st.write("Sur une journée de 16h éveillé :")
    phone = st.number_input("Combien d'heures sur ton tel ?", value=3.0, step=0.5)
    
    # Nouvelle logique simple : 16h - temps écran
    vie_gagnee = 16 - phone
    st.info(f"✨ Tu as vécu **{vie_gagnee} heures** pour toi aujourd'hui.")
    
    # Point gagné si moins de 3h (ou autre limite que tu veux)
    if phone < 3:
        objectifs_attains += 1
        st.caption("✅ Objectif < 3h validé")
    else:
        st.caption("❌ Trop d'écran")

    st.write("### 🧠 Esprit")
    c4 = st.checkbox("📖 Lecture (Min 10 pages)")
    c5 = st.checkbox("🙏 Prière / Méditation")
    
    if c4: objectifs_attains += 1
    if c5: objectifs_attains += 1

# >>> ONGLET 3 : EMPIRE <<<
with t3:
    st.write("### 👾 Twitch & Finance")
    twitch = st.number_input("Abonnés Twitch", value=11, step=1)
    
    c6 = st.checkbox("🔴 Action Twitch faite")
    c7 = st.checkbox("💰 Check Finance & 0 Dépense")
    
    if c6: objectifs_attains += 1
    if c7: objectifs_attains += 1

# --- REMPLISSAGE DU HAUT DE PAGE (Maintenant qu'on a les calculs) ---
with header_placeholder:
    st.markdown('<div class="big-title">BLISHKO MINDSET</div>', unsafe_allow_html=True)
    
    # Calcul pourcentage
    score_pct = int((objectifs_attains / total_objectifs) * 100)
    reste_a_faire = total_objectifs - objectifs_attains
    
    # Barre de progression
    st.progress(score_pct / 100)
    
    # Message simple
    if reste_a_faire == 0:
        st.success("👑 TOUT EST FAIT. TU ES LE ROI.")
    else:
        st.warning(f"⚠️ Il te reste **{reste_a_faire} actions** à valider.")
    
    st.divider()

# --- SAUVEGARDE ---
st.write("")
note = st.text_input("Une note pour aujourd'hui ?")

if st.button("💾 SAUVEGARDER MA JOURNÉE", type="primary", use_container_width=True):
    if repo:
        today = str(date.today())
        # Vérif doublon
        if not df.empty and today in df["Date"].values:
            st.error("Déjà enregistré aujourd'hui ! Reviens demain.")
        else:
            new_data = {
                "Date": today,
                "Score": score_pct,
                "Phone": phone,
                "Weight": weight,
                "Twitch": twitch,
                "Note": note
            }
            save_data(repo, contents, df, new_data)
            st.balloons()
            st.success("✅ Validé !")
    else:
        st.error("Erreur connexion GitHub (Vérifie tes Secrets)")

# --- VISUALISATION RAPIDE ---
if not df.empty:
    with st.expander("📊 Voir mes courbes"):
        st.line_chart(df.set_index("Date")["Score"])
