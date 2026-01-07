# app.py - Blishko's Mindset (initialisation unique + persistance à partir du premier enregistrement)
# Usage : streamlit run app.py
import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import pytz
import plotly.graph_objects as go
import random
from typing import Optional, Any, Tuple
from io import StringIO
from github import Github
import os
import logging

# ---------------------------
# Logging
# ---------------------------
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("blishko")

# ---------------------------
# Page config
# ---------------------------
st.set_page_config(page_title="Blishko’s Mindset", page_icon="💪", layout="centered", initial_sidebar_state="collapsed")

# ---------------------------
# Sidebar settings
# ---------------------------
st.sidebar.header("Paramètres")
INVEST_STOCKS = st.sidebar.number_input("Investi en bourse (initial)", value=50.0, step=1.0, format="%.2f")
INVEST_CRYPTO = st.sidebar.number_input("Investi en crypto (initial)", value=96.0, step=1.0, format="%.2f")
RETENTION_DAYS = int(st.sidebar.number_input("Durée de conservation (jours)", value=365, step=1))
st.sidebar.caption("Ajoute GITHUB_TOKEN et REPO_NAME dans st.secrets pour sauvegarder sur GitHub (optionnel).")

# ---------------------------
# Constants & helpers
# ---------------------------
tz = pytz.timezone("Europe/Paris")
now = datetime.now(tz)
today_str = now.strftime("%Y-%m-%d")
DATA_FILENAME = "data_2026.csv"
INIT_FLAG = "initialized.flag"  # marqueur local indiquant que la purge initiale a été faite
MARKER_SIZE = 4  # taille des carrés sur les graphiques

def cols_list():
    return ["Date","XP","Phone","Weight","Stocks","Crypto","Expenses","Twitch","School","Finance","Prayer","Reading","Sport","Hygiene","Budget"]

def make_empty_df():
    return pd.DataFrame(columns=cols_list())

# ---------------------------
# GitHub helpers (optionnel)
# ---------------------------
def init_github() -> Optional[Any]:
    try:
        token = st.secrets["GITHUB_TOKEN"]
        repo_name = st.secrets["REPO_NAME"]
        g = Github(token)
        repo = g.get_repo(repo_name)
        logger.info("GitHub initialisé")
        return repo
    except Exception:
        logger.info("GitHub non configuré ou inaccessible")
        return None

def read_repo_file(repo, path):
    try:
        contents = repo.get_contents(path)
        return contents
    except Exception:
        return None

def create_repo_file(repo, path, content, message):
    try:
        repo.create_file(path, message, content)
        return True
    except Exception as e:
        logger.warning("create_repo_file failed: %s", e)
        return False

def update_repo_file(repo, path, content, message, sha):
    try:
        repo.update_file(path, message, content, sha)
        return True
    except Exception as e:
        logger.warning("update_repo_file failed: %s", e)
        return False

# ---------------------------
# Load / Save data (GitHub preferred, fallback local)
# ---------------------------
def ensure_columns(df: pd.DataFrame) -> pd.DataFrame:
    for c in cols_list():
        if c not in df.columns:
            df[c] = 0
    if "Date" in df.columns:
        df["Date"] = pd.to_datetime(df["Date"], errors="coerce")
    return df[cols_list()]

def load_data(repo) -> Tuple[pd.DataFrame, Optional[Any]]:
    # Try GitHub first
    if repo:
        contents = read_repo_file(repo, DATA_FILENAME)
        if contents:
            try:
                df = pd.read_csv(StringIO(contents.decoded_content.decode("utf-8")))
                df = ensure_columns(df)
                return df, contents
            except Exception:
                pass
    # Fallback local
    if os.path.exists(DATA_FILENAME):
        try:
            df = pd.read_csv(DATA_FILENAME)
            df = ensure_columns(df)
            return df, None
        except Exception:
            pass
    # default empty
    return ensure_columns(pd.DataFrame()), None

def save_data(repo, df: pd.DataFrame, contents=None) -> bool:
    csv_content = df.to_csv(index=False)
    # Try GitHub
    if repo:
        try:
            if contents:
                repo.update_file(DATA_FILENAME, f"Update {datetime.utcnow().isoformat()}", csv_content, contents.sha)
            else:
                repo.create_file(DATA_FILENAME, "Initial commit - Blishko's Mindset", csv_content)
            return True
        except Exception as e:
            logger.warning("Sauvegarde GitHub échouée: %s", e)
    # Fallback local
    try:
        with open(DATA_FILENAME, "w", encoding="utf-8") as f:
            f.write(csv_content)
        return True
    except Exception as e:
        logger.error("Sauvegarde locale échouée: %s", e)
        return False

