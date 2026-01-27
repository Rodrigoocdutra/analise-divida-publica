import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots

# 1. CONFIGURAÇÃO DA PÁGINA (Deve ser a primeira linha de código Streamlit)
st.set_page_config(page_title="Dashboard Dívida Pública", layout="wide")

# Função de Definição de Cores por Governo
def get_cor(ano):
    if 2003 <= ano <= 2010: return 'red'        # Lula 1 e 2
    elif 2011 <= ano <= 2016: return 'orange'   # Dilma
    elif 2017 <= ano <= 2018: return 'green'    # Temer
    elif 2019 <= ano <= 2022: return 'lightblue'# Bolsonaro
    elif 2023 <= ano <= 2025: return 'red'      # Lula 3
    else: return 'lightgray'                    # Prospecção

# 2. BASE DE DADOS CONSOLIDADA
dados_validados = {
    'Ano': [2003, 2004, 2005, 2006, 2007, 2008, 2009, 2010, 2011, 2012, 2013, 2014, 2015, 2016, 2017, 2018, 2019, 2020, 2021, 2022, 2023, 2024],
    'Valor': [1.23, 1.33, 1.45, 1.54, 1.74, 1.97, 2.01, 2.21, 2.36, 2.58, 2.75, 3.25, 3.93, 4.38, 4.85, 5.27, 5.50, 6.50, 6.80, 6.90, 6.52, 7.32]
}
df = pd.DataFrame(dados_validados)
df = pd.concat([df, pd.DataFrame({'Ano': [2025], 'Valor': [8.48]})]).reset_index(drop=True)

# Geração da Prospecção (Próximos 4 anos)
for i in range(1, 5):
    novo_valor = round(df['Valor'].iloc[-1] * 1.07, 2)
    df = pd.concat([df, pd.DataFrame({'Ano': [2025+i], 'Valor': [novo_valor]})]).reset_index(drop=True)

# Cálculo do Crescimento Percentual
df['Crescimento_%'] = df['Valor'].pct_change() * 100

# --- INTERFACE DO DASHBOARD ---
st.title("📊 Painel de Análise: Dívida Pública Federal (DPF)")
st.markdown("Estudo sobre a evolução do estoque da dívida brasileira e suas taxas de variação anual.")

# Criação das Abas para Navegação
tab1, tab2 = st.tabs(["📈 Estoque Nominal", "📉 Variação Percentual"])

# Configuração comum de legenda para ambos os gráficos
legendas = [('Lula', 'red'), ('Dilma', 'orange'), ('Temer', 'green'), ('Bolsonaro', 'lightblue'), ('Prospecção', 'lightgray')]

# --- ABA 1: VISUALIZAÇÃO DE ESTOQUE ---
with tab1:
    fig1 = go.Figure()
    for nome, cor in legendas:
        fig1.add_trace(go.Bar(x=[None], y=[None], marker_color=cor, name=nome))

    for i, row in df.iterrows():
        fig1.add_trace(go.Bar(
            x=[int(row['Ano'])], y=[row['Valor']],
            marker_color=get_cor(row['Ano']),
            text=f"{row['Valor']:.2f}T", textposition='outside', showlegend=False
        ))

    fig1.update_layout(
        title="Estoque Nominal da Dívida (Trilhões de R$)",
        xaxis=dict(type='category', title="Ano"),
        template='plotly_white',
        height=550,
        legend=dict(orientation="h", y=-0.2, x=0.5, xanchor="center")
    )
    st.plotly_chart(fig1, use_container_width=True)

# --- ABA 2: VISUALIZAÇÃO DE CRESCIMENTO ---
with tab2:
    fig2 = make_subplots(specs=[[{"secondary_y": True}]])
    for nome, cor in legendas:
        fig2.add_trace(go.Bar(x=[None], y=[None], marker_color=cor, name=nome), secondary_y=False)

    for i, row in df.iterrows():
        fig2.add_trace(go.Bar(
            x=[int(row['Ano'])], y=[row['Valor']],
            marker_color=get_cor(row['Ano']),
            showlegend=False, text=f"{row['Valor']:.1f}T", textposition='inside'
        ), secondary_y=False)

    fig2.add_trace(go.Scatter(
        x=df['Ano'], y=df['Crescimento_%'], mode='lines+markers+text',
        name='Variação % Anual', line=dict(color='black', width=3),
        text=[f"{v:.1f}%" if pd.notnull(v) else "" for v in df['Crescimento_%']],
        textposition="top center"
    ), secondary_y=True)

    fig2.update_layout(
        title="Correlação: Estoque vs. Velocidade de Crescimento",
        xaxis=dict(type='category', title="Ano"),
        template='plotly_white',
        height=550,
        legend=dict(orientation="h", y=-0.2, x=0.5, xanchor="center")
    )
    fig2.update_yaxes(title_text="Estoque (Trilhões R$)", secondary_y=False)
    fig2.update_yaxes(title_text="Variação (%)", secondary_y=True, showgrid=False)
    
    st.plotly_chart(fig2, use_container_width=True)

# Rodapé Técnico
st.divider()
st.caption("Fontes: Tesouro Nacional e Banco Central. Valores nominais. Projeção baseada em crescimento médio de 7% a.a.")
