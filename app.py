# app.py - Blishko's Mindset (version finale)
# Copie-colle ce fichier et lance : streamlit run app.py

import streamlit as st
import pandas as pd
from github import Github
from io import StringIO
from datetime import datetime, timedelta
import pytz
import plotly.graph_objects as go
import random
from typing import Optional, Any, Tuple
import os
import logging

# ---------------------------
# LOGGING (utile pour debug si besoin)
# ---------------------------
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("blishko")

# ---------------------------
# CONFIG PAGE
# ---------------------------
st.set_page_config(page_title="Blishko’s Mindset", page_icon="💪", layout="centered", initial_sidebar_state="collapsed")

# ---------------------------
# SIDEBAR SETTINGS (modifiable)
# ---------------------------
st.sidebar.header("Paramètres")
INVEST_STOCKS = st.sidebar.number_input("Investi en bourse (initial)", value=50.0, step=1.0, format="%.2f")
INVEST_CRYPTO = st.sidebar.number_input("Investi en crypto (initial)", value=96.0, step=1.0, format="%.2f")
RETENTION_DAYS = int(st.sidebar.number_input("Durée de conservation (jours)", value=365, step=1))
st.sidebar.caption("Si tu veux sauvegarder sur GitHub, ajoute GITHUB_TOKEN et REPO_NAME dans st.secrets.")

# ---------------------------
# STYLE CSS (iOS-like, barre large)
# ---------------------------
st.markdown("""
<style>
:root { --bg:#000; --card:#1C1C1E; --card2:#2C2C2E; --muted:#8E8E93; --accent:#0A84FF; --good:#32D74B; --bad:#FF453A; --radius:16px; --font:-apple-system, BlinkMacSystemFont, "SF Pro Display", sans-serif; }
body {background:var(--bg); color:#fff; font-family:var(--font);}
.stApp {padding:18px;}
.card {background: linear-gradient(145deg, var(--card) 0%, var(--card2) 100%); border-radius:var(--radius); padding:18px; margin-bottom:14px; border:1px solid #2A2A2C;}
.header-title {text-align:center; font-size:44px; margin-bottom:6px; font-weight:800;}
.header-sub {text-align:center; color:var(--muted); margin-top:0; margin-bottom:10px;}
.progress-wrap {width:100%; background:#0b0b0b; border-radius:14px; padding:8px; margin-bottom:12px; box-shadow: inset 0 0 8px rgba(0,0,0,0.6);}
.progress-bar {height:20px; background:linear-gradient(90deg,#0A84FF,#0066CC); border-radius:12px; width:0%; display:flex; align-items:center; justify-content:center; color:#fff; font-weight:700;}
.quote {font-style:italic; font-size:16px; color:#FFFFFF; margin:6px 0;}
.quote-author {font-weight:700; color:#FFFFFF; margin-left:8px;}
.metric {padding:8px; border-radius:12px; text-align:center;}
.metric-value {font-size:26px; font-weight:800; color:var(--accent);}
.metric-label {font-size:13px; color:var(--muted);}
.small {font-size:13px; color:var(--muted);}
hr {border-color:#2A2A2C;}
</style>
""", unsafe_allow_html=True)

# ---------------------------
# CITATIONS (texte, auteur connu)
# ---------------------------
QUOTES = [
    ("La discipline est le pont entre les objectifs et les réalisations.", "Jim Rohn"),
    ("Le progrès, même petit, est toujours progrès.", "James Clear"),
    ("La constance bat le talent quand le talent ne travaille pas.", "Ryan Holiday"),
    ("Fais ce que tu dois faire aujourd'hui pour que demain soit plus simple.", "David Goggins"),
    ("Reste humble, travaille dur, sois patient.", "Naval Ravikant"),
    ("Ne cherche pas à être meilleur que les autres, cherche à être meilleur que toi-même.", "Jordan Peterson"),
    ("Les habitudes façonnent le destin.", "Aristote")
]

def quote_of_day(date: datetime) -> Tuple[str,str]:
    seed = int(date.strftime("%Y%m%d"))
    random.seed(seed)
    return random.choice(QUOTES)

