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

# --- CSS PERSONNALISÉ ---
st.markdown("""
<style>
    .main { background-color: #0c0e12; color: #e0e0e0; }
    .stTabs [data-baseweb="tab-list"] { gap: 10px; }
    .stTabs [data-baseweb="tab"] {
        height: 50px; background-color: #1a202c;
        border-radius: 10px 10px 0px 0px; color: #a0aec0; border: 1px solid #2d343f;
        padding: 10px 25px; font-weight: 600; transition: all 0.3s ease;
    }
    .stTabs [data-baseweb="tab"]:hover { color: #00c853; background-color: #2d3748; }
    .stTabs [data-baseweb="tab"][aria-selected="true"] {
        background-color: #00c853; color: #fff; border-color: #00c853; transform: translateY(-2px);
    }
    .kpi-card {
        background-color: #161a21; padding: 20px; border-radius: 12px;
        border: 1px solid #2d343f; text-align: center;
        transition: all 0.4s cubic-bezier(0.175, 0.885, 0.32, 1.275);
    }
    .kpi-card:hover {
        transform: translateY(-8px);
        border-color: #00c853;
        box-shadow: 0 10px 20px rgba(0, 200, 83, 0.2);
    }
    .kpi-title { color: #a0aec0; font-size: 14px; text-transform: uppercase; margin-bottom: 8px; }
    .kpi-value { color: #00c853; font-size: 28px; font-weight: 800; }
    .stButton>button { background-color: #00c853; color: white; border-radius: 8px; font-weight: bold; width: 100%; transition: 0.3s; }
    .stButton>button:hover { background-color: #00a441; transform: scale(1.02); }
</style>
""", unsafe_allow_html=True)

