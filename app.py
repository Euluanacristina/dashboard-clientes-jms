import pandas as pd
from flask import Flask, render_template
from datetime import datetime 

# =========================================================
# 1. CONFIGURAÇÃO BASE (Continua na ordem correta)
# =========================================================
app = Flask(__name__)

# 2. Link público direto do Google Sheets no formato CSV
ARQUIVO_PLANILHA = "https://docs.google.com/spreadsheets/d/e/2PACX-1vQbOSJQgaJvTOXAQfB37ISlnvnHZ4Ue5z5mCMHTazn1G0Uttp6DYmJsszYIUz7P2A/pub?gid=466266260&single=true&output=csv"

@app.route('/')
def dashboard():
    # 3. Bloco de processamento de dados
    try:
        # Lê o CSV diretamente da URL da web
        df = pd.read_csv(
            ARQUIVO_PLANILHA, 
            header=1, 
            encoding='latin1', 
            sep=',',
            skipinitialspace=True
        )
        
        if 'STATUS DO ATENDIMENTO' not in df.columns:
            raise ValueError("A coluna 'STATUS DO ATENDIMENTO' não foi encontrada.")

        df.dropna(how='all', inplace=True)

        # 5. Processamento e Contagem
        # Converte tudo para MAIÚSCULO e remove espaços extras
        df['STATUS DO ATENDIMENTO'] = df['STATUS DO ATENDIMENTO'].astype(str).str.upper().str.strip()
        contagem_status = df['STATUS DO ATENDIMENTO'].value_counts()
        
        # =======================================================
        # 6. EXTRAÇÃO CORRIGIDA (Conta SOMENTE os nomes exatos)
        # =======================================================
        resolvido = contagem_status.get('RESOLVIDO', 0)
        agendada = contagem_status.get('AGENDADA', 0)
        sem_retorno = contagem_status.get('SEM RETORNO', 0)
        
        # NOTA: O status 'ESTA NORMAL' agora será IGNORADO,
        # a menos que você o inclua manualmente em alguma categoria.
        # Para ver todos os status encontrados, você pode imprimir
        # print(contagem_status.to_dict()) no terminal.
        # =======================================================
        
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

    except Exception as e:
        return f"Erro Crítico: Não foi possível carregar ou processar os dados da planilha online. Detalhes: {e}", 500

if __name__ == '__main__':
    app.run(debug=True)