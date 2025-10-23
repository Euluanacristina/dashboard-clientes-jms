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
        df = pd.read_csv(
            ARQUIVO_PLANILHA,
            header=0,
            encoding='latin1',
            sep=',',
            skipinitialspace=True
        )

        df.columns = df.columns.str.strip()
        df_base = df.dropna(how='all')
        total_clientes = len(df_base)

        if COLUNA_STATUS_ESPERADA not in df_base.columns:
            st.error(f"Erro: Coluna '{COLUNA_STATUS_ESPERADA}' não encontrada.")
            return None, 0, 0, 0, 0, None

        df_status_preenchido = df_base.dropna(subset=[COLUNA_STATUS_ESPERADA])
        df_status_preenchido.loc[:, COLUNA_STATUS_ESPERADA] = (
            df_status_preenchido[COLUNA_STATUS_ESPERADA]
            .astype(str)
            .str.upper()
            .str.strip()
        )

        df_limpo = df_status_preenchido[df_status_preenchido[COLUNA_STATUS_ESPERADA] != '']
        contagem_status = df_limpo[COLUNA_STATUS_ESPERADA].value_counts()

        resolvido = contagem_status.get('RESOLVIDO', 0)
        agendada = contagem_status.get('AGENDADA', 0)
        sem_retorno = contagem_status.get('SEM RETORNO', 0)

        # Filtra os clientes "SEM RETORNO"
        df_sem_retorno = df_limpo[df_limpo[COLUNA_STATUS_ESPERADA] == 'SEM RETORNO']

        return resolvido, agendada, sem_retorno, total_clientes, df_limpo, df_sem_retorno

    except Exception as e:
        st.error("Erro ao carregar dados. Verifique o link da planilha.")
        # Opcional: st.exception(e) para debug
        return None, 0, 0, 0, 0, None

# ------------------------------------------------------------
# CABEÇALHO E BOTÕES DE AÇÃO (CORRIGIDO)
# ------------------------------------------------------------
col_logo, col_title, col_button = st.columns([1, 3, 1])

with col_logo:
    st.image(LOGO_URL_GITHUB, caption="", width=100)

with col_title:
    st.title("Painel de Atendimentos de Clientes")
    fuso_sp = pytz.timezone("America/Sao_Paulo")
    data_hora_sp = datetime.now(fuso_sp).strftime('%d/%m/%Y %H:%M:%S')
    st.markdown(
        f"**Última Atualização:** {data_hora_sp}",
        help="Horário local de São Paulo (UTC−3)."
    )

with col_button:
    # 1. BOTÃO RECARREGAR DADOS
    # Adiciona espaço para alinhar verticalmente
    st.markdown("<div style='height: 40px;'></div>", unsafe_allow_html=True) 
    if st.button("🔄 Recarregar Dados", use_container_width=True):
        carregar_dados_e_processar.clear()
        st.rerun()

    # 2. LÓGICA DO BOTÃO "CLIENTES SEM RETORNO"
    # Inicializa o estado da sessão (necessário antes do botão)
    if "mostrar_sem_retorno" not in st.session_state:
        st.session_state.mostrar_sem_retorno = False

    # Botão para mostrar/ocultar painel
    # Adiciona uma quebra de linha para espaçamento entre os botões
    st.markdown("<br>", unsafe_allow_html=True) 
    if st.button("📋 Clientes Sem Retorno", use_container_width=True):
        st.session_state.mostrar_sem_retorno = not st.session_state.mostrar_sem_retorno

# ------------------------------------------------------------
# EXIBIÇÃO DOS DADOS
# ------------------------------------------------------------
resolvido, agendada, sem_retorno, total_clientes, df_limpo, df_sem_retorno = carregar_dados_e_processar()

st.markdown("---")
if total_clientes:
    st.markdown(f"### Total de Clientes na Planilha: **{total_clientes}**")
st.markdown("---")

if resolvido is not None:
    col1, col2, col3 = st.columns(3)

    def display_card(title, count, color):
        html_content = f"""
            <div style='
                background-color: #1a1a1a;
                padding: 20px;
                border-radius: 12px;
                border: 1px solid {color};
                text-align: center;
                box-shadow: 0 0 15px rgba(0, 255, 0, 0.3);
                color: white;
                font-family: monospace;
            '>
                <h2 style='color: {color}; margin-top: 0;'>{title}</h2>
                <div style='font-size: 3em; font-weight: bold; color: {color};'>{count}</div>
            </div>
        """
        st.markdown(html_content, unsafe_allow_html=True)

    with col1:
        display_card("Resolvidos", resolvido, "#00FF00")
    with col2:
        display_card("Agendados", agendada, "#FFFF00")
    with col3:
        display_card("Sem Retorno", sem_retorno, "#FF0000")

# ------------------------------------------------------------
# EXIBIÇÃO DA LISTA "CLIENTES SEM RETORNO"
# ------------------------------------------------------------

# Exibir painel se o estado estiver ativo
if st.session_state.mostrar_sem_retorno:
    st.markdown("### 🧾 Lista de Clientes Sem Retorno:")

    # Verifica se há coluna de nome
    col_nome = None
    if df_sem_retorno is not None:
        for nome_coluna in df_sem_retorno.columns:
            if 'nome' in nome_coluna.lower():
                col_nome = nome_coluna
                break

    if col_nome and df_sem_retorno is not None:
        st.dataframe(df_sem_retorno[[col_nome]], use_container_width=True, hide_index=True)
    elif df_sem_retorno is not None and not df_sem_retorno.empty:
        st.warning("⚠️ Nenhuma coluna de nome encontrada na planilha, exibindo a tabela completa.")
        st.dataframe(df_sem_retorno, use_container_width=True, hide_index=True)
    else:
        st.info("🎉 Não há clientes com o status 'Sem Retorno' no momento.")