# --- INITIALISATION DES TABLES ---
def init_db():
    db = get_connection()
    cursor = db.cursor()
    cursor.execute("CREATE TABLE IF NOT EXISTS utilisateurs (nom TEXT PRIMARY KEY, mdp TEXT)")
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS collectes (
            id INTEGER PRIMARY KEY AUTOINCREMENT, utilisateur TEXT,
            culture TEXT, region TEXT, variete TEXT, prix INTEGER,
            date_saisie TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS cheptel (
            id INTEGER PRIMARY KEY AUTOINCREMENT, utilisateur TEXT,
            espece TEXT, sante TEXT,
            date_ajout TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    db.commit()
    db.close()

init_db()

if 'connecte' not in st.session_state: st.session_state['connecte'] = False
if 'user_name' not in st.session_state: st.session_state['user_name'] = ""

def display_kpi_card(title, value, subtext):
    st.markdown(f"""<div class="kpi-card"><div class="kpi-title">{title}</div><div class="kpi-value">{value}</div><div style='color:#718096; font-size:12px;'>{subtext}</div></div>""", unsafe_allow_html=True)

# --- INTERFACE D'ACCUEIL (Connexion/Inscription Basculable) ---
if not st.session_state['connecte']:
    st.markdown("<h1 style='text-align: center; margin-top: 50px;'>🌿 AgroCam Pro</h1>", unsafe_allow_html=True)
    col_c, col_m, col_d = st.columns([1, 1.5, 1])
    
    with col_m:
        # --- BOUTON BASCULABLE (TOGGLE) ---
        mode_inscription = st.toggle("Nouveau ici ? Créer un compte")

        if not mode_inscription:
            st.markdown("### Connexion")
            with st.form("login_form"):
                user_input = st.text_input("Nom d'utilisateur")
                pwd_input = st.text_input("Mot de passe", type="password")
                if st.form_submit_button("Se connecter"):
                    db = get_connection()
                    cursor = db.cursor()
                    cursor.execute("SELECT * FROM utilisateurs WHERE nom=? AND mdp=?", (user_input, pwd_input))
                    if cursor.fetchone():
                        st.session_state['connecte'] = True
                        st.session_state['user_name'] = user_input
                        db.close()
                        st.rerun()
                    else:
                        st.error("Identifiants incorrects.")
                        db.close()
        else:
            st.markdown("### Créer un compte")
            with st.form("signup_form"):
                n_user = st.text_input("Choisir un nom")
                n_pwd = st.text_input("Choisir un mot de passe", type="password")
                if st.form_submit_button("S'inscrire"):
                    db = get_connection()
                    cursor = db.cursor()
                    try:
                        cursor.execute("INSERT INTO utilisateurs (nom, mdp) VALUES (?, ?)", (n_user, n_pwd))
                        db.commit()
                        st.success("Compte créé ! Basculez l'interrupteur pour vous connecter.")
                    except:
                        st.error("Ce nom est déjà utilisé.")
                    db.close()

# --- APPLICATION PRINCIPALE ---
else:
    col_h1, col_h2 = st.columns([5, 1])
    with col_h1: st.markdown(f"<h1>🌿 Dashboard : {st.session_state['user_name']}</h1>", unsafe_allow_html=True)
    with col_h2: 
        if st.button("🚪 Déconnexion"):
            st.session_state['connecte'] = False
            st.rerun()

    k1, k2, k3, k4 = st.columns(4)
    with k1: display_kpi_card("Rendement", "1.42 t/ha", "⚖️ Basé sur vos données")
    with k2: display_kpi_card("Santé Cheptel", "Optimale", "✅ État global")
    with k3: display_kpi_card("Ventes", "En hausse", "📈 +12% ce mois")
    with k4: display_kpi_card("Météo", "24°C", "☀️ Douala, Cameroun")

    tab1, tab2, tab3 = st.tabs(["📝 Saisie Ventes", "🐄 Gestion Cheptel", "Analyse IA & Stats 📊"])

    # --- ONGLET 1 : VENTES (Historique Basculable) ---
    with tab1:
        st.subheader("Gestion des Transactions")
        col_f, col_spacer = st.columns([1, 1])
        with col_f:
            st.markdown("<div style='background-color: #161a21; padding: 20px; border-radius: 12px; border: 1px solid #2d343f;'>", unsafe_allow_html=True)
            with st.form("v_form", clear_on_submit=True):
                c1, c2 = st.columns(2)
                cult = c1.text_input("Culture")
                reg = c2.text_input("Région")
                var = st.text_input("Variété")
                px = st.number_input("Prix total (FCFA)", min_value=0)
                if st.form_submit_button("Enregistrer"):
                    db = get_connection()
                    cursor = db.cursor()
                    cursor.execute("INSERT INTO collectes (utilisateur, culture, region, variete, prix) VALUES (?,?,?,?,?)", (st.session_state['user_name'], cult, reg, var, px))
                    db.commit(); db.close(); st.success("✅ Vente enregistrée !")
            st.markdown("</div>", unsafe_allow_html=True)
        
        st.markdown("<br>", unsafe_allow_html=True)
        
        # --- HISTORIQUE BASCULABLE ---
        if st.checkbox("🔍 Afficher l'historique de vos ventes"):
            db = get_connection()
            df_v = pd.read_sql(f"SELECT culture, region, variete, prix, date_saisie FROM collectes WHERE utilisateur='{st.session_state['user_name']}' ORDER BY date_saisie DESC", db)
            db.close()
            if not df_v.empty:
                st.dataframe(df_v, use_container_width=True)
            else:
                st.info("Aucune donnée enregistrée pour le moment.")

    # --- ONGLET 2 : CHEPTEL (Historique Basculable) ---
    with tab2:
        st.subheader("Suivi des Animaux")
        col_c1, col_c2 = st.columns([1, 2])
        with col_c1:
            st.markdown("<div style='background-color: #161a21; padding: 20px; border-radius: 12px; border: 1px solid #2d343f;'>", unsafe_allow_html=True)
            with st.form("c_form", clear_on_submit=True):
                esp = st.selectbox("Espèce", ["Bovin", "Caprin", "Porcin", "Volaille"])
                san = st.select_slider("État de Santé", options=["Critique", "Moyen", "Bon", "Excellent"])
                if st.form_submit_button("Ajouter"):
                    db = get_connection()
                    cursor = db.cursor()
                    cursor.execute("INSERT INTO cheptel (utilisateur, espece, sante) VALUES (?,?,?)", (st.session_state['user_name'], esp, san))
                    db.commit(); db.close(); st.success("✅ Animal ajouté !")
            st.markdown("</div>", unsafe_allow_html=True)
        
        with col_c2:
            # --- HISTORIQUE BASCULABLE ---
            if st.checkbox("🔍 Afficher le registre du cheptel"):
                db = get_connection()
                df_c = pd.read_sql(f"SELECT espece, sante, date_ajout FROM cheptel WHERE utilisateur='{st.session_state['user_name']}' ORDER BY date_ajout DESC", db)
                db.close()
                if not df_c.empty:
                    st.dataframe(df_c, use_container_width=True)
                else:
                    st.info("Le registre est vide.")

    # --- ONGLET 3 : ANALYSE IA ---
    with tab3:
        st.subheader("Analyse Descriptive IA")
        db = get_connection()
        df_v_ia = pd.read_sql(f"SELECT culture, region, prix, date_saisie FROM collectes WHERE utilisateur='{st.session_state['user_name']}'", db)
        db.close()

        if not df_v_ia.empty:
            col_chart_m, col_chart_s = st.columns([2, 1])
            with col_chart_m:
                st.markdown("<div style='background-color: #161a21; padding: 15px; border-radius: 12px; border: 1px solid #2d343f;'>", unsafe_allow_html=True)
                st.write("📊 **Distribution des Ventes**")
                scatter = alt.Chart(df_v_ia).mark_circle(size=100, color='#00c853', opacity=0.7).encode(
                    x=alt.X('culture:N', title='Cultures'), y=alt.Y('prix:Q', title='Prix (FCFA)'),
                    tooltip=['culture', 'region', 'prix']
                ).interactive().properties(height=350)
                st.altair_chart(scatter, use_container_width=True)
                st.markdown("</div>", unsafe_allow_html=True)
            
            with col_chart_s:
                st.markdown("<div style='background-color: #161a21; padding: 15px; border-radius: 12px; border: 1px solid #2d343f;'>", unsafe_allow_html=True)
                st.write("🍕 **Répartition**")
                pie = alt.Chart(df_v_ia).mark_arc(innerRadius=50).encode(
                    theta="count():Q", color=alt.Color("culture:N", scale=alt.Scale(scheme='category20b')),
                    tooltip=['culture', 'count()']
                ).properties(height=350)
                st.altair_chart(pie, use_container_width=True)
                st.markdown("</div>", unsafe_allow_html=True)
        else:
            st.info("Enregistrez des données pour activer les graphiques d'analyse.")
