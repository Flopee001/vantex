import streamlit as st
import pandas as pd
import yfinance as yf
import numpy as np
import os

# --------------------------------------------------------
# 1. TRAVA DE SEGURANÇA IMEDIATA - SENHA: EZEQUIEL
# --------------------------------------------------------
SENHA_CORRETA = os.environ.get("IA_TRADER_PASSWORD", "EZEQUIEL")

st.set_page_config(page_title="IA Trader EUA - Real Time", page_icon="📈", layout="wide")

if "autenticado" not in st.session_state:
    st.session_state["autenticado"] = False

if not st.session_state["autenticado"]:
    st.markdown("<h2 style='text-align: center;'>🔒 Painel Restrito - IA Trader EUA</h2>", unsafe_allow_html=True)
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        senha_digitada = st.text_input("Insira sua chave de acesso para ativar a IA:", type="password")
        if st.button("ATIVAR INTELIGÊNCIA FINANCEIRA", use_container_width=True):
            if senha_digitada == SENHA_CORRETA:
                st.session_state["autenticado"] = True
                st.success("Acesso autorizado! Carregando algoritmos...")
                st.rerun()
            else:
                st.error("Chave incorreta. Acesso estritamente negado.")
    st.stop()

# --------------------------------------------------------
# FUNCTIONS: CÁLCULOS MATEMÁTICOS DE MERCADO REAL
# --------------------------------------------------------
def calcular_rsi(series, periods=14):
    """Calcula o Índice de Força Relativa (RSI) real baseado no fechamento"""
    delta = series.diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=periods).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=periods).mean()
    rs = gain / (loss + 1e-9)
    return 100 - (100 / (1 + rs))

@st.cache_data(ttl=3600)  # Guarda os dados por 1 hora para o app ficar ultrarápido
def buscar_dados_reais():
    """Baixa dados reais do Yahoo Finance para uma cesta de ações líderes dos EUA"""
    tickers = ["NVDA", "AAPL", "MSFT", "AMD", "TSLA", "AMZN", "GOOGL", "META", "NFLX", "AVGO"]
    
    # Baixa o último ano de dados históricos
    dados = yf.download(tickers, period="1y", group_by="ticker", progress=False)
    
    lista_final = []
    for t in tickers:
        try:
            df_ticker = dados[t]
            preco_atual = float(df_ticker["Close"].iloc[-1])
            preco_inicio_ano = float(df_ticker["Close"].iloc[0])
            
            # Cálculo do ganho percentual no período (Momentum)
            ganho_anual = ((preco_atual - preco_inicio_ano) / preco_inicio_ano) * 100
            
            # Cálculo do RSI real dos últimos 14 dias de mercado
            rsi_valores = calcular_rsi(df_ticker["Close"])
            rsi_atual = float(rsi_valores.iloc[-1])
            
            # Trata valores nulos caso ocorram
            if np.isnan(rsi_atual):
                rsi_atual = 50.0

            lista_final.append({
                "Ticker": t,
                "Preço Atual (USD)": round(preco_atual, 2),
                "Score Preço (RSI)": round(rsi_atual, 1),
                "Ganho Recente % (Momentum)": round(ganho_anual, 1)
            })
        except:
            continue
            
    return pd.DataFrame(lista_final)

# --------------------------------------------------------
# 2. SISTEMA LIBERADO (Apenas após digitar EZEQUIEL)
# --------------------------------------------------------
st.title("📈 Sistema IA Trader - Monitoramento de Ações EUA (LIVE DATA)")
st.write("Dados em tempo real extraídos diretamente do mercado americano.")

# Barra lateral para Entrada de Capital e Câmbio
st.sidebar.header("💰 Gerenciador de Capital")
fase = st.sidebar.selectbox("Selecione sua Fase Atual:", ["Fase 1: Aportes em Reais (BRL)", "Fase 2: Na França (EUR)"])

# Cotações de mercado aproximadas para conversão automática
TAXA_USD_BRL = 5.75  
TAXA_USD_EUR = 1.12  

