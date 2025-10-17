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

# 🟢 NOVO URL DA PLANILHA (CORRIGIDO PARA A ABA "CLIENTES") 🟢
# Este link inclui o 'gid' da sua aba de clientes
ARQUIVO_PLANILHA = "https://docs.google.com/spreadsheets/d/e/2PACX-1vQbOSJQgaJvTOXAQfB37ISlnvnHZ4Ue5z5mCMHTazn1G0Uttp6DYmJsszYIUz7P2A/pub?gid=466266260&single=true&output=csv"
# 🟢 🟢 🟢 🟢 🟢 🟢 🟢 🟢 🟢 🟢 🟢 🟢 🟢 🟢 🟢 🟢


# A função de carregamento agora usa um TTL de 60 segundos
@st.cache_data(ttl=60) # TEMPO DE CACHE REDUZIDO PARA 60 SEGUNDOS (1 MINUTO)
def carregar_dados_e_processar():
    """Busca os dados, processa e retorna a contagem de status."""
    COLUNA_STATUS = 'STATUS DO ATENDIMENTO'

    try:
        # 1. Lê o CSV diretamente da URL da web
        df = pd.read_csv(
            ARQUIVO_PLANILHA,
            header=0,
            encoding='latin1',
            sep=',',
            skipinitialspace=True
        )

        # =========================================================
        # INÍCIO DA SEÇÃO DE DEBUG (PARA VER SE OS DADOS ESTÃO CHEGANDO)
        # =========================================================
        st.info(f"DEBUG: DataFrame carregado com {len(df)} linhas antes da limpeza. Exibindo as 5 primeiras linhas:")
        st.dataframe(df.head())
        # =========================================================
        # FIM DA SEÇÃO DE DEBUG
        # =========================================================


        if COLUNA_STATUS not in df.columns:
            st.error(f"Erro: A coluna '{COLUNA_STATUS}' não foi encontrada na planilha.")
            return None, 0, 0, 0, 0
        
        # 2. LIMPEZA RIGOROSA (Para corrigir o bug de contagem de linhas vazias)
        # Remove linhas onde a coluna de STATUS está vazia (NaN).
        df.dropna(subset=[COLUNA_STATUS], inplace=True)
        # Remove linhas onde TODAS as colunas estão vazias
        df.dropna(how='all', inplace=True)


        # 3. Processamento e Contagem
        df[COLUNA_STATUS] = df[COLUNA_STATUS].astype(str).str.upper().str.strip()
        
        # 4. FILTRO DE VALORES VAZIOS APÓS O PROCESSAMENTO
        df_limpo = df[df[COLUNA_STATUS] != '']

        contagem_status = df_limpo[COLUNA_STATUS].value_counts()

        # 5. EXTRAÇÃO DOS VALORES
        resolvido = contagem_status.get('RESOLVIDO', 0)
        agendada = contagem_status.get('AGENDADA', 0)
        sem_retorno = contagem_status.get('SEM RETORNO', 0)
        total_clientes = len(df_limpo) 

        return resolvido, agendada, sem_retorno, total_clientes

    except Exception as e:
        # Exibe o erro crítico (como o 404, caso o link mude novamente)
        st.error(f"Erro Crítico ao carregar os dados: {e}") 
        return None, 0, 0, 0, 0

# =========================================================
# LAYOUT STREAMLIT
# =========================================================

# 1. Título, Logo e Botão de Recarregar
col_logo, col_title, col_button = st.columns([1, 3, 1])

with col_logo:
    st.image(LOGO_URL_GITHUB, caption="Logo JMS", width=100)

with col_title:
    st.title("Painel de Atendimentos de Clientes")
    data_hora_atual = datetime.now().strftime('%d/%m/%Y %H:%M:%S')
    st.markdown(f"**Última Atualização:** {data_hora_atual}", help="O cache é limpo automaticamente a cada 1 minuto.")

with col_button:
    st.markdown("<div style='height: 40px;'></div>", unsafe_allow_html=True)
    if st.button("Recarregar Dados", use_container_width=True):
        carregar_dados_e_processar.clear()
        st.rerun() 

# 2. Executa a função de carregamento
resolvido, agendada, sem_retorno, total_clientes = carregar_dados_e_processar()

# 3. Exibe o Total de Clientes
st.markdown(f"---")
# Verifica se os dados foram carregados antes de mostrar
if total_clientes is not None:
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

# 5. Adiciona um estilo global (Tema Matrix)
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
