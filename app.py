import streamlit as st
import pandas as pd
from datetime import datetime
import warnings


st.set_page_config(
    page_title="Dashboard de Clientes JMS",
    page_icon="📊",
    layout="wide", 
    initial_sidebar_state="collapsed"
)

warnings.simplefilter(action='ignore', category=pd.errors.ParserWarning)

LOGO_URL_GITHUB = "https://raw.githubusercontent.com/euluanacristina/dashboard-clientes-jms/main/static/Logo%20JMS.jpg"


ARQUIVO_PLANILHA = "https://docs.google.com/spreadsheets/d/e/2PACX-1vQbOSJQgaJvTOXAQfB37ISlnvnHZ4Ue5z5mCMHTazn1G0Uttp6DYmJsszYIUz7P2A/pub?gid=466266260&single=true&output=csv"



@st.cache_data(ttl=60) # TEMPO DE CACHE 60 SEGUNDOS (1 MINUTO)
def carregar_dados_e_processar():
    """Busca os dados, processa e retorna a contagem de status."""
    COLUNA_STATUS_ESPERADA = 'STATUS DO ATENDIMENTO' 

    try:
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
        

        df_status_preenchido.loc[:, COLUNA_STATUS] = df_status_preenchido[COLUNA_STATUS].astype(str).str.upper().str.strip()
        

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


# Logo e Botão de Recarregar
col_logo, col_title, col_button = st.columns([1, 3, 1])

with col_logo:
    st.image(LOGO_URL_GITHUB, caption="", width=100)

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

    #root, .stApp {
        min-height: 100vh;
        height: 100vh; 
    }

    .stApp > header {

        display: none !important;
    }
    
    .main {
        min-height: 100vh;
    }
    
    .stApp {
        background-color: #000000;
        color: #00FF00;
        font-family: 'Consolas', monospace;
    }
    h1, h2, h3 {
        color: #39FF14 !important; /* Um verde um pouco mais claro/neon */
        text-shadow: 0 0 5px rgba(57, 255, 20, 0.8);
    }
    
    .stMarkdown, .css-1aum9i {
        color: #00FF00 !important;
    }
    
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

