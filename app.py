import streamlit as st
import pandas as pd
from datetime import datetime
import warnings

# =========================================================
# CONFIGURAÇÃO GERAL E CARREGAMENTO DE DADOS
# =========================================================

# Configuração da página Streamlit
st.set_page_config(
    page_title="Dashboard de Clientes JMS",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Suprimir avisos de desempacotamento de dados para manter o console limpo.
warnings.simplefilter(action='ignore', category=pd.errors.ParserWarning)

# Link público direto da imagem no repositório GitHub (Link RAW)
LOGO_URL_GITHUB = "https://raw.githubusercontent.com/euluanacristina/dashboard-clientes-jms/main/static/Logo%20JMS.jpg"


# A função de carregamento agora aceita 'clear_cache'
@st.cache_data(ttl=60) # TEMPO DE CACHE REDUZIDO PARA 60 SEGUNDOS (1 MINUTO)
def carregar_dados_e_processar():
    """Busca os dados, processa e retorna a contagem de status."""
    ARQUIVO_PLANILHA = "https://docs.google.com/spreadsheets/d/e/2PACX-1vQbOSJQgaJvTOXAQfB37ISlnvnHZ4Ue5z5mCMHTazn1G0Uttp6DYmJsszYIUz7P2A/pub?gid=466266260&single=true&output=csv"
    COLUNA_STATUS = 'STATUS DO ATENDIMENTO'

    try:
        # Lê o CSV diretamente da URL da web
        df = pd.read_csv(
            ARQUIVO_PLANILHA,
            header=0,
            encoding='latin1',
            sep=',',
            skipinitialspace=True
        )

        if COLUNA_STATUS not in df.columns:
            st.error(f"Erro: A coluna '{COLUNA_STATUS}' não foi encontrada na planilha.")
            return None, 0, 0, 0, 0

        df.dropna(how='all', inplace=True)

        # Processamento e Contagem
        df[COLUNA_STATUS] = df[COLUNA_STATUS].astype(str).str.upper().str.strip()
        contagem_status = df[COLUNA_STATUS].value_counts()

        # EXTRAÇÃO DOS VALORES
        resolvido = contagem_status.get('RESOLVIDO', 0)
        agendada = contagem_status.get('AGENDADA', 0)
        sem_retorno = contagem_status.get('SEM RETORNO', 0)
        total_clientes = len(df)

        return resolvido, agendada, sem_retorno, total_clientes

    except Exception as e:
        st.error(f"Erro Crítico ao carregar os dados: {e}")
        return None, 0, 0, 0, 0

# =========================================================
# LAYOUT STREAMLIT
# =========================================================

# 1. Título e Logo (Usando colunas Streamlit)
col_logo, col_title, col_button = st.columns([1, 3, 1]) # Adicionamos uma coluna para o botão

with col_logo:
    # Usando o link RAW do GitHub para a imagem
    st.image(LOGO_URL_GITHUB, caption="", width=100)

with col_title:
    st.title("Painel de Atendimentos de Clientes")
    data_hora_atual = datetime.now().strftime('%d/%m/%Y %H:%M:%S')
    st.markdown(f"**Última Atualização:** {data_hora_atual}", help="O cache é limpo automaticamente a cada 1 minuto.")

with col_button:
    # Adicionamos um botão que limpa o cache quando clicado
    st.markdown("<div style='height: 40px;'></div>", unsafe_allow_html=True) # Espaçamento
    if st.button("Recarregar Dados", use_container_width=True):
        st.cache_data.clear() # Esta função limpa o cache de TODAS as funções
        st.experimental_rerun() # Força o Streamlit a rodar o script novamente

# 2. Executa a função de carregamento
# Quando o botão é clicado, o cache é limpo e a função é chamada novamente.
resolvido, agendada, sem_retorno, total_clientes = carregar_dados_e_processar()

# 3. Exibe o Total de Clientes
st.markdown(f"---")
st.markdown(f"### Total de Clientes na Planilha: **{total_clientes}**")
st.markdown(f"---")

# 4. Exibe os cartões de status (Usando colunas Streamlit)
if resolvido is not None:
    col1, col2, col3 = st.columns(3)

    # Função auxiliar para estilizar os cartões
    def display_card(col, title, count, color):
        """Cria um cartão com o estilo desejado."""
        col.markdown(
            f"""
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
            """,
            unsafe_allow_html=True
        )

    # Aplica o estilo "Matrix" com as cores desejadas
    display_card(col1, "Resolvidos", resolvido, "#00FF00")
    display_card(col2, "Agendados", agendada, "#FFFF00")
    display_card(col3, "Sem Retorno", sem_retorno, "#FF0000")

# 5. Adiciona um estilo global (Simulando o tema preto/verde do seu HTML)
st.markdown(
    """
    <style>
    /* Estilo do corpo para simular o tema Matrix (preto e verde) */
    .stApp {
        background-color: #000000;
        color: #00FF00;
        font-family: 'Consolas', monospace;
    }
    /* Estilo para títulos e texto do Streamlit */
    h1, h2, h3, .stMarkdown, .css-1aum9i {
        color: #00FF00 !important;
    }
    /* Estilo para texto selecionado no Markdown */
    .stMarkdown > p > span {
        color: #00FF00 !important;
    }
    /* Estiliza o botão Recarregar */
    .stButton>button {
        background-color: #00FF00;
        color: #000000;
        border: 1px solid #00FF00;
        font-weight: bold;
        border-radius: 8px;
        box-shadow: 0 0 10px rgba(0, 255, 0, 0.8);
        transition: all 0.2s;
    }
    .stButton>button:hover {
        background-color: #39FF14;
        color: #000000;
        box-shadow: 0 0 15px rgba(0, 255, 0, 1.0);
    }
    </style>
    """,
    unsafe_allow_html=True
)
