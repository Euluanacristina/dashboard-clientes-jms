import streamlit as st
import pandas as pd
from datetime import datetime
import pytz
import warnings

# ------------------------------------------------------------
# CONFIGURAÇÕES INICIAIS
# ------------------------------------------------------------
st.set_page_config(
    page_title="Dashboard de Clientes JMS",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="collapsed"
)

warnings.simplefilter(action='ignore', category=pd.errors.ParserWarning)

LOGO_URL_GITHUB = "https://raw.githubusercontent.com/euluanacristina/dashboard-clientes-jms/main/static/Logo%20JMS.jpg"
ARQUIVO_PLANILHA = "https://docs.google.com/spreadsheets/d/e/2PACX-1vQbOSJQgaJvTOXAQfB37ISlnvnHZ4Ue5z5mCMHTazn1G0Uttp6DYmJsszYIUz7P2A/pub?gid=466266260&single=true&output=csv"


# ------------------------------------------------------------
# FUNÇÃO: CARREGAR E PROCESSAR DADOS
# ------------------------------------------------------------
@st.cache_data(ttl=60)
def carregar_dados_e_processar():
    COLUNA_STATUS_ESPERADA = 'STATUS DO ATENDIMENTO'
    try:
        df = pd.read_csv(ARQUIVO_PLANILHA, encoding='latin1', sep=',', skipinitialspace=True)
        df.columns = df.columns.str.strip()
        COLUNA_STATUS = COLUNA_STATUS_ESPERADA.strip()

        df_base = df.dropna(how='all')
        total_clientes = len(df_base)

        if COLUNA_STATUS not in df_base.columns:
            st.error(f"Erro: A coluna '{COLUNA_STATUS_ESPERADA}' não foi encontrada.")
            return None, 0, 0, 0, 0, 0

        df_status = df_base.dropna(subset=[COLUNA_STATUS])
        df_status.loc[:, COLUNA_STATUS] = (
            df_status[COLUNA_STATUS].astype(str).str.upper().str.strip()
        )

        df_limpo = df_status[df_status[COLUNA_STATUS] != '']
        contagem_status = df_limpo[COLUNA_STATUS].value_counts()

        resolvido = contagem_status.get('RESOLVIDO', 0)
        agendada = contagem_status.get('AGENDADA', 0)
        sem_retorno = contagem_status.get('SEM RETORNO', 0)

        return df_limpo, df_base, resolvido, agendada, sem_retorno, total_clientes

    except Exception:
        st.error("Erro ao carregar os dados. Verifique se o link da planilha está ativo.")
        return None, 0, 0, 0, 0, 0


# ------------------------------------------------------------
# CABEÇALHO
# ------------------------------------------------------------
col_logo, col_title, col_button = st.columns([1, 3, 1])

with col_logo:
    st.image(LOGO_URL_GITHUB, width=100)

with col_title:
    st.title("Painel de Atendimentos de Clientes")
    fuso_sp = pytz.timezone("America/Sao_Paulo")
    data_hora_sp = datetime.now(fuso_sp).strftime('%d/%m/%Y %H:%M:%S')
    st.markdown(
        f"**Última Atualização:** {data_hora_sp}",
        help="Horário local de São Paulo (UTC−3). O cache é limpo automaticamente a cada 1 minuto."
    )

with col_button:
    st.markdown("<div style='height: 40px;'></div>", unsafe_allow_html=True)
    if st.button("Recarregar Dados", use_container_width=True):
        carregar_dados_e_processar.clear()
        st.rerun()


# ------------------------------------------------------------
# EXIBIÇÃO DOS DADOS
# ------------------------------------------------------------
df_limpo, df_base, resolvido, agendada, sem_retorno, total_clientes = carregar_dados_e_processar()

st.markdown("---")

if total_clientes is not None:
    st.markdown(f"### Total de Clientes na Planilha: **{total_clientes}**")
st.markdown("---")

if 'mostrar_sem_retorno' not in st.session_state:
    st.session_state.mostrar_sem_retorno = False


# Função para exibir cartões estilizados
def display_card(title, count, color, key, clickable=False):
    """Cria um cartão estilizado (click opcional)."""
    html_content = f"""
        <div id="{key}" style='
            background-color: #1a1a1a;
            padding: 20px;
            border-radius: 12px;
            border: 2px solid {color};
            text-align: center;
            box-shadow: 0 0 15px rgba(0, 255, 0, 0.5);
            color: white;
            font-family: monospace;
            cursor: {"pointer" if clickable else "default"};
            transition: transform 0.2s ease-in-out;
        ' onclick="window.parent.postMessage({{type: '{key}_clicked'}}, '*')">
            <h2 style='color: {color}; margin-top: 0; font-size: 1.3em;'>{title}</h2>
            <div style='font-size: 4em; font-weight: bold; color: {color};'>{count}</div>
        </div>
    """
    st.markdown(html_content, unsafe_allow_html=True)


col1, col2, col3 = st.columns(3)

with col1:
    display_card("Resolvidos", resolvido, "#00FF00", "resolvido")

with col2:
    display_card("Agendados", agendada, "#FFFF00", "agendado")

with col3:
    # Este é o clicável
    display_card("Sem Retorno", sem_retorno, "#FF0000", "sem_retorno", clickable=True)

# Script JS para capturar o clique
st.markdown("""
    <script>
    const streamlitEvents = window.parent.streamlitEvents || {};
    window.addEventListener("message", (event) => {
        if (event.data.type === "sem_retorno_clicked") {
            window.parent.postMessage({isClicked: true}, "*");
        }
    });
    </script>
""", unsafe_allow_html=True)


# ------------------------------------------------------------
# PAINEL DE CLIENTES "SEM RETORNO"
# ------------------------------------------------------------
if st.button("Mostrar/Ocultar Clientes 'Sem Retorno'"):
    st.session_state.mostrar_sem_retorno = not st.session_state.mostrar_sem_retorno

if st.session_state.mostrar_sem_retorno:
    st.markdown("### ☎️ Clientes com Status: *SEM RETORNO*")

    df_sem_retorno = df_limpo[df_limpo["STATUS DO ATENDIMENTO"] == "SEM RETORNO"]

    if "NOME" in df_sem_retorno.columns:
        st.dataframe(df_sem_retorno[["NOME"]], hide_index=True, use_container_width=True)
    else:
        st.warning("Coluna 'NOME' não encontrada na planilha.")


# ------------------------------------------------------------
# ESTILO MATRIX
# ------------------------------------------------------------
st.markdown("""
    <style>
    .stApp {
        background-color: #000000;
        color: #00FF00;
        font-family: 'Consolas', monospace;
    }
    h1, h2, h3 {
        color: #39FF14 !important;
        text-shadow: 0 0 5px rgba(57, 255, 20, 0.8);
    }
    </style>
""", unsafe_allow_html=True)