# ---------------------------
# Backup + initial clear (one-time)
# ---------------------------
def backup_and_clear_initial(repo, contents, df, tz):
    """
    Sauvegarde un backup (GitHub si possible, sinon local) puis remplace data_2026.csv par un fichier vide.
    Crée le flag INIT_FLAG localement ou sur repo pour indiquer que l'initialisation a été faite.
    """
    timestamp = datetime.now(tz).strftime("%Y%m%d_%H%M%S")
    backup_name = f"data_2026_backup_{timestamp}.csv"
    csv_content = df.to_csv(index=False)

    # Try GitHub backup
    if repo:
        try:
            # create backup file in repo
            repo.create_file(backup_name, f"Backup before initial clear {timestamp}", csv_content)
            # replace main data file with empty template
            empty_csv = make_empty_df().to_csv(index=False)
            if contents:
                repo.update_file(DATA_FILENAME, f"Reset data after backup {timestamp}", empty_csv, contents.sha)
            else:
                repo.create_file(DATA_FILENAME, f"Reset data after backup {timestamp}", empty_csv)
            # create flag file in repo
            repo.create_file(INIT_FLAG, f"Init flag {timestamp}", "initialized")
            return True, f"Backup GitHub créé : {backup_name} ; données réinitialisées."
        except Exception as e:
            logger.warning("Backup GitHub échoué: %s", e)

    # Local backup fallback
    try:
        local_backup_path = backup_name
        with open(local_backup_path, "w", encoding="utf-8") as f:
            f.write(csv_content)
        # overwrite local data file with empty template
        make_empty_df().to_csv(DATA_FILENAME, index=False)
        # create local flag
        with open(INIT_FLAG, "w", encoding="utf-8") as f:
            f.write("initialized")
        return True, f"Backup local créé : {local_backup_path} ; données locales réinitialisées."
    except Exception as e:
        logger.error("Échec backup local: %s", e)
        return False, f"Échec backup local : {e}"

def check_initialized(repo) -> bool:
    # Check local flag first
    if os.path.exists(INIT_FLAG):
        return True
    # If repo configured, check for flag file in repo
    if repo:
        contents = read_repo_file(repo, INIT_FLAG)
        if contents:
            return True
    return False

# ---------------------------
# Chart helpers
# ---------------------------
def line_chart_with_arrow(df: pd.DataFrame, x_col: str, y_col: str, title: str, color: str = "#0A84FF", target: Optional[float]=None):
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=df[x_col], y=df[y_col], mode='lines+markers', line=dict(color=color, width=3), marker=dict(size=MARKER_SIZE, symbol='square', color=color), name=title))
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
# Main initialization logic
# ---------------------------
repo = init_github()
df, contents = load_data(repo)

# If not initialized yet, perform one-time backup+clear so app starts empty for you
if not check_initialized(repo):
    # Only backup/clear if there is existing data to preserve
    try:
        if df is not None and not df.empty:
            success, msg = backup_and_clear_initial(repo, contents, df, tz)
            logger.info("Initial backup/clear: %s", msg)
        else:
            # ensure empty data file exists and create local flag
            make_empty_df().to_csv(DATA_FILENAME, index=False)
            with open(INIT_FLAG, "w", encoding="utf-8") as f:
                f.write("initialized")
        # reload after clear
        df, contents = load_data(repo)
    except Exception as e:
        logger.exception("Erreur lors de l'initialisation: %s", e)
        # ensure we still create flag to avoid repeated attempts
        try:
            with open(INIT_FLAG, "w", encoding="utf-8") as f:
                f.write("initialized")
        except Exception:
            pass

# ---------------------------
# UI header + progress bar (precision 0.01)
# ---------------------------
st.markdown(f"<h1 style='text-align:center; font-size:44px; margin-bottom:6px;'>Blishko’s Mindset</h1>", unsafe_allow_html=True)
st.markdown(f"<p style='text-align:center; color:#8E8E93; margin-top:0; margin-bottom:10px;'>{now.strftime('%A %d %B %Y')}</p>", unsafe_allow_html=True)

