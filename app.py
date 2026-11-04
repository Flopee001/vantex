import streamlit as st
import pandas as pd
import yfinance as yf
import numpy as np

# --------------------------------------------------------
# 1. SEGURANÇA INTEGRADA (SENHA FIXA PARA REPOSITÓRIO PÚBLICO)
# --------------------------------------------------------
SENHA_CORRETA = "EZEQUIEL"
# ⚠️ ADICIONE SEU ID DO ONESIGNAL DENTRO DAS ASPAS ABAIXO:
ONESIGNAL_APP_ID = "COLE_AQUI_O_SEU_ID_REAL"

st.set_page_config(page_title="IA Trader EUA - Public App", page_icon="📈", layout="wide")

# Conexão JavaScript para ativar as notificações push no seu celular
st.markdown(f"""
    <script src="https://onesignal.com" async></script>
    <script>
      window.OneSignal = window.OneSignal || [];
      OneSignal.push(function() {
        OneSignal.init({
          appId: "{ONESIGNAL_APP_ID}",
          safari_web_id: "web.onesignal.auto.ia_trader_ezequiel",
          notifyButton: { enable: true }
    </script>
""", unsafe_allow_html=True)

if "autenticado" not in st.session_state:
    st.session_state["autenticado"] = False

# Tela de Bloqueio Obrigatória (Pede a senha logo de cara)
if not st.session_state["autenticado"]:
    st.markdown("<h2 style='text-align: center; margin-top: 50px;'>🔒 Painel Restrito - IA Trader EUA</h2>", unsafe_allow_html=True)
    col1, col2, col3 = st.columns(3)
    with col2:
        senha_digitada = st.text_input("Insira sua chave de acesso para ativar a IA:", type="password")
        if st.button("ATIVAR INTELIGÊNCIA FINANCEIRA", use_container_width=True):
            if senha_digitada == SENHA_CORRETA:
                st.session_state["autenticado"] = True
                st.success("Acesso autorizado! Carregando tabelas...")
                st.rerun()
            else:
                st.error("Chave incorreta. Acesso estritamente negado.")
    st.stop()

# --------------------------------------------------------
# PROCESSAMENTO DE DADOS FINANCEIROS REAIS
# --------------------------------------------------------
def calcular_rsi(series, periods=14):
    delta = series.diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=periods).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=periods).mean()
    rs = gain / (loss + 1e-9)
    return 100 - (100 / (1 + rs))

@st.cache_data(ttl=1800)
def buscar_dados_reais():
    tickers = ["NVDA", "AAPL", "MSFT", "AMD", "TSLA", "AMZN", "GOOGL", "META", "NFLX", "AVGO"]
    dados = yf.download(tickers, period="1y", group_by="ticker", progress=False)
    lista_final = []
    for t in tickers:
        try:
            df_ticker = dados[t]
            preco_atual = float(df_ticker["Close"].iloc[-1])
            preco_inicio_ano = float(df_ticker["Close"].iloc[0])
            ganho_anual = ((preco_atual - preco_inicio_ano) / preco_inicio_ano) * 100
            rsi_valores = calcular_rsi(df_ticker["Close"])
            rsi_atual = float(rsi_valores.iloc[-1])
            if np.isnan(rsi_atual): rsi_atual = 50.0
            
            lista_final.append({
                "Ação (Ticker)": t,
                "Preço Atual (USD)": round(preco_atual, 2),
                "Score Preço (RSI)": round(rsi_atual, 1),
                "Ganho Recente % (Momentum)": round(ganho_anual, 1)
            })
        except: continue
    return pd.DataFrame(lista_final)

# --------------------------------------------------------
# 2. INTERFACE VISUAL DO APLICATIVO
# --------------------------------------------------------
st.title("📈 Painel IA Trader - Monitoramento Avançado")
st.write("Configurações táticas e tabelas automatizadas organizadas do melhor ao pior.")

# Menu de Capital na barra lateral esquerda
st.sidebar.header("💰 Planejamento de Capital")
fase = st.sidebar.selectbox("Fase do Plano de Depósitos:", ["Fase 1: R$ 1.000 Mensais (BRL)", "Fase 2: € 1.000 na França (EUR)"])

TAXA_USD_BRL, TAXA_USD_EUR = 5.75, 1.12  

if fase == "Fase 1: R$ 1.000 Mensais (BRL)":
    capital_disponivel_usd = 1000.0 / TAXA_USD_BRL
    st.sidebar.metric("Aporte Mensal Estimado", f"${capital_disponivel_usd:.2f} USD")
else:
    capital_disponivel_usd = 1000.0 * TAXA_USD_EUR
    st.sidebar.metric("Aporte Mensal Estimado", f"${capital_disponivel_usd:.2f} USD")

with st.spinner("Atualizando tabelas de Wall Street..."):
    df_mercado = buscar_dados_reais()

# TABELAS DE MERCADO DO MELHOR AO PIOR
st.header("📊 Filtros de Seleção do Algoritmo")
aba1, aba2 = st.tabs(["🎯 Filtro 1: Melhor Preço para Comprar", "🔥 Filtro 2: As que Ganham Mais"])

with aba1:
    st.subheader("📋 Ranking: Ativos Técnicos Mais Descontados (Menor RSI)")
    df_desconto = df_mercado.sort_values(by="Score Preço (RSI)", ascending=True)
    st.dataframe(df_desconto.reset_index(drop=True), use_container_width=True)

with aba2:
    st.subheader("📋 Ranking: Líderes de Valorização Comercial (% de Aumento)")
    df_momentum = df_mercado.sort_values(by="Ganho Recente % (Momentum)", ascending=False)
    st.dataframe(df_momentum.reset_index(drop=True), use_container_width=True)

# CALCULADORA AUTOMÁTICA DE COMPRA/VENDA E GESTÃO DE RISCO
st.header("🧮 Simulador de Execução de Ordens")
acao_selecionada = st.selectbox("Selecione a ação para calcular sua ordem:", df_mercado["Ação (Ticker)"].tolist())

row = df_mercado[df_mercado["Ação (Ticker)"] == acao_selecionada].iloc[0]
preco_acao = row["Preço Atual (USD)"]

# Divide o dinheiro por 3 ativos para segurança (diversificação)
capital_por_acao = capital_disponivel_usd / 3.0
quantidade_acoes = capital_por_acao / preco_acao
preco_stop, preco_alvo = preco_acao * 0.94, preco_acao * 1.12

c1, c2, c3, c4 = st.columns(4)
c1.metric("Quantidade de Ações", f"{quantidade_acoes:.4f}")
c2.metric("Orçamento Alocado", f"${capital_por_acao:.2f} USD")
c3.metric("🛑 Stop-Loss (Venda se cair)", f"${preco_stop:.2f} USD", "-6.0%")
c4.metric("🎯 Alvo de Lucro (Venda se subir)", f"${preco_alvo:.2f} USD", "+12.0%")

st.info(f"🛡️ **Estratégia de Controle de Danos:** Ao comprar {quantidade_acoes:.4f} frações de {acao_selecionada}, ative a venda automática caso toque em **${preco_stop:.2f}**. Isso blinda seu capital de grandes prejuízos.")

if st.button("🔒 Bloquear Aplicativo"):
    st.session_state["autenticado"] = False
    st.rerun()