# ---------------------------
# GITHUB HELPERS (lecture/écriture)
# ---------------------------
@st.cache_resource
def init_github() -> Optional[Any]:
    try:
        token = st.secrets["GITHUB_TOKEN"]
        repo_name = st.secrets["REPO_NAME"]
        g = Github(token)
        repo = g.get_repo(repo_name)
        logger.info("Connexion GitHub OK")
        return repo
    except Exception as e:
        logger.info("GitHub non configuré ou erreur de connexion")
        return None

def ensure_columns(df: pd.DataFrame) -> pd.DataFrame:
    cols = ["Date","XP","Phone","Weight","Stocks","Crypto","Expenses","Twitch","School","Finance","Prayer","Reading","Sport","Hygiene","Budget"]
    for c in cols:
        if c not in df.columns:
            df[c] = 0
    if "Date" in df.columns:
        df["Date"] = pd.to_datetime(df["Date"], errors="coerce")
    return df[cols]

def load_data(repo) -> Tuple[pd.DataFrame, Optional[Any]]:
    # Try GitHub first if configured, otherwise local fallback
    if repo:
        try:
            contents = repo.get_contents("data_2026.csv")
            df = pd.read_csv(StringIO(contents.decoded_content.decode("utf-8")))
            df = ensure_columns(df)
            return df, contents
        except Exception as e:
            logger.info("Pas de fichier sur GitHub ou erreur lecture, fallback local")
    try:
        df = pd.read_csv("data_2026.csv")
        df = ensure_columns(df)
        return df, None
    except Exception:
        return ensure_columns(pd.DataFrame()), None

def save_data(repo, df: pd.DataFrame, contents=None) -> bool:
    csv_content = df.to_csv(index=False)
    if repo:
        try:
            if contents:
                repo.update_file("data_2026.csv", f"Update {datetime.utcnow().isoformat()}", csv_content, contents.sha)
            else:
                repo.create_file("data_2026.csv", "Initial commit - Blishko's Mindset", csv_content)
            return True
        except Exception as e:
            logger.warning("Échec sauvegarde GitHub, tentative locale")
            # fallback to local
    try:
        with open("data_2026.csv", "w", encoding="utf-8") as f:
            f.write(csv_content)
        return True
    except Exception as e:
        logger.error("Échec sauvegarde locale: %s", e)
        return False

# ---------------------------
# BACKUP & PURGE (automatique unique)
# ---------------------------
def make_empty_df() -> pd.DataFrame:
    cols = ["Date","XP","Phone","Weight","Stocks","Crypto","Expenses","Twitch","School","Finance","Prayer","Reading","Sport","Hygiene","Budget"]
    return pd.DataFrame(columns=cols)

def backup_and_clear(repo, contents, df, tz, retention_start):
    """
    Sauvegarde un backup (GitHub si possible, sinon local) puis remplace data_2026.csv par un fichier vide.
    Retourne (success: bool, message: str).
    """
    timestamp = datetime.now(tz).strftime("%Y%m%d_%H%M%S")
    backup_name = f"data_2026_backup_{timestamp}.csv"
    csv_content = df.to_csv(index=False)

    # Try GitHub backup if repo available
    if repo:
        try:
            # create backup file in repo (unique name)
            repo.create_file(backup_name, f"Backup before purge {timestamp}", csv_content)
            # replace main data file with empty template
            empty_csv = make_empty_df().to_csv(index=False)
            if contents:
                repo.update_file("data_2026.csv", f"Reset data after backup {timestamp}", empty_csv, contents.sha)
            else:
                repo.create_file("data_2026.csv", f"Reset data after backup {timestamp}", empty_csv)
            return True, f"Backup GitHub créé : {backup_name} ; données réinitialisées."
        except Exception as e:
            logger.warning("Backup GitHub échoué: %s", e)
            # fallback to local

    # Local backup fallback
    try:
        local_backup_path = backup_name
        with open(local_backup_path, "w", encoding="utf-8") as f:
            f.write(csv_content)
        # overwrite local data file with empty template
        make_empty_df().to_csv("data_2026.csv", index=False)
        return True, f"Backup local créé : {local_backup_path} ; données locales réinitialisées."
    except Exception as e:
        logger.error("Échec backup local: %s", e)
        return False, f"Échec backup local : {e}"

