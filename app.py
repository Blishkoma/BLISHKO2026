# app.py (version mise à jour : finances séparées, dépenses, citation format auteur)
import streamlit as st
import pandas as pd
from github import Github
from io import StringIO
from datetime import datetime
import pytz
import plotly.graph_objects as go
import random
from typing import Optional, Any, Tuple

# ---------------------------
# CONFIG
# ---------------------------
st.set_page_config(page_title="High Performance 2026", page_icon="💪", layout="centered", initial_sidebar_state="collapsed")

# ---------------------------
# PARAMÈTRES FINANCIERS INITIAUX (modifiable)
# ---------------------------
INVEST_STOCKS = 50.0   # montant initial investi en bourse
INVEST_CRYPTO = 96.0   # montant initial investi en crypto

# ---------------------------
# CSS (iOS-like)
# ---------------------------
st.markdown("""
<style>
:root { --bg:#000; --card:#1C1C1E; --card2:#2C2C2E; --muted:#8E8E93; --accent:#0A84FF; --good:#32D74B; --bad:#FF453A; --radius:16px; --font:-apple-system, BlinkMacSystemFont, "SF Pro Display", sans-serif; }
body {background:var(--bg); color:#fff; font-family:var(--font);}
.stApp {padding:18px;}
.card {background: linear-gradient(145deg, var(--card) 0%, var(--card2) 100%); border-radius:var(--radius); padding:20px; margin-bottom:18px; border:1px solid #2A2A2C;}
.card-title {font-size:20px; font-weight:700; margin-bottom:12px;}
.metric {padding:10px; border-radius:12px; text-align:center;}
.metric-value {font-size:28px; font-weight:800; color:var(--accent);}
.metric-label {font-size:13px; color:var(--muted);}
.small {font-size:13px; color:var(--muted);}
hr {border-color:#2A2A2C;}
</style>
""", unsafe_allow_html=True)

# ---------------------------
# CITATIONS (texte, auteur)
# ---------------------------
QUOTES = [
    ("La discipline est le pont entre les objectifs et les réalisations.", "Jim Rohn"),
    ("Le progrès, même petit, est toujours progrès.", "Anonyme"),
    ("La constance bat le talent quand le talent ne travaille pas.", "Unknown"),
    ("Fais ce que tu dois faire aujourd'hui pour que demain soit plus simple.", "Auteur inconnu"),
    ("Reste humble, travaille dur, sois patient.", "Auteur inconnu")
]

def quote_of_day(date: datetime) -> Tuple[str,str]:
    seed = int(date.strftime("%Y%m%d"))
    random.seed(seed)
    return random.choice(QUOTES)

# ---------------------------
# GITHUB HELPERS
# ---------------------------
@st.cache_resource
def init_github() -> Optional[Any]:
    try:
        token = st.secrets["GITHUB_TOKEN"]
        repo_name = st.secrets["REPO_NAME"]
        g = Github(token)
        repo = g.get_repo(repo_name)
        return repo
    except Exception:
        st.error("Erreur connexion GitHub. Vérifie tes secrets.")
        return None

def ensure_columns(df: pd.DataFrame) -> pd.DataFrame:
    cols = ["Date","XP","Phone","Weight","Stocks","Crypto","Expenses","Twitch","School","Finance","Prayer","Reading","Sport","Hygiene","Budget"]
    for c in cols:
        if c not in df.columns:
            df[c] = 0
    # keep Date as datetime if present
    if "Date" in df.columns:
        df["Date"] = pd.to_datetime(df["Date"], errors="coerce")
    return df[cols]

def load_data(repo) -> Tuple[pd.DataFrame, Optional[Any]]:
    if not repo:
        return ensure_columns(pd.DataFrame()), None
    try:
        contents = repo.get_contents("data_2026.csv")
        df = pd.read_csv(StringIO(contents.decoded_content.decode("utf-8")))
        df = ensure_columns(df)
        return df, contents
    except Exception:
        return ensure_columns(pd.DataFrame()), None

