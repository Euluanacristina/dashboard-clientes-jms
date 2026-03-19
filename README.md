# 📊 Dashboard de Clientes JMS

Painel de atendimentos em tempo real, desenvolvido com **Streamlit** e integrado ao **Google Sheets**. Permite visualizar e acompanhar o status dos atendimentos de clientes de forma simples e visual.

---

## 🚀 Funcionalidades

- Leitura automática de dados via Google Sheets (atualização a cada 60 segundos)
- Exibição do total de clientes cadastrados na planilha
- Cards coloridos com contagem por status:
  - ✅ **Resolvidos** — verde
  - 📅 **Agendados** — amarelo
  - ⚠️ **Sem Retorno** — vermelho
- Lista de clientes com status "Sem Retorno" em layout de cards
- Botão para recarregar os dados manualmente

---

## 🛠️ Tecnologias utilizadas

- [Python](https://www.python.org/)
- [Streamlit](https://streamlit.io/)
- [Pandas](https://pandas.pydata.org/)
- [Google Sheets](https://sheets.google.com/) (via CSV público)
- [Pytz](https://pypi.org/project/pytz/) — fuso horário de São Paulo

---

## ▶️ Como rodar localmente

**1. Clone o repositório:**
```bash
git clone https://github.com/euluanacristina/dashboard-clientes-jms.git
cd dashboard-clientes-jms
```

**2. Instale as dependências:**
```bash
pip install streamlit pandas pytz
```

**3. Execute o projeto:**
```bash
streamlit run app.py
```

---

## 📁 Estrutura do projeto

```
dashboard-clientes-jms/
├── app.py              # Código principal do dashboard
├── static/
│   └── Logo JMS.jpg   # Logo exibida no cabeçalho
└── README.md
```

---

## 📋 Pré-requisitos da planilha

A planilha do Google Sheets precisa estar **publicada como CSV** e conter obrigatoriamente:

- Uma coluna chamada `STATUS DO ATENDIMENTO` com os valores: `RESOLVIDO`, `AGENDADA` ou `SEM RETORNO`
- Uma coluna com `nome` no título (para exibição dos cards de clientes sem retorno)
