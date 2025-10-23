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
    COLUNA_NOME = 'NOME'

    try:
        df = pd.read_csv(
            ARQUIVO_PLANILHA,
            header=0,
            encoding='latin1',
            sep=',',
            skipinitialspace=True
        )

        df.columns = df.columns.str.strip()
        df = df.dropna(how='all')

        if COLUNA_STATUS_ESPERADA not in df.columns or COLUNA_NOME not in df.columns:
            st.error("Erro: Colunas esperadas não foram encontradas na planilha.")
            return None, 0, 0, 0, 0, pd.DataFrame()

        df[COLUNA_STATUS_ESPERADA] = (
            df[COLUNA_STATUS_ESPERADA].astype(str).str.upper().str.strip()
        )

        total_clientes = len(df)
        contagem_status = df[COLUNA_STATUS_ESPERADA].value_counts()

        resolvido = contagem_status.get('RESOLVIDO', 0)
        agendada = contagem_status.get('AGENDADA', 0)
        sem_retorno = contagem_status.get('SEM RETORNO', 0)

        # Filtra apenas clientes com "Sem Retorno"
        df_sem_retorno = df[df[COLUNA_STATUS_ESPERADA] == 'SEM RETORNO'][[COLUNA_NOME]]

        return resolvido, agendada, sem_retorno, total_clientes, df_sem_retorno

    except Exception as e:
        st.error(f"Erro ao carregar os dados: {e}")
        return None, 0, 0, 0, 0, pd.DataFrame()

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
        help="Horário local de São Paulo (UTC−3)."
    )

with col_button:
    st.markdown("<div style='height: 40px;'></div>", unsafe_allow_html=True)
    if st.button("🔄 Recarregar Dados", use_container_width=True):
        carregar_dados_e_processar.clear()
        st.rerun()

# ------------------------------------------------------------
# EXIBIÇÃO DOS DADOS
# ------------------------------------------------------------
resolvido, agendada, sem_retorno, total_clientes, df_sem_retorno = carregar_dados_e_processar()

st.markdown("---")
st.markdown(f"### Total de Clientes na Planilha: **{total_clientes}**")
st.markdown("---")

col1, col2, col3 = st.columns(3)

def display_card(title, count, color, key=None, clickable=False):
    """Cria um cartão estilizado; se for clicável, age como botão."""
    html = f"""
        <div style='
            background-color: #1a1a1a;
            padding: 20px;
            border-radius: 12px;
            border: 1px solid {color};
            text-align: center;
            box-shadow: 0 0 15px {color};
            color: white;
            font-family: monospace;
            cursor: {"pointer" if clickable else "default"};
        '>
            <h2 style='color: {color}; margin-top: 0; font-size: 1.4em;'>{title}</h2>
            <div style='font-size: 4em; font-weight: bold; color: {color};'>{count}</div>
        </div>
    """
    if clickable:
        # Usa botão HTML dentro do Streamlit
        clicked = st.button(label="", key=key, help=f"Clique para ver detalhes de {title}", use_container_width=True)
        st.markdown(html, unsafe_allow_html=True)
        return clicked
    else:
        st.markdown(html, unsafe_allow_html=True)
        return False

# Renderiza os cartões
with col1:
    display_card("Resolvidos", resolvido, "#00FF00")

with col2:
    display_card("Agendados", agendada, "#FFFF00")

with col3:
    if "mostrar_sem_retorno" not in st.session_state:
        st.session_state.mostrar_sem_retorno = False

    # Torna o cartão “Sem Retorno” clicável
    clicado = st.button("", key="botao_sem_retorno", help="Clique para ver os clientes 'Sem Retorno'", use_container_width=True)
    st.markdown(f"""
        <div style='
            background-color: #1a1a1a;
            padding: 20px;
            border-radius: 12px;
            border: 1px solid #FF0000;
            text-align: center;
            box-shadow: 0 0 15px #FF0000;
            color: white;
            font-family: monospace;
            cursor: pointer;
        '>
            <h2 style='color: #FF0000; margin-top: 0; font-size: 1.4em;'>Sem Retorno</h2>
            <div style='font-size: 4em; font-weight: bold; color: #FF0000;'>{sem_retorno}</div>
        </div>
    """, unsafe_allow_html=True)

    if clicado:
        st.session_state.mostrar_sem_retorno = not st.session_state.mostrar_sem_retorno

# ------------------------------------------------------------
# PAINEL DE CLIENTES "SEM RETORNO"
# ------------------------------------------------------------
if st.session_state.mostrar_sem_retorno and not df_sem_retorno.empty:
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("### 📞 Clientes com Status: *SEM RETORNO*")
    st.dataframe(
        df_sem_retorno,
        hide_index=True,
        use_container_width=True,
        height=400
    )