def save_data(repo, df: pd.DataFrame, contents=None) -> bool:
    if not repo:
        return False
    try:
        csv_content = df.to_csv(index=False)
        if contents:
            repo.update_file("data_2026.csv", f"Update {datetime.utcnow().isoformat()}", csv_content, contents.sha)
        else:
            repo.create_file("data_2026.csv", "Initial commit - High Performance Dashboard", csv_content)
        return True
    except Exception as e:
        st.error(f"Erreur sauvegarde: {e}")
        return False

# ---------------------------
# CHART HELPERS
# ---------------------------
def line_chart(df: pd.DataFrame, x_col: str, y_col: str, title: str, color: str = "#0A84FF", target: Optional[float]=None):
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=df[x_col], y=df[y_col], mode="lines+markers", line=dict(color=color, width=3), marker=dict(size=6)))
    if target is not None:
        fig.add_hline(y=target, line_dash="dash", line_color="#FF453A", annotation_text=f"Target: {target}", annotation_position="top right")
    fig.update_layout(plot_bgcolor='#1C1C1E', paper_bgcolor='#000000', font=dict(color='#FFFFFF', family='-apple-system'), margin=dict(l=10,r=10,t=40,b=20))
    fig.update_xaxes(showgrid=True, gridcolor="#2C2C2E")
    fig.update_yaxes(showgrid=True, gridcolor="#2C2C2E")
    return fig

def bar_chart(df: pd.DataFrame, x_col: str, y_col: str, title: str, color: str = "#FFD60A"):
    fig = go.Figure()
    fig.add_trace(go.Bar(x=df[x_col], y=df[y_col], marker_color=color))
    fig.update_layout(plot_bgcolor='#1C1C1E', paper_bgcolor='#000000', font=dict(color='#FFFFFF'), margin=dict(l=10,r=10,t=40,b=20))
    return fig

# ---------------------------
# UTIL
# ---------------------------
tz = pytz.timezone("Europe/Paris")
now = datetime.now(tz)
today_str = now.strftime("%Y-%m-%d")

repo = init_github()
df, contents = load_data(repo)

# ---------------------------
# HEADER & QUOTE (format demandé)
# ---------------------------
st.markdown(f"<h1 style='text-align:center; font-size:44px;'>💪 HIGH PERFORMANCE 2026</h1>", unsafe_allow_html=True)
st.markdown(f"<p style='text-align:center; color:#8E8E93;'>{now.strftime('%A %d %B %Y')}</p>", unsafe_allow_html=True)

q_text, q_author = quote_of_day(now)
# affichage : guillemets + italique + auteur connu
st.markdown(f"<div class='card'><div class='card-title'>💬 Citation</div><p style='font-style:italic; font-size:16px;'>“{q_text}” — <strong>{q_author}</strong></p></div>", unsafe_allow_html=True)

# ---------------------------
# TABS
# ---------------------------
tab_journal, tab_stats = st.tabs(["📝 JOURNAL", "📊 STATISTIQUES"])

# ---------------------------
# JOURNAL TAB (inputs journaliers)
# ---------------------------
with tab_journal:
    st.markdown("<div class='card'><div class='card-title'>📱 Habitudes & Finances</div>", unsafe_allow_html=True)
    col1, col2 = st.columns([2,1])
    with col1:
        phone = st.number_input("Heures d'écran aujourd'hui", min_value=0.0, max_value=24.0, value=3.0, step=0.25, key="phone")
        stocks = st.number_input("Gain/perte Bourse aujourd'hui (€)", value=0.0, step=0.5, format="%.2f", key="stocks")
        crypto = st.number_input("Gain/perte Crypto aujourd'hui (€)", value=0.0, step=0.5, format="%.2f", key="crypto")
        expenses = st.number_input("Dépenses aujourd'hui (€)", min_value=0.0, value=0.0, step=0.5, format="%.2f", key="expenses")
        twitch = st.number_input("Abonnés Twitch", min_value=0, value=int(df["Twitch"].iloc[-1]) if not df.empty else 0, step=1, key="twitch")
    with col2:
        st.markdown("<div class='metric'><div class='metric-value'>—</div><div class='metric-label'>Score (après enregistrement)</div></div>", unsafe_allow_html=True)
        st.caption("Le score de discipline sera calculé à l'enregistrement.")
    st.markdown("<hr>", unsafe_allow_html=True)

    # grouped toggles
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

    # poids disponible tout le temps
    weight = st.number_input("Poids (kg) - entre quand tu veux", min_value=0.0, max_value=300.0, value=0.0, step=0.1, key="weight")

    st.markdown("</div>", unsafe_allow_html=True)

    # Save button
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
        if df.empty:
            df = pd.DataFrame([new_row])
        else:
            if today_str in df["Date"].astype(str).values:
                df.loc[df["Date"].astype(str) == today_str, list(new_row.keys())] = list(new_row.values())
            else:
                df = pd.concat([df, pd.DataFrame([new_row])], ignore_index=True)
        df = ensure_columns(df)
        df["Date"] = pd.to_datetime(df["Date"])
        df = df.sort_values("Date").reset_index(drop=True)
        if save_data(repo, df, contents):
            st.success(f"Journée enregistrée — Score {xp}%")
            df, contents = load_data(repo)
        else:
            st.error("Erreur lors de la sauvegarde sur GitHub.")