# ---------------------------
# CHART HELPERS (marqueurs réduits, flèche rouge)
# ---------------------------
MARKER_SIZE = 4  # petits carrés comme demandé

def line_chart_with_arrow(df: pd.DataFrame, x_col: str, y_col: str, title: str, color: str = "#0A84FF", target: Optional[float]=None):
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=df[x_col],
        y=df[y_col],
        mode='lines+markers',
        line=dict(color=color, width=3),
        marker=dict(size=MARKER_SIZE, symbol='square', color=color),
        name=title
    ))
    if len(df) >= 2:
        x0 = df[x_col].iloc[-2]; y0 = df[y_col].iloc[-2]
        x1 = df[x_col].iloc[-1]; y1 = df[y_col].iloc[-1]
        fig.add_shape(type="line", x0=x0, y0=y0, x1=x1, y1=y1, line=dict(color="#FF453A", width=2))
        fig.add_annotation(x=x1, y=y1, ax=x0, ay=y0, showarrow=True, arrowhead=3, arrowsize=1.2, arrowcolor="#FF453A", arrowwidth=2)
    if target is not None:
        fig.add_hline(y=target, line_dash="dash", line_color="#FF453A", annotation_text=f"Target: {target}", annotation_position="top right")
    fig.update_layout(title=title, plot_bgcolor='#1C1C1E', paper_bgcolor='#000000', font=dict(color='#FFFFFF', family='-apple-system'), xaxis=dict(gridcolor='#2C2C2E'), yaxis=dict(gridcolor='#2C2C2E'), margin=dict(l=20,r=20,t=50,b=20))
    return fig

def bar_with_small_squares(df: pd.DataFrame, x_col: str, y_col: str, title: str, bar_color: str = "#FFD60A", square_color: str = "#FF453A"):
    fig = go.Figure()
    fig.add_trace(go.Bar(x=df[x_col], y=df[y_col], name=title, marker=dict(color=bar_color)))
    fig.add_trace(go.Scatter(x=df[x_col], y=df[y_col], mode='markers', marker=dict(symbol='square', size=MARKER_SIZE, color=square_color), name='points'))
    fig.update_layout(title=title, plot_bgcolor='#1C1C1E', paper_bgcolor='#000000', font=dict(color='#FFFFFF', family='-apple-system'), xaxis=dict(gridcolor='#2C2C2E'), yaxis=dict(gridcolor='#2C2C2E'), margin=dict(l=20,r=20,t=50,b=20))
    return fig

# ---------------------------
# UTIL & INITIAL STATE
# ---------------------------
tz = pytz.timezone("Europe/Paris")
now = datetime.now(tz)
today_str = now.strftime("%Y-%m-%d")

# retention start: today at 20:00 (Europe/Paris)
today_local = now.date()
RETENTION_START = tz.localize(datetime(today_local.year, today_local.month, today_local.day, 20, 0, 0))
RETENTION_END = RETENTION_START + timedelta(days=RETENTION_DAYS)

# session flags
if "auto_purge_done" not in st.session_state:
    st.session_state["auto_purge_done"] = False
if "purge_done" not in st.session_state:
    st.session_state["purge_done"] = False

# init GitHub (optional)
repo = init_github()
df, contents = load_data(repo)

# --- Purge once at first run: backup existing data and clear it so the app starts clean ---
# This executes once per session when the app is first launched after you paste this file.
# It creates a backup file (GitHub if configured, otherwise local) and replaces data_2026.csv with an empty template.
if (not st.session_state["purge_done"]):
    # Only perform purge if there is existing data (non-empty) to backup/clear.
    try:
        if df is not None and not df.empty:
            success, msg = backup_and_clear(repo, contents, df, tz, RETENTION_START)
            if success:
                logger.info("Backup and clear done: %s", msg)
            else:
                logger.warning("Backup failed: %s", msg)
            # reload after backup/clear
            df, contents = load_data(repo)
        else:
            # ensure empty file exists locally if none
            make_empty_df().to_csv("data_2026.csv", index=False)
        st.session_state["purge_done"] = True
    except Exception as e:
        logger.exception("Erreur lors de la purge initiale: %s", e)
        st.session_state["purge_done"] = True  # avoid blocking the app

