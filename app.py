import streamlit as st
import pandas as pd
from github import Github
from io import StringIO
from datetime import datetime
import pytz
import plotly.graph_objects as go

# ============================================================
# CONFIGURATION & DESIGN iOS DARK MODE
# ============================================================
st.set_page_config(
    page_title="High Performance 2026",
    page_icon="💪",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# CSS INJECTION - APPLE DARK MODE STRICT
st.markdown("""
<style>
/* ===== FOND NOIR ABSOLU ===== */
.stApp {
    background-color: #000000 !important;
}

/* ===== TEXTES BLANCS PARTOUT ===== */
h1, h2, h3, h4, h5, h6, p, span, div, label, .stMarkdown {
    color: #FFFFFF !important;
    font-family: -apple-system, BlinkMacSystemFont, "SF Pro Display", sans-serif !important;
}

/* ===== CARTE iOS STYLE ===== */
.ios-card {
    background: linear-gradient(145deg, #1C1C1E 0%, #2C2C2E 100%);
    border-radius: 20px;
    padding: 30px;
    margin-bottom: 20px;
    border: 1px solid #3A3A3C;
    box-shadow: 0 8px 32px rgba(0, 0, 0, 0.5);
    transition: transform 0.2s ease;
}

.ios-card:hover {
    transform: translateY(-2px);
    box-shadow: 0 12px 40px rgba(0, 0, 0, 0.7);
}

/* ===== TITRE DE CARTE ===== */
.card-title {
    font-size: 24px;
    font-weight: 700;
    margin-bottom: 20px;
    letter-spacing: -0.5px;
}

/* ===== INPUTS iOS STYLE ===== */
.stNumberInput input {
    background-color: #2C2C2E !important;
    color: #FFFFFF !important;
    border: 1px solid #3A3A3C !important;
    border-radius: 12px !important;
    text-align: center;
    font-size: 22px !important;
    font-weight: 600 !important;
    padding: 12px !important;
}

.stNumberInput input:focus {
    border-color: #0A84FF !important;
    box-shadow: 0 0 0 3px rgba(10, 132, 255, 0.1) !important;
}

/* ===== GROS TOGGLE SWITCHES ===== */
.stCheckbox {
    transform: scale(2.5);
    transform-origin: left center;
    margin-left: 20px;
    margin-top: 5px;
    margin-bottom: 5px;
}

/* ===== BOUTON PRIMARY ===== */
.stButton button[kind="primary"] {
    background: linear-gradient(135deg, #0A84FF 0%, #0066CC 100%) !important;
    color: white !important;
    border: none !important;
    border-radius: 14px !important;
    font-size: 18px !important;
    font-weight: 700 !important;
    padding: 18px 32px !important;
    box-shadow: 0 4px 20px rgba(10, 132, 255, 0.4) !important;
    transition: all 0.3s ease !important;
}

.stButton button[kind="primary"]:hover {
    transform: translateY(-2px);
    box-shadow: 0 6px 30px rgba(10, 132, 255, 0.6) !important;
}

/* ===== TABS STYLE ===== */
.stTabs [data-baseweb="tab-list"] {
    gap: 10px;
    background-color: #1C1C1E;
    border-radius: 14px;
    padding: 8px;
}

.stTabs [data-baseweb="tab"] {
    background-color: transparent;
    border-radius: 10px;
    color: #8E8E93 !important;
    font-size: 18px !important;
    font-weight: 600 !important;
    padding: 12px 24px;
}

.stTabs [aria-selected="true"] {
    background-color: #2C2C2E !important;
    color: #FFFFFF !important;
}

/* ===== METRICS ===== */
.metric-container {
    background-color: #2C2C2E;
    border-radius: 12px;
    padding: 16px;
    text-align: center;
    border: 1px solid #3A3A3C;
}

.metric-value {
    font-size: 32px;
    font-weight: 700;
    color: #0A84FF;
}

.metric-label {
    font-size: 14px;
    color: #8E8E93;
    margin-top: 8px;
}

/* ===== CAPTION ===== */
.stCaption {
    color: #8E8E93 !important;
    font-size: 14px !important;
}

/* ===== DIVIDER ===== */
hr {
    border-color: #3A3A3C !important;
    margin: 20px 0;
}

/* ===== HIDE STREAMLIT BRANDING ===== */
#MainMenu {visibility: hidden;}
footer {visibility: hidden;}
header {visibility: hidden;}
</style>
""", unsafe_allow_html=True)

# ============================================================
# FONCTIONS GITHUB
# ============================================================
@st.cache_resource
def init_github():
    """Initialise la connexion GitHub"""
    try:
        token = st.secrets["GITHUB_TOKEN"]
        repo_name = st.secrets["REPO_NAME"]
        g = Github(token)
        repo = g.get_repo(repo_name)
        return repo
    except Exception as e:
        st.error(f"⚠️ Erreur connexion GitHub: {str(e)}")
        return None

def load_data(repo):
    """Charge les données depuis GitHub"""
    if not repo:
        return pd.DataFrame(columns=[
            "Date", "XP", "Phone", "Weight", "PnL", "Twitch",
            "School", "Finance", "Prayer", "Reading", "Sport",
            "Hygiene", "Budget"
        ]), None
    
    try:
        contents = repo.get_contents("data_2026.csv")
        df = pd.read_csv(StringIO(contents.decoded_content.decode("utf-8")))
        return df, contents
    except:
        return pd.DataFrame(columns=[
            "Date", "XP", "Phone", "Weight", "PnL", "Twitch",
            "School", "Finance", "Prayer", "Reading", "Sport",
            "Hygiene", "Budget"
        ]), None

def save_data(repo, df, contents=None):
    """Sauvegarde les données sur GitHub"""
    if not repo:
        return False
    
    try:
        csv_content = df.to_csv(index=False)
        if contents:
            repo.update_file(
                "data_2026.csv",
                f"Update {datetime.now().strftime('%Y-%m-%d %H:%M')}",
                csv_content,
                contents.sha
            )
        else:
            repo.create_file(
                "data_2026.csv",
                "Initial commit - High Performance Dashboard",
                csv_content
            )
        return True
    except Exception as e:
        st.error(f"⚠️ Erreur sauvegarde: {str(e)}")
        return False

# ============================================================
# FONCTIONS GRAPHIQUES
# ============================================================
def create_line_chart(df, column, title, color="#0A84FF", target=None):
    """Crée un graphique ligne style iOS"""
    fig = go.Figure()
    
    fig.add_trace(go.Scatter(
        x=df["Date"],
        y=df[column],
        mode='lines+markers',
        name=title,
        line=dict(color=color, width=3),
        marker=dict(size=8, color=color),
        fill='tozeroy',
        fillcolor=f'rgba({int(color[1:3], 16)}, {int(color[3:5], 16)}, {int(color[5:7], 16)}, 0.1)'
    ))
    
    if target:
        fig.add_hline(
            y=target,
            line_dash="dash",
            line_color="#FF453A",
            annotation_text=f"Target: {target}",
            annotation_position="right"
        )
    
    fig.update_layout(
        title=title,
        plot_bgcolor='#1C1C1E',
        paper_bgcolor='#000000',
        font=dict(color='#FFFFFF', family='-apple-system'),
        xaxis=dict(gridcolor='#2C2C2E', showgrid=True),
        yaxis=dict(gridcolor='#2C2C2E', showgrid=True),
        hovermode='x unified',
        margin=dict(l=20, r=20, t=60, b=20)
    )
    
    return fig

def create_bar_chart(df, column, title, color="#32D74B"):
    """Crée un graphique barre style iOS"""
    fig = go.Figure()
    
    fig.add_trace(go.Bar(
        x=df["Date"],
        y=df[column],
        name=title,
        marker=dict(
            color=color,
            line=dict(color=color, width=0)
        )
    ))
    
    fig.update_layout(
        title=title,
        plot_bgcolor='#1C1C1E',
        paper_bgcolor='#000000',
        font=dict(color='#FFFFFF', family='-apple-system'),
        xaxis=dict(gridcolor='#2C2C2E'),
        yaxis=dict(gridcolor='#2C2C2E'),
        margin=dict(l=20, r=20, t=60, b=20)
    )
    
    return fig

# ============================================================
# APPLICATION PRINCIPALE
# ============================================================
repo = init_github()
df, contents = load_data(repo)

# Timezone & Date
tz = pytz.timezone('Europe/Paris')
today_obj = datetime.now(tz)
today_str = today_obj.strftime('%Y-%m-%d')
is_friday = (today_obj.weekday() == 4)

# Header
st.markdown(f"""
<h1 style='text-align: center; font-size: 48px; margin-bottom: 10px;'>
    💪 HIGH PERFORMANCE 2026
</h1>
<p style='text-align: center; color: #8E8E93; font-size: 18px; margin-bottom: 40px;'>
    {today_obj.strftime('%A %d %B %Y')}
</p>
""", unsafe_allow_html=True)

# ============================================================
# TABS NAVIGATION
# ============================================================
tab1, tab2 = st.tabs(["📝 JOURNAL", "📊 VISION"])

# ============================================================
# TAB 1: JOURNAL DU JOUR
# ============================================================
with tab1:
    # --- PHONE DETOX ---
    st.markdown('<div class="ios-card">', unsafe_allow_html=True)
    st.markdown('<div class="card-title">📱 PHONE DETOX</div>', unsafe_allow_html=True)
    
    phone_hours = st.number_input(
        "Heures d'écran aujourd'hui",
        min_value=0.0,
        max_value=24.0,
        value=3.0,
        step=0.5,
        key="phone_input"
    )
    
    time_saved = 16 - phone_hours
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown(f"""
        <div class="metric-container">
            <div class="metric-value">{phone_hours}h</div>
            <div class="metric-label">Temps écran</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        color_saved = '#32D74B' if time_saved >= 13 else '#FF453A'
        st.markdown(f"""
        <div class="metric-container">
            <div class="metric-value" style="color: {color_saved}">{time_saved}h</div>
            <div class="metric-label">Temps libre</div>
        </div>
        """, unsafe_allow_html=True)
    
    st.caption("🎯 Objectif: Moins de 3h d'écran par jour")
    st.markdown('</div>', unsafe_allow_html=True)

    # --- SCHOOL/WORK ---
    st.markdown('<div class="ios-card">', unsafe_allow_html=True)
    st.markdown('<div class="card-title">🎓 ÉCOLE / TRAVAIL</div>', unsafe_allow_html=True)
    
    col_school_label, col_school_toggle = st.columns([4, 1])
    with col_school_label:
        st.markdown('<p style="font-size: 18px; margin-top: 8px;">Travail sérieux effectué</p>', unsafe_allow_html=True)
    with col_school_toggle:
        toggle_school = st.checkbox("School", key="toggle_school", label_visibility="collapsed")
    
    st.markdown('</div>', unsafe_allow_html=True)

    # --- FINANCE/EMPIRE ---
    st.markdown('<div class="ios-card">', unsafe_allow_html=True)
    st.markdown('<div class="card-title">💰 FINANCE & EMPIRE</div>', unsafe_allow_html=True)
    
    pnl_value = st.number_input(
        "PnL du jour (€)",
        value=0.0,
        step=10.0,
        format="%.2f",
        key="pnl_input"
    )
    
    st.markdown("---")
    col_finance_label, col_finance_toggle = st.columns([4, 1])
    with col_finance_label:
        st.markdown('<p style="font-size: 18px; margin-top: 8px;">Finance checkée à l\'heure prévue</p>', unsafe_allow_html=True)
    with col_finance_toggle:
        toggle_finance = st.checkbox("Finance", key="toggle_finance", label_visibility="collapsed")
    
    st.markdown('</div>', unsafe_allow_html=True)

    # --- TWITCH ---
    st.markdown('<div class="ios-card">', unsafe_allow_html=True)
    st.markdown('<div class="card-title">🎮 TWITCH</div>', unsafe_allow_html=True)
    
    twitch_subs = st.number_input(
        "Nombre d'abonnés actuels",
        min_value=0,
        value=11,
        step=1,
        key="twitch_input"
    )
    
    st.markdown("---")
    col_twitch_label, col_twitch_toggle = st.columns([4, 1])
    with col_twitch_label:
        st.markdown('<p style="font-size: 18px; margin-top: 8px;">Stream ou amélioration effectuée</p>', unsafe_allow_html=True)
    with col_twitch_toggle:
        toggle_twitch = st.checkbox("Twitch", key="toggle_twitch", label_visibility="collapsed")
    
    st.markdown('</div>', unsafe_allow_html=True)

    # --- SPIRITUALITÉ - PRIÈRE ---
    st.markdown('<div class="ios-card">', unsafe_allow_html=True)
    st.markdown('<div class="card-title">🙏 SPIRITUALITÉ - PRIÈRE</div>', unsafe_allow_html=True)
    
    col_prayer_label, col_prayer_toggle = st.columns([4, 1])
    with col_prayer_label:
        st.markdown('<p style="font-size: 18px; margin-top: 8px;">Prière quotidienne effectuée</p>', unsafe_allow_html=True)
    with col_prayer_toggle:
        toggle_prayer = st.checkbox("Prayer", key="toggle_prayer", label_visibility="collapsed")
    
    st.markdown('</div>', unsafe_allow_html=True)

    # --- SPIRITUALITÉ - LECTURE ---
    st.markdown('<div class="ios-card">', unsafe_allow_html=True)
    st.markdown('<div class="card-title">📖 SPIRITUALITÉ - LECTURE</div>', unsafe_allow_html=True)
    
    col_reading_label, col_reading_toggle = st.columns([4, 1])
    with col_reading_label:
        st.markdown('<p style="font-size: 18px; margin-top: 8px;">Lecture quotidienne effectuée</p>', unsafe_allow_html=True)
    with col_reading_toggle:
        toggle_reading = st.checkbox("Reading", key="toggle_reading", label_visibility="collapsed")
    
    st.markdown('</div>', unsafe_allow_html=True)

    # --- SPORT (MUSCU) ---
    st.markdown('<div class="ios-card">', unsafe_allow_html=True)
    st.markdown('<div class="card-title">💪 SPORT - MUSCULATION</div>', unsafe_allow_html=True)
    
    st.markdown("""
    <div style="background-color: #2C2C2E; padding: 16px; border-radius: 12px; margin-bottom: 20px;">
        <p style="font-size: 18px; margin: 0;">🔥 Routine:</p>
        <ul style="font-size: 16px; color: #8E8E93; margin-top: 10px;">
            <li>20 Pompes (Matin)</li>
            <li>20 Pompes (Soir)</li>
            <li>60 Répétitions Barre</li>
        </ul>
    </div>
    """, unsafe_allow_html=True)
    
    if is_friday:
        st.markdown("⚖️ **PESÉE DU VENDREDI**")
        weight_value = st.number_input(
            "Poids (kg)",
            min_value=0.0,
            max_value=200.0,
            value=70.0,
            step=0.1,
            key="weight_input"
        )
    else:
        st.markdown("""
        <div style="background-color: #2C2C2E; padding: 16px; border-radius: 12px; text-align: center; border: 2px dashed #FF453A;">
            <p style="font-size: 18px; color: #FF453A; margin: 0;">🔒 PESÉE VERROUILLÉE</p>
            <p style="font-size: 14px; color: #8E8E93; margin-top: 8px;">Rendez-vous vendredi pour la pesée hebdomadaire</p>
        </div>
        """, unsafe_allow_html=True)
        weight_value = 0.0
    
    st.markdown("---")
    col_sport_label, col_sport_toggle = st.columns([4, 1])
    with col_sport_label:
        st.markdown('<p style="font-size: 18px; margin-top: 8px;">Séance complète validée</p>', unsafe_allow_html=True)
    with col_sport_toggle:
        toggle_sport = st.checkbox("Sport", key="toggle_sport", label_visibility="collapsed")
    
    st.markdown('</div>', unsafe_allow_html=True)

    # --- HYGIÈNE / ENVIRONNEMENT ---
    st.markdown('<div class="ios-card">', unsafe_allow_html=True)
    st.markdown('<div class="card-title">🧼 HYGIÈNE & ENVIRONNEMENT</div>', unsafe_allow_html=True)
    
    col_hygiene_label, col_hygiene_toggle = st.columns([4, 1])
    with col_hygiene_label:
        st.markdown('<p style="font-size: 18px; margin-top: 8px;">Chambre rangée + Hygiène impeccable</p>', unsafe_allow_html=True)
    with col_hygiene_toggle:
        toggle_hygiene = st.checkbox("Hygiene", key="toggle_hygiene", label_visibility="collapsed")
    
    st.markdown('</div>', unsafe_allow_html=True)

    # --- BUDGET ---
    st.markdown('<div class="ios-card">', unsafe_allow_html=True)
    st.markdown('<div class="card-title">💸 BUDGET</div>', unsafe_allow_html=True)
    
    col_budget_label, col_budget_toggle = st.columns([4, 1])
    with col_budget_label:
        st.markdown('<p style="font-size: 18px; margin-top: 8px;">Zéro dépense inutile aujourd\'hui</p>', unsafe_allow_html=True)
    with col_budget_toggle:
        toggle_budget = st.checkbox("Budget", key="toggle_budget", label_visibility="collapsed")
    
    st.markdown('</div>', unsafe_allow_html=True)

    # --- BOUTON SAUVEGARDE ---
    st.markdown("<br>", unsafe_allow_html=True)
    
    if st.button("💾 ENREGISTRER MA JOURNÉE", type="primary", use_container_width=True):
        toggles = [
            toggle_school,
            toggle_finance,
            toggle_twitch,
            toggle_prayer,
            toggle_reading,
            toggle_sport,
            toggle_hygiene,
            toggle_budget,
            phone_hours <= 3.0
        ]
        xp_score = int((sum(toggles) / len(toggles)) * 100)
        
        new_row = {
            "Date": today_str,
            "XP": xp_score,
            "Phone": phone_hours,
            "Weight": weight_value,
            "PnL": pnl_value,
            "Twitch": twitch_subs,
            "School": int(toggle_school),
            "Finance": int(toggle_finance),
            "Prayer": int(toggle_prayer),
            "Reading": int(toggle_reading),
            "Sport": int(toggle_sport),
            "Hygiene": int(toggle_hygiene),
            "Budget": int(toggle_budget)
        }
        
        if not df.empty and today_str in df["Date"].values:
            df.loc[df["Date"] == today_str, list(new_row.keys())] = list(new_row.values())
            action = "mise à jour"
        else:
            df = pd.concat([df, pd.DataFrame([new_row])], ignore_index=True)
            action = "sauvegardée"
        
        if save_data(repo, df, contents):
            st.markdown(f"""
            <div style="background: linear-gradient(135deg, #32D74B 0%, #30D158 100%);
                        padding: 20px; border-radius: 16px; text-align: center; margin-top: 20px;">
                <h2 style="margin: 0; font-size: 28px;">✅ JOURNÉE {action.upper()} !</h2>
                <p style="font-size: 48px; font-weight: 700; margin: 10px 0;">{xp_score}%</p>
                <p style="font-size: 18px; margin: 0;">Score de Discipline</p>
            </div>
            """, unsafe_allow_html=True)
            df, contents = load_data(repo)
        else:
            st.error("⚠️ Erreur lors de la sauvegarde. Vérifie ta connexion GitHub.")

# ============================================================
# TAB 2: VISION & ANALYTICS
# ============================================================
with tab2:
    st.markdown('<h2 style="text-align: center; margin-bottom: 40px;">📈 MES STATISTIQUES</h2>', unsafe_allow_html=True)
    
    if df.empty:
        st.markdown("""
        <div style="background-color: #1C1C1E; padding: 60px; border-radius: 20px; text-align: center;">
            <h3 style="color: #8E8E93;">📭 Aucune donnée disponible</h3>
            <p style="color: #8E8E93;">Commence par remplir ton journal dans l'onglet JOURNAL</p>
        </div>
        """, unsafe_allow_html=True)
    else:
        df["Date"] = pd.to_datetime(df["Date"])
        df = df.sort_values("Date")
        
        # --- METRICS OVERVIEW ---
        st.markdown("### 📊 Vue d'ensemble")
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            avg_xp = df["XP"].mean()
            st.markdown(f"""
            <div class="metric-container">
                <div class="metric-value">{avg_xp:.0f}%</div>
                <div class="metric-label">XP Moyen</div>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            avg_phone = df["Phone"].mean()
            color_phone = "#32D74B" if avg_phone <= 3 else "#FF453A"
            st.markdown(f"""
            <div class="metric-container">
                <div class="metric-value" style="color: {color_phone}">{avg_phone:.1f}h</div>
                <div class="metric-label">Écran Moyen</div>
            </div>
            """, unsafe_allow_html=True)
        
        with col3:
            total_pnl = df["PnL"].sum()
            color_pnl = "#32D74B" if total_pnl >= 0 else "#FF453A"
            st.markdown(f"""
            <div class="metric-container">
                <div class="metric-value" style="color: {color_pnl}">{total_pnl:.0f}€</div>
                <div class="metric-label">PnL Total</div>
            </div>
            """, unsafe_allow_html=True)
        
        with col4:
            last_subs = df["Twitch"].iloc[-1]
            st.markdown(f"""
            <div class="metric-container">
                <div class="metric-value" style="color: #BF5AF2">{last_subs}</div>
                <div class="metric-label">Subs Twitch</div>
            </div>
            """, unsafe_allow_html=True)
        
        st.markdown("<br>", unsafe_allow_html=True)
        
        # --- GRAPHIQUE 1: DISCIPLINE (XP) ---
        st.markdown("### 🎯 Évolution de la Discipline")
        fig_xp = create_line_chart(df, "XP", "Score XP (%)", color="#0A84FF", target=80)
        st.plotly_chart(fig_xp, use_container_width=True)
        
        # --- GRAPHIQUE 2: TÉLÉPHONE ---
        st.markdown("### 📱 Temps d'écran quotidien")
        fig_phone = create_bar_chart(df, "Phone", "Heures d'écran", color="#FF453A")
        st.plotly_chart(fig_phone, use_container_width=True)
        st.caption("🎯 Objectif: Rester en dessous de 3h par jour")
        
        # --- GRAPHIQUE 3: POIDS ---
        st.markdown("### ⚖️ Évolution du Poids")
        df_weight = df[df["Weight"] > 0].copy()
        if not df_weight.empty:
            fig_weight = create_line_chart(df_weight, "Weight", "Poids (kg)", color="#32D74B")
            st.plotly_chart(fig_weight, use_container_width=True)
        else:
            st.info("⚖️ Pèse-toi un vendredi pour voir ton évolution ici")
        
        # --- GRAPHIQUE 4: FINANCE ---
        st.markdown("### 💰 Performance Financière (PnL)")
        fig_pnl = create_bar_chart(df, "PnL", "PnL Quotidien (€)", color="#FFD60A")
        st.plotly_chart(fig_pnl, use_container_width=True)
        
        # --- GRAPHIQUE 5: TWITCH ---
        st.markdown("### 🎮 Croissance Twitch")
        fig_twitch = create_line_chart(df, "Twitch", "Nombre d'abonnés", color="#BF5AF2")
        st.plotly_chart(fig_twitch, use_container_width=True)
        
        # --- STATS BONUS ---
        st.markdown("---")
        st.markdown("### 📋 Statistiques Détaillées")
        
        col_a, col_b = st.columns(2)
        
        with col_a:
            st.markdown("#### 🎯 Taux de Réussite")
            school_rate = (df["School"].sum() / len(df) * 100) if "School" in df.columns else 0
            finance_rate = (df["Finance"].sum() / len(df) * 100) if "Finance" in df.columns else 0
            prayer_rate = (df["Prayer"].sum() / len(df) * 100) if "Prayer" in df.columns else 0
            reading_rate = (df["Reading"].sum() / len(df) * 100) if "Reading" in df.columns else 0
            
            st.markdown(f"🎓 École/Travail: **{school_rate:.0f}%**")
            st.markdown(f"💰 Finance: **{finance_rate:.0f}%**")
            st.markdown(f"🙏 Prière: **{prayer_rate:.0f}%**")
            st.markdown(f"📖 Lecture: **{reading_rate:.0f}%**")
        
        with col_b:
            st.markdown("#### 💪 Habitudes Physiques")
            sport_rate = (df["Sport"].sum() / len(df) * 100) if "Sport" in df.columns else 0
            hygiene_rate = (df["Hygiene"].sum() / len(df) * 100) if "Hygiene" in df.columns else 0
            budget_rate = (df["Budget"].sum() / len(df) * 100) if "Budget" in df

sport_rate = (df["Sport"].sum() / len(df) * 100) if "Sport" in df.columns else 0
            hygiene_rate = (df["Hygiene"].sum() / len(df) * 100) if "Hygiene" in df.columns else 0
            budget_rate = (df["Budget"].sum() / len(df) * 100) if "Budget" in df.columns else 0
            
            st.markdown(f"💪 Sport: **{sport_rate:.0f}%**")
            st.markdown(f"🧼 Hygiène: **{hygiene_rate:.0f}%**")
            st.markdown(f"💸 Budget: **{budget_rate:.0f}%**")
        
        # --- FOOTER ---
        st.markdown("<br><br>", unsafe_allow_html=True)
        st.markdown("""
        <div style="text-align: center; color: #8E8E93; font-size: 14px; padding: 20px;">
            <p>💪 High Performance Dashboard 2026</p>
            <p>Continue de push, tu es sur la bonne voie ! 🚀</p>
        </div>
        """, unsafe_allow_html=True)
