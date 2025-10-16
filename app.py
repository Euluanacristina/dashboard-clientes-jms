import pandas as pd
from flask import Flask, render_template
from datetime import datetime 
import warnings

# Suprimir avisos de desempacotamento de dados para manter o console limpo,
# pois o Pandas pode emitir warnings durante o carregamento de dados do tipo CSV.
warnings.simplefilter(action='ignore', category=pd.errors.ParserWarning)


# =========================================================
# 1. CONFIGURAÇÃO BASE (Continua na ordem correta)
# =========================================================
app = Flask(__name__)

# 2. Link público direto do Google Sheets no formato CSV
ARQUIVO_PLANILHA = "https://docs.google.com/spreadsheets/d/e/2PACX-1vQbOSJQgaJvTOXAQfB37ISlnvnHZ4Ue5z5mCMHTazn1G0Uttp6DYmJsszYIUz7P2A/pub?gid=466266260&single=true&output=csv"

@app.route('/')
def dashboard():
    # 3. Bloco de processamento de dados
    try: # <--- Começa aqui
        # Lê o CSV diretamente da URL da web
        # header=0 garante que a primeira linha (Linha 1 da planilha)
        # seja usada como cabeçalho, onde 'STATUS DO ATENDIMENTO' está definido.
        df = pd.read_csv(
            ARQUIVO_PLANILHA, 
            header=0, 
            encoding='latin1',  
            sep=',',
            skipinitialspace=True
        )
        
        COLUNA_STATUS = 'STATUS DO ATENDIMENTO'
        if COLUNA_STATUS not in df.columns:
            colunas_encontradas = ", ".join(df.columns.tolist())
            raise ValueError(f"A coluna '{COLUNA_STATUS}' não foi encontrada. Colunas lidas: {colunas_encontradas}")

        df.dropna(how='all', inplace=True)

        # 5. Processamento e Contagem
        df[COLUNA_STATUS] = df[COLUNA_STATUS].astype(str).str.upper().str.strip()
        contagem_status = df[COLUNA_STATUS].value_counts()
        
        # 6. EXTRAÇÃO
        resolvido = contagem_status.get('RESOLVIDO', 0)
        agendada = contagem_status.get('AGENDADA', 0)
        sem_retorno = contagem_status.get('SEM RETORNO', 0)
        
        total_clientes = len(df)
        
        # 7. Prepara a data e hora para o HTML
        data_hora_atual = datetime.now().strftime('%d/%m/%Y %H:%M:%S')
        
        # 8. Renderiza o template HTML e passa os dados
        return render_template(
            'dashboard.html',
            resolvido=resolvido,
            agendada=agendada,
            sem_retorno=sem_retorno,
            total=total_clientes,
            data_hora=data_hora_atual
        )

    except Exception as e: # <--- Deve estar alinhado com o 'try:'
        # Retorna o erro detalhado para o navegador
        return f"Erro Crítico: Não foi possível carregar ou processar os dados da planilha online. Detalhes: {e}", 500

if __name__ == '__main__':
    app.run(debug=True)