# ---------------------------
# HEADER + BARRE DE PROGRESSION (précision 0,01)
# ---------------------------
st.markdown(f"<div class='header-title'>Blishko’s Mindset</div>", unsafe_allow_html=True)
st.markdown(f"<p class='header-sub'>{now.strftime('%A %d %B %Y')}</p>", unsafe_allow_html=True)

# percentage of year 2026 elapsed relative to 2026-12-31 23:59:59
start_2026 = tz.localize(datetime(2026,1,1,0,0,0))
end_2026 = tz.localize(datetime(2026,12,31,23,59,59))
now_clamped = min(max(now, start_2026), end_2026)
total_seconds = (end_2026 - start_2026).total_seconds()
elapsed_seconds = (now_clamped - start_2026).total_seconds()
fraction = elapsed_seconds / total_seconds if total_seconds > 0 else 0.0
percent = fraction * 100.0
percent_display = f"{percent:.2f}".replace(".", ",") + "%"
progress_html = f"""
<div class="progress-wrap">
  <div class="progress-bar" style="width:{percent:.2f}%;">{percent:.2f}%</div>
</div>
<p style="text-align:center; color:#8E8E93; margin-top:6px;">Année 2026 écoulée : <strong style="color:#FFFFFF">{percent_display}</strong></p>
"""
st.markdown(progress_html, unsafe_allow_html=True)

# ---------------------------
# QUOTE (sans label, italique + auteur connu)
# ---------------------------
q_text, q_author = quote_of_day(now)
st.markdown(f"<div class='card'><p class='quote'>“{q_text}” <span class='quote-author'>— {q_author}</span></p></div>", unsafe_allow_html=True)

# ---------------------------
# TABS
# ---------------------------
tab_journal, tab_stats = st.tabs(["📝 JOURNAL", "📊 STATISTIQUES"])