# ---------------------------
# STATISTICS TAB
# ---------------------------
with tab_stats:
    st.markdown("<div class='card'><div class='card-title'>📈 Mes statistiques financières & habitudes</div>", unsafe_allow_html=True)
    if df.empty or len(df) < 1:
        st.info("Aucune donnée disponible. Remplis ton journal pour voir les graphiques.")
    else:
        df = df.copy()
        df["Date"] = pd.to_datetime(df["Date"])
        df = df.sort_values("Date")

        # Overview metrics
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

        # Bourse chart
        st.markdown("### 💹 Bourse (gain/perte journalier)")
        df_stock = df[["Date","Stocks"]].copy()
        df_stock["MA7"] = df_stock["Stocks"].rolling(7, min_periods=1).mean()
        fig_stock = go.Figure()
        fig_stock.add_trace(go.Bar(x=df_stock["Date"], y=df_stock["Stocks"], name="Journalier", marker_color="#0A84FF"))
        fig_stock.add_trace(go.Scatter(x=df_stock["Date"], y=df_stock["MA7"], name="MA7", line=dict(color="#32D74B", width=3)))
        fig_stock.update_layout(plot_bgcolor='#1C1C1E', paper_bgcolor='#000000', font=dict(color='#FFFFFF'))
        st.plotly_chart(fig_stock, use_container_width=True)

        # Crypto chart
        st.markdown("### 🔥 Crypto (gain/perte journalier)")
        df_crypto = df[["Date","Crypto"]].copy()
        df_crypto["MA7"] = df_crypto["Crypto"].rolling(7, min_periods=1).mean()
        fig_crypto = go.Figure()
        fig_crypto.add_trace(go.Bar(x=df_crypto["Date"], y=df_crypto["Crypto"], name="Journalier", marker_color="#BF5AF2"))
        fig_crypto.add_trace(go.Scatter(x=df_crypto["Date"], y=df_crypto["MA7"], name="MA7", line=dict(color="#0A84FF", width=3)))
        fig_crypto.update_layout(plot_bgcolor='#1C1C1E', paper_bgcolor='#000000', font=dict(color='#FFFFFF'))
        st.plotly_chart(fig_crypto, use_container_width=True)

        # Expenses chart
        st.markdown("### 🧾 Dépenses quotidiennes")
        fig_exp = go.Figure()
        fig_exp.add_trace(go.Bar(x=df["Date"], y=df["Expenses"], name="Dépenses", marker_color="#FF453A"))
        fig_exp.update_layout(plot_bgcolor='#1C1C1E', paper_bgcolor='#000000', font=dict(color='#FFFFFF'))
        st.plotly_chart(fig_exp, use_container_width=True)

        # Poids
        st.markdown("### ⚖️ Évolution du poids")
        df_w = df[df["Weight"] > 0]
        if not df_w.empty:
            st.plotly_chart(line_chart(df_w, "Date", "Weight", "Poids (kg)", color="#32D74B"), use_container_width=True)
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

        # Detailed rates
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
