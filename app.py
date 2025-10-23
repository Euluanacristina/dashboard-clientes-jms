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
@st.cache_data(ttl=60)  # Cache de 1 minuto
def carregar_dados_e_processar():
    COLUNA_STATUS_ESPERADA = 'STATUS DO ATENDIMENTO'
    COLUNA_NOME_ESPERADA = 'NOME'

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
            st.error(f"Erro: A coluna '{COLUNA_STATUS_ESPERADA}' não foi encontrada na planilha.")
            return None, None, 0, 0, 0, 0

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

        # Filtrar apenas os clientes com "SEM RETORNO"
        df_sem_retorno = df_limpo[df_limpo[COLUNA_STATUS_ESPERADA] == 'SEM RETORNO']

        return df_sem_retorno, df_limpo, resolvido, agendada, sem_retorno, total_clientes

    except Exception as e:
        st.error("Erro Crítico ao carregar os dados: verifique se o link da planilha está ativo e publicado como CSV.")
        return None, None, 0, 0, 0, 0


# ------------------------------------------------------------
# CABEÇALHO: LOGO + TÍTULO + BOTÃO
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
df_sem_retorno, df_limpo, resolvido, agendada, sem_retorno, total_clientes = carregar_dados_e_processar()

st.markdown("---")

if total_clientes is not None:
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
                box-shadow: 0 0 15px rgba(0, 255, 0, 0.5);
                color: white;
                font-family: monospace;
            '>
                <h2 style='color: {color}; margin-top: 0; font-size: 1.4em;'>{title}</h2>
                <div style='font-size: 4em; font-weight: bold; color: {color};'>{count}</div>
            </div>
        """
        return html_content 

    with col1:
        st.markdown(display_card("Resolvidos", resolvido, "#00FF00"), unsafe_allow_html=True)
    with col2:
        st.markdown(display_card("Agendados", agendada, "#FFFF00"), unsafe_allow_html=True)
    with col3:
        st.markdown(display_card("Sem Retorno", sem_retorno, "#FF0000"), unsafe_allow_html=True)

# ------------------------------------------------------------
# EXIBIR LISTA DE CLIENTES "SEM RETORNO"
# ------------------------------------------------------------
st.markdown("---")
st.subheader("📞 Clientes com Status: *SEM RETORNO*")

if df_sem_retorno is not None and not df_sem_retorno.empty:
    colunas_disponiveis = [c for c in ['NOME', 'TELEFONE', 'ENDEREÇO', 'OBSERVAÇÃO', 'DATA'] if c in df_sem_retorno.columns]
    
    if 'NOME' in df_sem_retorno.columns:
        st.dataframe(
            df_sem_retorno[colunas_disponiveis].reset_index(drop=True),
            use_container_width=True,
            hide_index=True
        )
    else:
        st.warning("A coluna 'NOME' não foi encontrada na planilha.")
else:
    st.info("Nenhum cliente com status 'SEM RETORNO' encontrado no momento.")