# ---------------------------
# JOURNAL TAB (inputs journaliers)
# ---------------------------
with tab_journal:
    st.markdown("<div class='card'>", unsafe_allow_html=True)
    st.markdown("<div style='font-weight:700; font-size:18px; margin-bottom:8px;'>Habitudes & Finances</div>", unsafe_allow_html=True)

    col1, col2 = st.columns([2,1])
    with col1:
        phone = st.number_input("Heures d'écran aujourd'hui", min_value=0.0, max_value=24.0, value=3.0, step=0.25, key="phone")
        stocks = st.number_input("Gain/perte Bourse aujourd'hui (€)", value=0.0, step=0.5, format="%.2f", key="stocks")
        crypto = st.number_input("Gain/perte Crypto aujourd'hui (€)", value=0.0, step=0.5, format="%.2f", key="crypto")
        expenses = st.number_input("Dépenses aujourd'hui (€)", min_value=0.0, value=0.0, step=0.5, format="%.2f", key="expenses")
        twitch_default = int(df["Twitch"].iloc[-1]) if (df is not None and not df.empty) else 0
        twitch = st.number_input("Abonnés Twitch", min_value=0, value=twitch_default, step=1, key="twitch")
    with col2:
        st.markdown("<div class='metric'><div class='metric-value'>—</div><div class='metric-label'>Score (après enregistrement)</div></div>", unsafe_allow_html=True)
        st.caption("Le score de discipline sera calculé à l'enregistrement.")
    st.markdown("<hr>", unsafe_allow_html=True)

    habits = {
        "School":"Travail/Étude fait",
        "Finance":"Finance checkée",
        "Prayer":"Prière",
        "Reading":"Lecture",
        "Sport":"Sport complet",
        "Hygiene":"Hygiène & chambre",
        "Budget":"Zéro dépense inutile"
    }
    toggles = {}
    for k, label in habits.items():
        toggles[k] = st.checkbox(label, key=f"chk_{k}")

    weight = st.number_input("Poids (kg) - entre quand tu veux", min_value=0.0, max_value=300.0, value=0.0, step=0.1, key="weight")
    st.markdown("</div>", unsafe_allow_html=True)

    # ENREGISTREMENT
    if st.button("💾 Enregistrer la journée", type="primary"):
        toggles_list = [int(toggles[k]) for k in habits.keys()]
        phone_goal_ok = 1 if phone <= 3.0 else 0
        xp = int((sum(toggles_list) + phone_goal_ok) / (len(toggles_list) + 1) * 100)
        new_row = {
            "Date": today_str,
            "XP": xp,
            "Phone": phone,
            "Weight": weight,
            "Stocks": float(stocks),
            "Crypto": float(crypto),
            "Expenses": float(expenses),
            "Twitch": int(twitch),
            **{k: int(v) for k, v in toggles.items()}
        }

        # upsert
        if df is None or df.empty:
            df = pd.DataFrame([new_row])
        else:
            if today_str in df["Date"].astype(str).values:
                df.loc[df["Date"].astype(str) == today_str, list(new_row.keys())] = list(new_row.values())
            else:
                df = pd.concat([df, pd.DataFrame([new_row])], ignore_index=True)

        # purge automatique au premier enregistrement après RETENTION_START (si applicable)
        now_local = datetime.now(tz)
        if (not st.session_state["auto_purge_done"]) and (now_local >= RETENTION_START):
            # purge old test data older than RETENTION_START
            try:
                df["Date"] = pd.to_datetime(df["Date"], errors="coerce")
                df = df[df["Date"] >= RETENTION_START].reset_index(drop=True)
            except Exception:
                pass
            st.session_state["auto_purge_done"] = True

        df = ensure_columns(df)
        df["Date"] = pd.to_datetime(df["Date"])
        df = df.sort_values("Date").reset_index(drop=True)

        if save_data(repo, df, contents):
            st.success(f"Journée enregistrée — Score {xp}%")
            # RÉCAPITULATIF IA (comparaison simple et directe)
            st.markdown("<br>", unsafe_allow_html=True)
            st.markdown("<div style='background:linear-gradient(135deg,#111 0%, #222 100%); padding:16px; border-radius:12px;'>", unsafe_allow_html=True)
            st.markdown("<h3 style='margin-top:0;'>Récapitulatif</h3>", unsafe_allow_html=True)

            # trouver la ligne d'hier si existante
            yesterday_row = None
            if len(df) >= 2:
                # on suppose que la dernière ligne est aujourd'hui
                yesterday_row = df.iloc[-2]

            analysis_lines = []
            analysis_lines.append(f"Ton score de discipline aujourd'hui est **{xp}%**.")

            if yesterday_row is not None:
                # téléphone
                phone_diff = phone - float(yesterday_row.get("Phone", 0))
                if phone_diff < 0:
                    analysis_lines.append(f"Temps d'écran: **{phone}h**, {abs(phone_diff):.2f}h de moins que la veille — bonne amélioration.")
                elif phone_diff > 0:
                    analysis_lines.append(f"Temps d'écran: **{phone}h**, {phone_diff:.2f}h de plus que la veille — attention.")
                else:
                    analysis_lines.append(f"Temps d'écran: **{phone}h**, identique à la veille.")

                # finances net aujourd'hui vs hier
                today_net = float(new_row.get("Stocks",0)) + float(new_row.get("Crypto",0))
                yesterday_net = float(yesterday_row.get("Stocks",0)) + float(yesterday_row.get("Crypto",0))
                net_diff = today_net - yesterday_net
                if net_diff > 0:
                    analysis_lines.append(f"Finances: gain net aujourd'hui **{today_net:.2f}€**, soit **{net_diff:.2f}€** de mieux que la veille.")
                elif net_diff < 0:
                    analysis_lines.append(f"Finances: gain net aujourd'hui **{today_net:.2f}€**, soit **{abs(net_diff):.2f}€** de moins que la veille.")
                else:
                    analysis_lines.append(f"Finances: **{today_net:.2f}€**, identique à la veille.")

                # dépenses
                expenses_diff = float(new_row.get("Expenses",0)) - float(yesterday_row.get("Expenses",0))
                if expenses_diff > 0:
                    analysis_lines.append(f"Dépenses: **{new_row['Expenses']:.2f}€**, {expenses_diff:.2f}€ de plus que la veille.")
                elif expenses_diff < 0:
                    analysis_lines.append(f"Dépenses: **{new_row['Expenses']:.2f}€**, {abs(expenses_diff):.2f}€ de moins que la veille.")
                else:
                    analysis_lines.append(f"Dépenses: **{new_row['Expenses']:.2f}€**, identiques à la veille.")

                # comparaison du score global
                yesterday_xp = int(yesterday_row.get("XP",0))
                if xp > yesterday_xp:
                    analysis_lines.append(f"Ton score est **meilleur** qu'hier ({xp}% vs {yesterday_xp}%).")
                elif xp < yesterday_xp:
                    analysis_lines.append(f"Ton score est **moins bon** qu'hier ({xp}% vs {yesterday_xp}%).")
                else:
                    analysis_lines.append(f"Ton score est **identique** à hier ({xp}%).")
            else:
                analysis_lines.append("Aucune donnée précédente pour comparer (première entrée ou pas assez d'historique).")

            for line in analysis_lines:
                st.markdown(f"- {line}", unsafe_allow_html=True)
            st.markdown("</div>", unsafe_allow_html=True)

            # recharger
            df, contents = load_data(repo)
        else:
            st.error("Erreur lors de la sauvegarde. Vérifie GITHUB_TOKEN / REPO_NAME ou les permissions d'écriture, ou l'accès au fichier local.")

