# app.py
import streamlit as st
import pandas as pd
from github import Github
from io import StringIO
from datetime import datetime, timedelta
import pytz
import plotly.graph_objects as go
from typing import Optional, Tuple, Dict, Any, List
import random

# ---------------------------
# CONFIG
# ---------------------------
st.set_page_config(page_title="High Performance 2026", page_icon="💪", layout="centered", initial_sidebar_state="collapsed")

# ---------------------------
# CSS (iOS-like, responsive)
# ---------------------------
st.markdown("""
<style>
:root {
  --bg:#000000; --card:#1C1C1E; --card-2:#2C2C2E; --muted:#8E8E93; --accent:#0A84FF; --good:#32D74B; --bad:#FF453A;
  --radius:16px; --font:-apple-system, BlinkMacSystemFont, "SF Pro Display", sans-serif;
}
body {background:var(--bg); color:#fff; font-family:var(--font);}
.stApp {padding:18px;}
.card {background: linear-gradient(145deg, var(--card) 0%, var(--card-2) 100%); border-radius:var(--radius); padding:20px; margin-bottom:18px; border:1px solid #2A2A2C;}
.card-title {font-size:20px; font-weight:700; margin-bottom:12px;}
.metric {background:transparent; padding:10px; border-radius:12px; text-align:center;}
.metric-value {font-size:28px; font-weight:800; color:var(--accent);}
.metric-label {font-size:13px; color:var(--muted);}
.small {font-size:13px; color:var(--muted);}
hr {border-color:#2A2A2C;}
@media (max-width:600px) {
  .card {padding:14px;}
  .card-title {font-size:18px;}
}
</style>
""", unsafe_allow_html=True)

# ---------------------------
# QUOTES (local list, rotate daily)
# ---------------------------
QUOTES = [
    "La discipline est le pont entre les objectifs et les réalisations. — Jim Rohn",
    "Fais ce que tu dois faire aujourd'hui pour que demain soit plus simple.",
    "Le progrès, même petit, est toujours progrès.",
    "La constance bat le talent quand le talent ne travaille pas.",
    "Reste humble, travaille dur, sois patient."
]

def quote_of_day(date: datetime) -> str:
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
    except Exception as e:
        st.error("Erreur connexion GitHub. Vérifie tes secrets.")
        return None

def load_data(repo) -> Tuple[pd.DataFrame, Optional[Any]]:
    cols = ["Date","XP","Phone","Weight","PnL","Twitch","School","Finance","Prayer","Reading","Sport","Hygiene","Budget"]
    if not repo:
        return pd.DataFrame(columns=cols), None
    try:
        contents = repo.get_contents("data_2026.csv")
        df = pd.read_csv(StringIO(contents.decoded_content.decode("utf-8")))
        # normalize date
        df["Date"] = pd.to_datetime(df["Date"])
        return df, contents
    except Exception:
        # return empty template
        return pd.DataFrame(columns=cols), None

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
# HEADER
# ---------------------------
st.markdown(f"<h1 style='text-align:center; font-size:44px;'>💪 HIGH PERFORMANCE 2026</h1>", unsafe_allow_html=True)
st.markdown(f"<p style='text-align:center; color:#8E8E93;'>{now.strftime('%A %d %B %Y')}</p>", unsafe_allow_html=True)

# Quote
st.markdown(f"<div class='card'><div class='card-title'>💬 Citation du jour</div><p class='small'>{quote_of_day(now)}</p></div>", unsafe_allow_html=True)

# ---------------------------
# TABS
# ---------------------------
tab_journal, tab_stats = st.tabs(["📝 JOURNAL", "📊 STATISTIQUES"])

