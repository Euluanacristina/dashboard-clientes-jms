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

# Link público direto do Google Sheets no formato CSV
# A anotação @st.cache_data garante que o Streamlit carregue os dados
# apenas uma vez (ou quando a URL mudar), tornando o app muito mais rápido.
@st.cache_data(ttl=600) # Recarrega os dados a cada 10 minutos (600 segundos)
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
col_logo, col_title = st.columns([1, 4])

# O Streamlit não consegue acessar arquivos locais no GitHub diretamente.
# Usamos um placeholder para a logo, como no seu HTML original.
with col_logo:
    # URL de placeholder para a logo (pode ser substituída por uma URL pública, se disponível)
    st.image("https://placehold.co/100x40/000000/00FF00?text=JMS+LOGO", caption="Logo JMS")

with col_title:
    st.title("Painel de Atendimentos de Clientes")
    data_hora_atual = datetime.now().strftime('%d/%m/%Y %H:%M:%S')
    st.markdown(f"**Última Atualização:** {data_hora_atual}", help="Os dados são recarregados a cada 10 minutos.")


# 2. Executa a função de carregamento
resolvido, agendada, sem_retorno, total_clientes = carregar_dados_e_processar()

# 3. Exibe o Total de Clientes
st.markdown(f"---")
st.markdown(f"### Total de Clientes na Planilha: **{total_clientes}**")
st.markdown(f"---")

# 4. Exibe os cartões de status (Usando colunas Streamlit)
if resolvido is not None:
    # st.columns divide a tela horizontalmente para criar o layout de cartões
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
    </style>
    """,
    unsafe_allow_html=True
)