# ---------------------------
# STATISTICS TAB
# ---------------------------
with tab_stats:
    st.markdown("<div class='card'>", unsafe_allow_html=True)
    st.markdown("<div style='font-weight:700; font-size:18px; margin-bottom:8px;'>Statistiques financières & habitudes</div>", unsafe_allow_html=True)
    if df is None or df.empty or len(df) < 1:
        st.info("Aucune donnée disponible. Remplis ton journal pour voir les graphiques.")
    else:
        df = df.copy()
        df["Date"] = pd.to_datetime(df["Date"])
        df = df.sort_values("Date")

        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.markdown(f"<div class='metric'><div class='metric-value'>{df['XP'].mean():.0f}%</div><div class='metric-label'>XP moyen</div></div>", unsafe_allow_html=True)
        with col2:
            avg_phone = df["Phone"].mean()
            color = "#32D74B" if avg_phone <= 3 else "#FF453A"
            st.markdown(f"<div class='metric'><div class='metric-value' style='color:{color}'>{avg_phone:.1f}h</div><div class='metric-label'>Écran moyen</div></div>", unsafe_allow_html=True)
        with col3:
            net_gain = df["Stocks"].sum() + df["Crypto"].sum()
            color_net = "#32D74B" if net_gain >= 0 else "#FF453A"
            st.markdown(f"<div class='metric'><div class='metric-value' style='color:{color_net}'>{net_gain:.2f}€</div><div class='metric-label'>Gain net depuis le début</div></div>", unsafe_allow_html=True)
        with col4:
            total_expenses = df["Expenses"].sum()
            st.markdown(f"<div class='metric'><div class='metric-value'>{total_expenses:.2f}€</div><div class='metric-label'>Dépenses totales</div></div>", unsafe_allow_html=True)

        st.markdown("<hr>", unsafe_allow_html=True)

        # Bourse
        st.markdown("### 💹 Bourse (gain/perte journalier)")
        df_stock = df[["Date","Stocks"]].copy()
        df_stock["MA7"] = df_stock["Stocks"].rolling(7, min_periods=1).mean()
        fig_stock = go.Figure()
        fig_stock.add_trace(go.Bar(x=df_stock["Date"], y=df_stock["Stocks"], name="Journalier", marker_color="#0A84FF"))
        fig_stock.add_trace(go.Scatter(x=df_stock["Date"], y=df_stock["MA7"], name="MA7", line=dict(color="#32D74B", width=3), marker=dict(size=MARKER_SIZE, symbol='square', color="#32D74B")))
        fig_stock.add_trace(go.Scatter(x=df_stock["Date"], y=df_stock["Stocks"], mode='markers', marker=dict(symbol='square', size=MARKER_SIZE, color="#FF453A"), name='points'))
        if len(df_stock) >= 2:
            x0 = df_stock["Date"].iloc[-2]; y0 = df_stock["Stocks"].iloc[-2]
            x1 = df_stock["Date"].iloc[-1]; y1 = df_stock["Stocks"].iloc[-1]
            fig_stock.add_shape(type="line", x0=x0, y0=y0, x1=x1, y1=y1, line=dict(color="#FF453A", width=2))
            fig_stock.add_annotation(x=x1, y=y1, ax=x0, ay=y0, showarrow=True, arrowhead=3, arrowcolor="#FF453A", arrowwidth=2)
        fig_stock.update_layout(plot_bgcolor='#1C1C1E', paper_bgcolor='#000000', font=dict(color='#FFFFFF'))
        st.plotly_chart(fig_stock, use_container_width=True)

        # Crypto
        st.markdown("### 🔥 Crypto (gain/perte journalier)")
        df_crypto = df[["Date","Crypto"]].copy()
        df_crypto["MA7"] = df_crypto["Crypto"].rolling(7, min_periods=1).mean()
        fig_crypto = go.Figure()
        fig_crypto.add_trace(go.Bar(x=df_crypto["Date"], y=df_crypto["Crypto"], name="Journalier", marker_color="#BF5AF2"))
        fig_crypto.add_trace(go.Scatter(x=df_crypto["Date"], y=df_crypto["MA7"], name="MA7", line=dict(color="#0A84FF", width=3), marker=dict(size=MARKER_SIZE, symbol='square', color="#0A84FF")))
        fig_crypto.add_trace(go.Scatter(x=df_crypto["Date"], y=df_crypto["Crypto"], mode='markers', marker=dict(symbol='square', size=MARKER_SIZE, color="#FF453A"), name='points'))
        if len(df_crypto) >= 2:
            x0 = df_crypto["Date"].iloc[-2]; y0 = df_crypto["Crypto"].iloc[-2]
            x1 = df_crypto["Date"].iloc[-1]; y1 = df_crypto["Crypto"].iloc[-1]
            fig_crypto.add_shape(type="line", x0=x0, y0=y0, x1=x1, y1=y1, line=dict(color="#FF453A", width=2))
            fig_crypto.add_annotation(x=x1, y=y1, ax=x0, ay=y0, showarrow=True, arrowhead=3, arrowcolor="#FF453A", arrowwidth=2)
        fig_crypto.update_layout(plot_bgcolor='#1C1C1E', paper_bgcolor='#000000', font=dict(color='#FFFFFF'))
        st.plotly_chart(fig_crypto, use_container_width=True)

        # Dépenses
        st.markdown("### 🧾 Dépenses quotidiennes")
        fig_exp = bar_with_small_squares(df, "Date", "Expenses", "Dépenses", bar_color="#FF453A", square_color="#FFFFFF")
        st.plotly_chart(fig_exp, use_container_width=True)

        # Poids
        st.markdown("### ⚖️ Évolution du poids")
        df_w = df[df["Weight"] > 0]
        if not df_w.empty:
            st.plotly_chart(line_chart_with_arrow(df_w, "Date", "Weight", "Poids (kg)", color="#32D74B"), use_container_width=True)
        else:
            st.info("Aucune donnée de poids enregistrée pour l'instant.")

        # ROI & investissements
        st.markdown("<hr>", unsafe_allow_html=True)
        st.markdown("#### 💰 Investissements & ROI")
        invested_total = INVEST_STOCKS + INVEST_CRYPTO
        roi_text = "N/A"
        if invested_total > 0:
            roi = (net_gain / invested_total) * 100
            roi_text = f"{roi:.2f}%"
        st.markdown(f"- Investi en bourse : **{INVEST_STOCKS:.2f}€**")
        st.markdown(f"- Investi en crypto : **{INVEST_CRYPTO:.2f}€**")
        st.markdown(f"- Gain net depuis le début : **{net_gain:.2f}€**")
        st.markdown(f"- ROI simple : **{roi_text}**")

        # Taux de réussite
        st.markdown("<hr>", unsafe_allow_html=True)
        st.markdown("#### Taux de réussite par catégorie")
        rates = {}
        for k in ["School","Finance","Prayer","Reading","Sport","Hygiene","Budget"]:
            if k in df.columns:
                rates[k] = df[k].sum() / len(df) * 100
        cols = st.columns(len(rates))
        for (name, val), col in zip(rates.items(), cols):
            col.metric(label=name, value=f"{val:.0f}%")

    st.markdown("</div>", unsafe_allow_html=True)