# percentage of year 2026 elapsed
start_2026 = tz.localize(datetime(2026,1,1,0,0,0))
end_2026 = tz.localize(datetime(2026,12,31,23,59,59))
now_clamped = min(max(now, start_2026), end_2026)
total_seconds = (end_2026 - start_2026).total_seconds()
elapsed_seconds = (now_clamped - start_2026).total_seconds()
fraction = elapsed_seconds / total_seconds if total_seconds > 0 else 0.0
percent = fraction * 100.0
percent_display = f"{percent:.2f}".replace(".", ",") + "%"
progress_html = f"""
<div style='width:100%; background:#0b0b0b; border-radius:14px; padding:8px; margin-bottom:12px; box-shadow: inset 0 0 8px rgba(0,0,0,0.6);'>
  <div style='height:20px; background:linear-gradient(90deg,#0A84FF,#0066CC); border-radius:12px; width:{percent:.2f}%; display:flex; align-items:center; justify-content:center; color:#fff; font-weight:700;'>{percent:.2f}%</div>
</div>
<p style='text-align:center; color:#8E8E93; margin-top:6px;'>Année 2026 écoulée : <strong style='color:#FFFFFF'>{percent_display}</strong></p>
"""
st.markdown(progress_html, unsafe_allow_html=True)

# Quote
QUOTES = [
    ("La discipline est le pont entre les objectifs et les réalisations.", "Jim Rohn"),
    ("Le progrès, même petit, est toujours progrès.", "James Clear"),
    ("La constance bat le talent quand le talent ne travaille pas.", "Ryan Holiday"),
    ("Fais ce que tu dois faire aujourd'hui pour que demain soit plus simple.", "David Goggins"),
    ("Reste humble, travaille dur, sois patient.", "Naval Ravikant")
]
seed = int(now.strftime("%Y%m%d"))
random.seed(seed)
q_text, q_author = random.choice(QUOTES)
st.markdown(f"<div style='background:linear-gradient(145deg,#1C1C1E,#2C2C2E); padding:14px; border-radius:12px; margin-bottom:14px;'><p style='font-style:italic; margin:0;'>“{q_text}” <strong>— {q_author}</strong></p></div>", unsafe_allow_html=True)

# ---------------------------
# Tabs: Journal & Stats
# ---------------------------
tab_journal, tab_stats = st.tabs(["📝 JOURNAL", "📊 STATISTIQUES"])

