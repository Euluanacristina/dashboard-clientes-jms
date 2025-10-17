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
    # layout wide é bom, mas o min-height 100vh no CSS garante o resto
    layout="wide", 
    initial_sidebar_state="collapsed"
)

# Suprimir avisos de desempacotamento de dados para manter o console limpo.
warnings.simplefilter(action='ignore', category=pd.errors.ParserWarning)

# Link público direto da imagem no repositório GitHub (Link RAW)
LOGO_URL_GITHUB = "https://raw.githubusercontent.com/euluanacristina/dashboard-clientes-jms/main/static/Logo%20JMS.jpg"

# URL DA PLANILHA - *CONFIRMADO E MANTIDO*
# Este link deve estar publicado na web como CSV (Valores Separados por Vírgula)
ARQUIVO_PLANILHA = "https://docs.google.com/spreadsheets/d/e/2PACX-1vQbOSJQgaJvTOXAQfB37ISlnvnHZ4Ue5z5mCMHTazn1G0Uttp6DYjsszYIUz7P2A/pub?gid=466266260&single=true&output=csv"


# A função de carregamento agora usa um TTL de 60 segundos
@st.cache_data(ttl=60) # TEMPO DE CACHE REDUZIDO PARA 60 SEGUNDOS (1 MINUTO)
def carregar_dados_e_processar():
    """Busca os dados, processa e retorna a contagem de status."""
    COLUNA_STATUS_ESPERADA = 'STATUS DO ATENDIMENTO' 

    try:
        # 1. Lê o CSV diretamente da URL da web
        df = pd.read_csv(
            ARQUIVO_PLANILHA,
            header=0,
            encoding='latin1',
            sep=',',
            skipinitialspace=True
        )
        
        # Limpa espaços em branco dos nomes das colunas
        df.columns = df.columns.str.strip()
        COLUNA_STATUS = COLUNA_STATUS_ESPERADA.strip()
        
        # 1. CÁLCULO TOTAL: Remove linhas onde TODAS as colunas estão vazias 
        df_base = df.dropna(how='all') 
        total_clientes = len(df_base)

        
        if COLUNA_STATUS not in df_base.columns:
            st.error(f"Erro: A coluna '{COLUNA_STATUS_ESPERADA}' não foi encontrada na planilha.")
            return None, 0, 0, 0, 0
        
        # 2. FILTRO PARA CONTAGEM DE STATUS: Usa apenas linhas que tem status preenchido
        df_status_preenchido = df_base.dropna(subset=[COLUNA_STATUS])
        

        # 3. Processamento e Contagem
        df_status_preenchido[COLUNA_STATUS] = df_status_preenchido[COLUNA_STATUS].astype(str).str.upper().str.strip()
        
        # 4. FILTRO DE VALORES VAZIOS APÓS O PROCESSAMENTO
        df_limpo = df_status_preenchido[df_status_preenchido[COLUNA_STATUS] != '']

        contagem_status = df_limpo[COLUNA_STATUS].value_counts()

        # 5. EXTRAÇÃO DOS VALORES
        resolvido = contagem_status.get('RESOLVIDO', 0)
        agendada = contagem_status.get('AGENDADA', 0)
        sem_retorno = contagem_status.get('SEM RETORNO', 0)

        # RETORNA TODOS OS VALORES PARA USAR NO LAYOUT
        return resolvido, agendada, sem_retorno, total_clientes

    except Exception as e:
        # EXIBE O ERRO DE REDE/HTTP, O QUE INCLUI O 404
        st.error(f"Erro Crítico ao carregar os dados: HTTP Error 404 Not Found (ou problema de conexão). Verifique se o link da planilha está ativo e publicado como CSV.")
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
        # Limpa o cache para forçar uma nova leitura da planilha
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
# Só exibe se a variável 'resolvido' não for None, indicando sucesso no carregamento
if resolvido is not None:
    col1, col2, col3 = st.columns(3)

    # Função auxiliar para estilizar os cartões
    def display_card(title, count, color):
        """Cria um cartão com o estilo desejado e retorna a string HTML."""
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

    # Aplica o estilo "Matrix" com as cores desejadas
    with col1:
        html_resolvido = display_card("Resolvidos", resolvido, "#00FF00")
        st.markdown(html_resolvido, unsafe_allow_html=True)
        
    with col2:
        html_agendada = display_card("Agendados", agendada, "#FFFF00")
        st.markdown(html_agendada, unsafe_allow_html=True)
        
    with col3:
        html_sem_retorno = display_card("Sem Retorno", sem_retorno, "#FF0000")
        st.markdown(html_sem_retorno, unsafe_allow_html=True)


# 5. Adiciona um estilo global (Tema Matrix)
st.markdown(
    """
    <style>
    /* CORREÇÃO DO PROBLEMA DE TAMANHO: Força o conteúdo principal a ter altura total da tela */
    
    /* Garante que o elemento root e o Streamlit App ocupem toda a altura */
    #root, .stApp {
        min-height: 100vh;
        height: 100vh; /* Adiciona height: 100vh para ser mais agressivo */
    }

    .stApp > header {
        /* Garante que o header (topo do Streamlit) não ocupe espaço extra */
        display: none !important;
    }
    
    .main {
        /* Ocupa 100% da altura restante da tela (resolve o problema do espaço preto) */
        min-height: 100vh;
    }
    
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