if fase == "Fase 1: Aportes em Reais (BRL)":
    valor_brl = st.sidebar.number_input("Valor do Depósito Mensal (R$):", value=1000.0, step=100.0)
    capital_disponivel_usd = valor_brl / TAXA_USD_BRL
    st.sidebar.metric("Poder de Compra Real Convertido", f"${capital_disponivel_usd:.2f} USD")
else:
    valor_eur = st.sidebar.number_input("Valor do Depósito Mensal (€):", value=1000.0, step=100.0)
    capital_disponivel_usd = valor_eur * TAXA_USD_EUR
    st.sidebar.metric("Poder de Compra Real Convertido", f"${capital_disponivel_usd:.2f} USD")

# Carrega os dados usando a função em tempo real
with st.spinner("Conectando aos servidores de Wall Street e calculando indicadores..."):
    df_mercado = buscar_dados_reais()

# --------------------------------------------------------
# 3. ALGORITMO DE FILTRAGEM (RANKING REAL: MELHOR AO PIOR)
# --------------------------------------------------------
st.header("🔍 Varredura Avançada de Mercado")
filtro_opcao = st.radio("Selecione o filtro de organização da IA:", 
                        ["Organizar por Melhor Preço de Compra (Ações Descontadas - Menor RSI)", 
                         "Organizar pelas que Ganham Mais (Maior Força de Alta - Momentum)"])

if filtro_opcao == "Organizar por Melhor Preço de Compra (Ações Descontadas - Menor RSI)":
    # Menor RSI indica ativo sobrevendido (oportunidade técnica de compra barata)
    df_filtrado = df_mercado.sort_values(by="Score Preço (RSI)", ascending=True)
    st.subheader("📋 Ranking: Melhores Preços de Entrada Técnicos (Mais Descontadas)")
else:
    # Maior ganho indica os papéis que estão explodindo em valorização
    df_filtrado = df_mercado.sort_values(by="Ganho Recente % (Momentum)", ascending=False)
    st.subheader("📋 Ranking: Líderes de Ganhos no Mercado (% de Aumento)")

st.dataframe(df_filtrado.reset_index(drop=True), use_container_width=True)

# --------------------------------------------------------
# 4. CALCULADORA DINÂMICA DE QUANTIDADE DE AÇÕES
# --------------------------------------------------------
st.header("🧮 Calculadora de Execução de Ordens")

acao_selecionada = st.selectbox("Escolha uma Ação do Ranking Real para Operar:", df_filtrado["Ticker"].tolist())
row = df_filtrado[df_filtrado["Ticker"] == acao_selecionada].iloc[0]

preco_acao = row["Preço Atual (USD)"]
st.info(f"Ativo Ativo: **{acao_selecionada}** | Preço de Mercado Agora: **${preco_acao:.2f} USD**")

# Divisão de risco: divide o seu aporte mensal atual por 3 ações recomendadas
capital_por_acao = capital_disponivel_usd / 3.0
quantidade_acoes = capital_por_acao / preco_acao

# Regras estritas de gerenciamento de perdas (Stop em 6% e Alvo em 12%)
preco_stop = preco_acao * 0.94
preco_alvo = preco_acao * 1.12

st.subheader("📦 Sugestão de Ordem Gerada por Tamanho de Capital:")
col1, col2, col3, col4 = st.columns(4)
col1.metric("Quantas Ações Comprar (Frações)", f"{quantidade_acoes:.4f}")
col2.metric("Orçamento p/ esta Ação", f"${capital_por_acao:.2f} USD")
col3.metric("🛑 Saída em Perda (Stop-Loss)", f"${preco_stop:.2f} USD", "-6.0%")
col4.metric("🎯 Saída em Lucro (Alvo Teórico)", f"${preco_alvo:.2f} USD", "+12.0%")

st.markdown(f"""
🛡️ **Instruções de Risco da IA:** Para o lote de **{quantidade_acoes:.4f}** ações da empresa **{acao_selecionada}**, programar a ordem de mercado automática. 
Se as flutuações do mercado jogarem o valor para baixo de **${preco_stop:.2f} USD**, liquide a operação imediatamente. Isso protege seus investimentos em Reais ou Euros de desvalorizações acentuadas.
""")

if st.button("🔒 Encerrar Sessão (Bloquear Painel)"):
    st.session_state["autenticado"] = False
    st.rerun()