# JOURNAL
with tab_journal:
    st.markdown("<div style='background:linear-gradient(145deg,#1C1C1E,#2C2C2E); padding:16px; border-radius:12px;'>", unsafe_allow_html=True)
    st.markdown("<h3 style='margin-top:0;'>Habitudes & Finances</h3>", unsafe_allow_html=True)

    col1, col2 = st.columns([2,1])
    with col1:
        phone = st.number_input("Heures d'écran aujourd'hui", min_value=0.0, max_value=24.0, value=3.0, step=0.25, key="phone")
        stocks = st.number_input("Gain/perte Bourse aujourd'hui (€)", value=0.0, step=0.5, format="%.2f", key="stocks")
        crypto = st.number_input("Gain/perte Crypto aujourd'hui (€)", value=0.0, step=0.5, format="%.2f", key="crypto")
        expenses = st.number_input("Dépenses aujourd'hui (€)", min_value=0.0, value=0.0, step=0.5, format="%.2f", key="expenses")
        twitch_default = int(df["Twitch"].iloc[-1]) if (df is not None and not df.empty) else 0
        twitch = st.number_input("Abonnés Twitch", min_value=0, value=twitch_default, step=1, key="twitch")
    with col2:
        st.markdown("<div style='text-align:center; padding:8px; border-radius:10px; background:#111;'><div style='font-size:28px; font-weight:800; color:#0A84FF;'>—</div><div style='font-size:12px; color:#8E8E93;'>Score (après enregistrement)</div></div>", unsafe_allow_html=True)
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
    cols = st.columns(3)
    for i, (k, label) in enumerate(habits.items()):
        toggles[k] = cols[i % 3].checkbox(label, key=f"chk_{k}")

    weight = st.number_input("Poids (kg) - entre quand tu veux", min_value=0.0, max_value=300.0, value=0.0, step=0.1, key="weight")
    st.markdown("</div>", unsafe_allow_html=True)

    # Save action
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

        # upsert into df
        if df is None or df.empty:
            df = pd.DataFrame([new_row])
        else:
            if today_str in df["Date"].astype(str).values:
                df.loc[df["Date"].astype(str) == today_str, list(new_row.keys())] = list(new_row.values())
            else:
                df = pd.concat([df, pd.DataFrame([new_row])], ignore_index=True)

        # ensure date dtype and sort
        df = ensure_columns(df)
        df["Date"] = pd.to_datetime(df["Date"])
        df = df.sort_values("Date").reset_index(drop=True)

        # save persistently
        saved = save_data(repo, df, contents)
        if saved:
            st.success(f"Journée enregistrée — Score {xp}%")
            # show recap analysis
            st.markdown("<br>", unsafe_allow_html=True)
            st.markdown("<div style='background:linear-gradient(135deg,#111 0%, #222 100%); padding:16px; border-radius:12px;'>", unsafe_allow_html=True)
            st.markdown("<h3 style='margin-top:0;'>Récapitulatif</h3>", unsafe_allow_html=True)

            # compare to yesterday if exists
            yesterday_row = None
            if len(df) >= 2:
                yesterday_row = df.iloc[-2]

            analysis_lines = []
            analysis_lines.append(f"Ton score de discipline aujourd'hui est **{xp}%**.")
            if yesterday_row is not None:
                phone_diff = phone - float(yesterday_row.get("Phone", 0))
                if phone_diff < 0:
                    analysis_lines.append(f"Temps d'écran: **{phone}h**, {abs(phone_diff):.2f}h de moins que la veille — bonne amélioration.")
                elif phone_diff > 0:
                    analysis_lines.append(f"Temps d'écran: **{phone}h**, {phone_diff:.2f}h de plus que la veille — attention.")
                else:
                    analysis_lines.append(f"Temps d'écran: **{phone}h**, identique à la veille.")

                today_net = float(new_row.get("Stocks",0)) + float(new_row.get("Crypto",0))
                yesterday_net = float(yesterday_row.get("Stocks",0)) + float(yesterday_row.get("Crypto",0))
                net_diff = today_net - yesterday_net
                if net_diff > 0:
                    analysis_lines.append(f"Finances: gain net aujourd'hui **{today_net:.2f}€**, soit **{net_diff:.2f}€** de mieux que la veille.")
                elif net_diff < 0:
                    analysis_lines.append(f"Finances: gain net aujourd'hui **{today_net:.2f}€**, soit **{abs(net_diff):.2f}€** de moins que la veille.")
                else:
                    analysis_lines.append(f"Finances: **{today_net:.2f}€**, identique à la veille.")

                expenses_diff = float(new_row.get("Expenses",0)) - float(yesterday_row.get("Expenses",0))
                if expenses_diff > 0:
                    analysis_lines.append(f"Dépenses: **{new_row['Expenses']:.2f}€**, {expenses_diff:.2f}€ de plus que la veille.")
                elif expenses_diff < 0:
                    analysis_lines.append(f"Dépenses: **{new_row['Expenses']:.2f}€**, {abs(expenses_diff):.2f}€ de moins que la veille.")
                else:
                    analysis_lines.append(f"Dépenses: **{new_row['Expenses']:.2f}€**, identiques à la veille.")

                yesterday_xp = int(yesterday_row.get("XP",0))
                if xp > yesterday_xp:
                    analysis_lines.append(f"Ton score est **meilleur** qu'hier ({xp}% vs {yesterday_xp}%).")
                elif xp < yesterday_xp:
                    analysis_lines.append(f"Ton score est **moins bon** qu'hier ({xp}% vs {yesterday_xp}%).")
                else:
                    analysis_lines.append(f"Ton score est **identique** à hier ({xp}%).")
            else:
                analysis_lines.append("Aucune donnée précédente pour comparer (première entrée).")

            for line in analysis_lines:
                st.markdown(f"- {line}", unsafe_allow_html=True)
            st.markdown("</div>", unsafe_allow_html=True)
            # reload df and contents
            df, contents = load_data(repo)
        else:
            st.error("Erreur lors de la sauvegarde. Vérifie GITHUB_TOKEN / REPO_NAME ou permissions d'écriture locale.")