# ---------------------------
# JOURNAL TAB
# ---------------------------
with tab_journal:
    st.markdown("<div class='card'><div class='card-title'>📱 Habitudes & Check</div>", unsafe_allow_html=True)
    col1, col2 = st.columns([2,1])
    with col1:
        phone = st.number_input("Heures d'écran aujourd'hui", min_value=0.0, max_value=24.0, value=3.0, step=0.25, key="phone")
        pnl = st.number_input("PnL du jour (€)", value=0.0, step=1.0, format="%.2f", key="pnl")
        twitch = st.number_input("Abonnés Twitch", min_value=0, value=int(df["Twitch"].iloc[-1]) if not df.empty else 0, step=1, key="twitch")
    with col2:
        st.markdown("<div class='metric'><div class='metric-value'>{:.0f}%</div><div class='metric-label'>Score cible</div></div>".format(0), unsafe_allow_html=True)
        st.caption("Le score sera calculé à l'enregistrement.")
    st.markdown("<hr>", unsafe_allow_html=True)

    # grouped toggles
    st.markdown("<div style='display:flex; gap:12px; flex-wrap:wrap;'>", unsafe_allow_html=True)
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
    st.markdown("</div>", unsafe_allow_html=True)

    # weight only on Friday (example)
    is_friday = (now.weekday() == 4)
    if is_friday:
        weight = st.number_input("Poids (kg) - pesée du vendredi", min_value=0.0, max_value=300.0, value=70.0, step=0.1, key="weight")
    else:
        st.info("Pesée hebdomadaire disponible le vendredi.")
        weight = 0.0

    st.markdown("</div>", unsafe_allow_html=True)

    # Save button
    if st.button("💾 Enregistrer la journée", type="primary"):
        # prepare row
        toggles_list = [int(toggles[k]) for k in habits.keys()]
        # include phone goal
        phone_goal_ok = 1 if phone <= 3.0 else 0
        xp = int((sum(toggles_list) + phone_goal_ok) / (len(toggles_list) + 1) * 100)
        new_row = {
            "Date": today_str,
            "XP": xp,
            "Phone": phone,
            "Weight": weight,
            "PnL": pnl,
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
        # ensure Date dtype
        df["Date"] = pd.to_datetime(df["Date"])
        df = df.sort_values("Date").reset_index(drop=True)
        # save
        if save_data(repo, df, contents):
            st.success(f"Journée enregistrée — Score {xp}%")
            # reload contents to update sha
            df, contents = load_data(repo)
        else:
            st.error("Erreur lors de la sauvegarde sur GitHub.")

# ---------------------------
# STATS TAB
# ---------------------------
with tab_stats:
    st.markdown("<div class='card'><div class='card-title'>📈 Mes statistiques</div>", unsafe_allow_html=True)
    if df.empty or len(df) < 1:
        st.info("Aucune donnée disponible. Remplis ton journal pour voir les graphiques.")
    else:
        df = df.copy()
        df["Date"] = pd.to_datetime(df["Date"])
        df = df.sort_values("Date")
        # overview metrics
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.markdown(f"<div class='metric'><div class='metric-value'>{df['XP'].mean():.0f}%</div><div class='metric-label'>XP moyen</div></div>", unsafe_allow_html=True)
        with col2:
            avg_phone = df["Phone"].mean()
            color = "#32D74B" if avg_phone <= 3 else "#FF453A"
            st.markdown(f"<div class='metric'><div class='metric-value' style='color:{color}'>{avg_phone:.1f}h</div><div class='metric-label'>Écran moyen</div></div>", unsafe_allow_html=True)
        with col3:
            st.markdown(f"<div class='metric'><div class='metric-value'>{df['PnL'].sum():.0f}€</div><div class='metric-label'>PnL total</div></div>", unsafe_allow_html=True)
        with col4:
            st.markdown(f"<div class='metric'><div class='metric-value'>{df['Twitch'].iloc[-1]}</div><div class='metric-label'>Subs Twitch</div></div>", unsafe_allow_html=True)

        st.markdown("<hr>", unsafe_allow_html=True)

        # Phone chart with comparisons
        phone_df = df[["Date","Phone"]].copy()
        phone_df["Phone_prev"] = phone_df["Phone"].shift(1)
        phone_df["MA7"] = phone_df["Phone"].rolling(7, min_periods=1).mean()
        fig_phone = go.Figure()
        fig_phone.add_trace(go.Bar(x=phone_df["Date"], y=phone_df["Phone"], name="Aujourd'hui", marker_color="#FF453A"))
        fig_phone.add_trace(go.Scatter(x=phone_df["Date"], y=phone_df["MA7"], name="Moyenne 7j", line=dict(color="#0A84FF", width=3)))
        fig_phone.add_trace(go.Scatter(x=phone_df["Date"], y=phone_df["Phone_prev"], name="Jour précédent", line=dict(color="#8E8E93", width=2, dash="dot")))
        fig_phone.update_layout(title="Heures d'écran — comparaison", plot_bgcolor='#1C1C1E', paper_bgcolor='#000000', font=dict(color='#FFFFFF'))
        st.plotly_chart(fig_phone, use_container_width=True)

        # Weight
        df_w = df[df["Weight"] > 0]
        if not df_w.empty:
            st.plotly_chart(line_chart(df_w, "Date", "Weight", "Poids (kg)", color="#32D74B"), use_container_width=True)
        else:
            st.info("Pesée hebdomadaire: pas encore de données de poids.")

        # XP evolution
        st.plotly_chart(line_chart(df, "Date", "XP", "Score XP (%)", color="#0A84FF", target=80), use_container_width=True)

        # PnL
        st.plotly_chart(bar_chart(df, "Date", "PnL", "PnL quotidien (€)", color="#FFD60A"), use_container_width=True)

        # Detailed rates
        st.markdown("<hr>", unsafe_allow_html=True)
        st.markdown("#### Taux de réussite par catégorie")
        rates = {}
        for k in habits.keys():
            if k in df.columns:
                rates[k] = df[k].sum() / len(df) * 100
        cols = st.columns(len(rates))
        for (name, val), col in zip(rates.items(), cols):
            col.metric(label=name, value=f"{val:.0f}%")

    st.markdown("</div>", unsafe_allow_html=True)
