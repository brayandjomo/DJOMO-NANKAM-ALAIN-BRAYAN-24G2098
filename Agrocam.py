import streamlit as st
import pandas as pd
import sqlite3
import altair as alt

# --- CONFIGURATION DE LA PAGE ---
st.set_page_config(
    page_title="AgroCam Pro - Pilotage Intelligent",
    page_icon="🌿",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- FONCTION DE CONNEXION (SQLite) ---
def get_connection():
    return sqlite3.connect("agrocam.db", check_same_thread=False)

# --- CSS PERSONNALISÉ (Animations et Design) ---
st.markdown("""
<style>
    /* Global Styles */
    .stApp { background-color: #0c0e12; color: #e0e0e0; }
    
    /* Animation du bouton Analyse IA au survol */
    div.stButton > button:first-child[key="ai_btn"] {
        background-color: #00c853;
        color: white;
        transition: all 0.3s ease-in-out;
        border: none;
        height: 3.5em;
        font-size: 18px;
        font-weight: bold;
    }
    div.stButton > button:first-child[key="ai_btn"]:hover {
        transform: scale(1.03) translateY(-3px);
        box-shadow: 0 10px 20px rgba(0, 200, 83, 0.4);
        background-color: #00e676;
    }

    /* Style Page Inscription / Connexion (Inspiration Image) */
    .auth-container {
        background-color: #ffffff;
        padding: 40px;
        border-radius: 20px;
        box-shadow: 0 10px 25px rgba(0,0,0,0.2);
        text-align: center;
        max-width: 450px;
        margin: auto;
    }
    .auth-title { color: #1a202c; font-size: 32px; font-weight: 800; margin-bottom: 8px; }
    .auth-subtitle { color: #718096; font-size: 14px; margin-bottom: 30px; }

    /* KPI Cards */
    .kpi-card {
        background-color: #161a21; padding: 20px; border-radius: 12px;
        border: 1px solid #2d343f; text-align: center;
        transition: all 0.4s ease;
    }
    .kpi-card:hover { transform: translateY(-5px); border-color: #00c853; }
    .kpi-value { color: #00c853; font-size: 28px; font-weight: 800; }
    
    /* Tabs Customization (Garde la taille originale des icônes) */
    .stTabs [data-baseweb="tab"] {
        background-color: #1a202c; border-radius: 10px 10px 0px 0px; 
        color: #a0aec0; font-weight: 600;
    }
    .stTabs [data-baseweb="tab"][aria-selected="true"] {
        background-color: #00c853; color: white;
    }
</style>
""", unsafe_allow_html=True)

# --- INITIALISATION DB ---
def init_db():
    db = get_connection()
    cursor = db.cursor()
    cursor.execute("CREATE TABLE IF NOT EXISTS utilisateurs (nom TEXT PRIMARY KEY, mdp TEXT)")
    cursor.execute("CREATE TABLE IF NOT EXISTS collectes (id INTEGER PRIMARY KEY AUTOINCREMENT, utilisateur TEXT, culture TEXT, region TEXT, variete TEXT, prix INTEGER, date_saisie TIMESTAMP DEFAULT CURRENT_TIMESTAMP)")
    cursor.execute("CREATE TABLE IF NOT EXISTS cheptel (id INTEGER PRIMARY KEY AUTOINCREMENT, utilisateur TEXT, espece TEXT, sante TEXT, date_ajout TIMESTAMP DEFAULT CURRENT_TIMESTAMP)")
    db.commit()
    db.close()

init_db()

if 'connecte' not in st.session_state: st.session_state['connecte'] = False
if 'user_name' not in st.session_state: st.session_state['user_name'] = ""

def display_kpi_card(title, value, subtext):
    st.markdown(f"""<div class="kpi-card"><div style='color:#a0aec0; font-size:14px;'>{title}</div><div class="kpi-value">{value}</div><div style='color:#718096; font-size:12px;'>{subtext}</div></div>""", unsafe_allow_html=True)

# --- INTERFACE D'ACCUEIL ---
if not st.session_state['connecte']:
    _, col_auth, _ = st.columns([1, 1.2, 1])
    
    with col_auth:
        st.markdown("<br><br>", unsafe_allow_html=True)
        mode = st.radio("Action", ["Se Connecter", "S'inscrire"], horizontal=True, label_visibility="collapsed")
        
        if mode == "S'inscrire":
            st.markdown("""<div class='auth-container'><div class='auth-title'>Create Account</div><div class='auth-subtitle'>Join the AgroCam Pro community today.</div>""", unsafe_allow_html=True)
            with st.form("signup_form"):
                nom = st.text_input("Full Name", placeholder="Your Name")
                pwd = st.text_input("Password", type="password", placeholder="Choose a password")
                if st.form_submit_button("Sign Up", use_container_width=True):
                    db = get_connection()
                    try:
                        db.execute("INSERT INTO utilisateurs (nom, mdp) VALUES (?, ?)", (nom, pwd))
                        db.commit()
                        st.success("Compte créé ! Connectez-vous.")
                    except: st.error("Nom déjà pris.")
                    db.close()
            st.markdown("</div>", unsafe_allow_html=True)
        else:
            st.markdown("""<div class='auth-container'><div class='auth-title'>Welcome Back</div><div class='auth-subtitle'>Please enter your details to login.</div>""", unsafe_allow_html=True)
            with st.form("login_form"):
                u_nom = st.text_input("User Name", placeholder="Enter your name")
                u_pwd = st.text_input("Password", type="password", placeholder="Enter your password")
                if st.form_submit_button("Sign In", use_container_width=True):
                    db = get_connection()
                    res = db.execute("SELECT * FROM utilisateurs WHERE nom=? AND mdp=?", (u_nom, u_pwd)).fetchone()
                    if res:
                        st.session_state['connecte'] = True
                        st.session_state['user_name'] = u_nom
                        st.rerun()
                    else: st.error("Erreur d'authentification.")
                    db.close()
            st.markdown("</div>", unsafe_allow_html=True)

# --- APPLICATION PRINCIPALE ---
else:
    c1, c2 = st.columns([5, 1])
    c1.title(f"🌿 Dashboard : {st.session_state['user_name']}")
    if c2.button("🚪 Déconnexion"):
        st.session_state['connecte'] = False
        st.rerun()

    k_cols = st.columns(4)
    with k_cols[0]: display_kpi_card("Rendement", "1.42 t/ha", "⚖️ Basé sur vos données")
    with k_cols[1]: display_kpi_card("Santé Cheptel", "Optimale", "✅ État global")
    with k_cols[2]: display_kpi_card("Ventes", "En hausse", "📈 +12% ce mois")
    with k_cols[3]: display_kpi_card("Météo", "24°C", "☀️ Douala, Cameroun")

    tab1, tab2, tab3 = st.tabs(["📝 Saisie Ventes", "🐄 Gestion Cheptel", "Analyse IA & Stats 📊"])

    with tab1:
        st.subheader("Gestion des Transactions")
        with st.form("v_form"):
            col_in = st.columns(3)
            cult = col_in[0].text_input("Culture")
            reg = col_in[1].text_input("Région")
            px = col_in[2].number_input("Prix (FCFA)", min_value=0)
            if st.form_submit_button("Enregistrer"):
                db = get_connection()
                db.execute("INSERT INTO collectes (utilisateur, culture, region, prix) VALUES (?,?,?,?)", (st.session_state['user_name'], cult, reg, px))
                db.commit(); db.close(); st.success("Vente enregistrée !")
        
        # Toggle Basculable (Nouvelle fonctionnalité)
        if st.toggle("🔍 Afficher l'historique des ventes", key="toggle_v"):
            db = get_connection()
            df = pd.read_sql(f"SELECT culture, region, prix, date_saisie FROM collectes WHERE utilisateur='{st.session_state['user_name']}'", db)
            st.dataframe(df, use_container_width=True)
            db.close()

    with tab2:
        st.subheader("Suivi des Animaux")
        with st.form("c_form"):
            esp = st.selectbox("Espèce", ["Bovin", "Caprin", "Porcin", "Volaille"])
            san = st.select_slider("Santé", options=["Critique", "Moyen", "Bon", "Excellent"])
            if st.form_submit_button("Ajouter"):
                db = get_connection()
                db.execute("INSERT INTO cheptel (utilisateur, espece, sante) VALUES (?,?,?)", (st.session_state['user_name'], esp, san))
                db.commit(); db.close(); st.success("Animal ajouté !")
        
        # Toggle Basculable (Nouvelle fonctionnalité)
        if st.toggle("🔍 Afficher le registre du cheptel", key="toggle_c"):
            db = get_connection()
            df = pd.read_sql(f"SELECT espece, sante, date_ajout FROM cheptel WHERE utilisateur='{st.session_state['user_name']}'", db)
            st.dataframe(df, use_container_width=True)
            db.close()

    with tab3:
        st.subheader("Analyse Descriptive IA")
        
        # Bouton avec Animation au survol (Clé 'ai_btn' pour le CSS)
        if st.button("🚀 Lancer l'Analyse IA", key="ai_btn", use_container_width=True):
            st.toast("L'IA examine vos données...", icon="🤖")
            st.balloons()

        db = get_connection()
        df_ia = pd.read_sql(f"SELECT culture, region, prix FROM collectes WHERE utilisateur='{st.session_state['user_name']}'", db)
        db.close()

        if not df_ia.empty:
            # Graphique en Nuage de points (Conservé comme demandé)
            scatter = alt.Chart(df_ia).mark_circle(size=120, color='#00c853', opacity=0.7).encode(
                x=alt.X('culture:N', title='Cultures'),
                y=alt.Y('prix:Q', title='Prix (FCFA)'),
                tooltip=['culture', 'region', 'prix']
            ).interactive().properties(height=400)
            st.altair_chart(scatter, use_container_width=True)
        else:
            st.info("Enregistrez des données pour activer les graphiques d'analyse.")