# STATISTICS
with tab_stats:
    st.markdown("<div style='background:linear-gradient(145deg,#1C1C1E,#2C2C2E); padding:16px; border-radius:12px;'>", unsafe_allow_html=True)
    st.markdown("<h3 style='margin-top:0;'>Statistiques financières & habitudes</h3>", unsafe_allow_html=True)
    if df is None or df.empty or len(df) < 1:
        st.info("Aucune donnée disponible. Commence à saisir une journée pour que les données persistent.")
    else:
        df = df.copy()
        df["Date"] = pd.to_datetime(df["Date"])
        df = df.sort_values("Date")

        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.markdown(f"<div style='text-align:center; padding:8px; border-radius:12px;'><div style='font-size:26px; font-weight:800;'>{df['XP'].mean():.0f}%</div><div style='color:#8E8E93;'>XP moyen</div></div>", unsafe_allow_html=True)
        with col2:
            avg_phone = df["Phone"].mean()
            color = "#32D74B" if avg_phone <= 3 else "#FF453A"
            st.markdown(f"<div style='text-align:center; padding:8px; border-radius:12px;'><div style='font-size:26px; font-weight:800; color:{color};'>{avg_phone:.1f}h</div><div style='color:#8E8E93;'>Écran moyen</div></div>", unsafe_allow_html=True)
        with col3:
            net_gain = df["Stocks"].sum() + df["Crypto"].sum()
            color_net = "#32D74B" if net_gain >= 0 else "#FF453A"
            st.markdown(f"<div style='text-align:center; padding:8px; border-radius:12px;'><div style='font-size:26px; font-weight:800; color:{color_net};'>{net_gain:.2f}€</div><div style='color:#8E8E93;'>Gain net depuis le début</div></div>", unsafe_allow_html=True)
        with col4:
            total_expenses = df["Expenses"].sum()
            st.markdown(f"<div style='text-align:center; padding:8px; border-radius:12px;'><div style='font-size:26px; font-weight:800;'>{total_expenses:.2f}€</div><div style='color:#8E8E93;'>Dépenses totales</div></div>", unsafe_allow_html=True)

        st.markdown("<hr>", unsafe_allow_html=True)

        # Bourse
        st.markdown("### 💹 Bourse (gain/perte journalier)")
        df_stock = df[["Date","Stocks"]].copy()
        df_stock["MA7"] = df_stock["Stocks"].rolling(7, min_periods=1).mean()
        st.plotly_chart(bar_with_small_squares(df_stock, "Date", "Stocks", "Bourse", bar_color="#0A84FF", square_color="#FF453A"), use_container_width=True)

        # Crypto
        st.markdown("### 🔥 Crypto (gain/perte journalier)")
        df_crypto = df[["Date","Crypto"]].copy()
        df_crypto["MA7"] = df_crypto["Crypto"].rolling(7, min_periods=1).mean()
        st.plotly_chart(bar_with_small_squares(df_crypto, "Date", "Crypto", "Crypto", bar_color="#BF5AF2", square_color="#FF453A"), use_container_width=True)

        # Dépenses
        st.markdown("### 🧾 Dépenses quotidiennes")
        st.plotly_chart(bar_with_small_squares(df, "Date", "Expenses", "Dépenses", bar_color="#FF453A", square_color="#FFFFFF"), use_container_width=True)

        # Poids
        st.markdown("### ⚖️ Évolution du poids")
        df_w = df[df["Weight"] > 0]
        if not df_w.empty:
            st.plotly_chart(line_chart_with_arrow(df_w, "Date", "Weight", "Poids (kg)", color="#32D74B"), use_container_width=True)
        else:
            st.info("Aucune donnée de poids enregistrée pour l'instant.")

        # ROI
        st.markdown("<hr>", unsafe_allow_html=True)
        invested_total = INVEST_STOCKS + INVEST_CRYPTO
        roi_text = "N/A"
        if invested_total > 0:
            roi = (net_gain / invested_total) * 100
            roi_text = f"{roi:.2f}%"
        st.markdown(f"- Investi en bourse : **{INVEST_STOCKS:.2f}€**")
        st.markdown(f"- Investi en crypto : **{INVEST_CRYPTO:.2f}€**")
        st.markdown(f"- Gain net depuis le début : **{net_gain:.2f}€**")
        st.markdown(f"- ROI simple : **{roi_text}**")

    st.markdown("</div>", unsafe_allow_html=True)
