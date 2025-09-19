# dashboard_supabase_fallback_completo.py
# 🌱 Dashboard de Metas - Streamlit + Supabase com fallback

import sys
import subprocess

# ----------------------------
# Instalação automática de pacotes se não estiverem presentes
# ----------------------------
def install(package):
    subprocess.check_call([sys.executable, "-m", "pip", "install", package])

for pkg in ["streamlit==1.27.0", "pandas==2.1.1", "plotly==5.16.1", "supabase==1.0.2"]:
    try:
        __import__(pkg.split("==")[0])
    except ImportError:
        install(pkg)

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from supabase import create_client, Client

# ----------------------------
# CONFIGURAÇÃO DA PÁGINA
# ----------------------------
st.set_page_config(
    page_title="Dashboard de Metas",
    layout="wide",
    page_icon="📊"
)

# ----------------------------
# CONFIGURAÇÃO DO SUPABASE
# ----------------------------
SUPABASE_URL = "https://tapyzjzwulidvxzipylw.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InRhcHl6anp3dWxpZHZ4emlweWx3Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTgyODkwMDEsImV4cCI6MjA3Mzg2NTAwMX0.9ha44r7PSPGYQIVkTO_D4KzNNUdnzpfa_IlfbFGjsVM"
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

# ----------------------------
# MAPEAMENTO DE NOMES
# ----------------------------
NOME_MAPPING = {
    'Werbet': 'Werbet', 'Werker Alencar': 'Werbet', 'Werbet Alencar': 'Werbet',
    'Pamela': 'Pamela', 'Pamela Crédita': 'Pamela', 'Pamela Cri': 'Pamela', 'Pamela Cristina': 'Pamela',
    'Ana Clara': 'Ana Clara', 'Ana Clara Souza': 'Ana Clara',
    'Danilo': 'Danilo', 'Danilo Neder': 'Danilo',
    'Natalie': 'Natalie', 'Natalie Lopes': 'Natalie',
    'Andressa': 'Andressa',
    'Rafael': 'Rafael', 'Rafael Miguel': 'Rafael',
    'Thaís': 'Thaís', 'Thais Mendonca': 'Thaís', 'Thais': 'Thaís', 'Thaki': 'Thaís'
}

# ----------------------------
# METAS MENSAIS
# ----------------------------
META_MENSAL_POR_COMERCIAL = {
    "Janeiro": { "Andressa": 22, "Rafael": 22, "Thaís": 22, "Ana Clara": 44, "Danilo": 44, "Pamela": 44, "Natalie": 44, "Werbet": 44 },
    "Fevereiro": { "Andressa": 20, "Rafael": 20, "Thaís": 20, "Ana Clara": 40, "Danilo": 40, "Pamela": 40, "Natalie": 40, "Werbet": 40 },
    "Março": { "Andressa": 21, "Rafael": 21, "Thaís": 21, "Ana Clara": 42, "Danilo": 42, "Pamela": 42, "Natalie": 42, "Werbet": 42 },
    "Abril": { "Andressa": 22, "Rafael": 22, "Thaís": 22, "Ana Clara": 44, "Danilo": 44, "Pamela": 44, "Natalie": 44, "Werbet": 44 },
    "Maio": { "Andressa": 22, "Rafael": 22, "Thaís": 22, "Ana Clara": 44, "Danilo": 44, "Pamela": 44, "Natalie": 44, "Werbet": 44 },
    "Junho": { "Andressa": 21, "Rafael": 21, "Thaís": 21, "Ana Clara": 42, "Danilo": 42, "Pamela": 42, "Natalie": 42, "Werbet": 42 },
    "Julho": { "Andressa": 23, "Rafael": 23, "Thaís": 23, "Ana Clara": 46, "Danilo": 46, "Pamela": 46, "Natalie": 46, "Werbet": 46 },
    "Agosto": { "Andressa": 21, "Rafael": 21, "Thaís": 21, "Ana Clara": 42, "Danilo": 42, "Pamela": 42, "Natalie": 42, "Werbet": 42 },
    "Setembro": { "Andressa": 22, "Rafael": 22, "Thaís": 22, "Ana Clara": 44, "Danilo": 44, "Pamela": 44, "Natalie": 44, "Werbet": 44 },
    "Outubro": { "Andressa": 23, "Rafael": 23, "Thaís": 23, "Ana Clara": 46, "Danilo": 46, "Pamela": 46, "Natalie": 46, "Werbet": 46 },
    "Novembro": { "Andressa": 21, "Rafael": 21, "Thaís": 21, "Ana Clara": 42, "Danilo": 42, "Pamela": 42, "Natalie": 42, "Werbet": 42 },
    "Dezembro": { "Andressa": 22, "Rafael": 22, "Thaís": 22, "Ana Clara": 44, "Danilo": 44, "Pamela": 44, "Natalie": 44, "Werbet": 44 }
}

# ----------------------------
# FUNÇÃO DE META TOTAL
# ----------------------------
def meta_mensal_total(nome, meses):
    return sum(META_MENSAL_POR_COMERCIAL[m].get(nome, 0) for m in meses)

# ----------------------------
# CARREGAR DADOS DO SUPABASE COM FALLBACK
# ----------------------------
@st.cache_data
def load_data():
    try:
        response = supabase.table("Projeto Perfomance comercial").select("*").execute()
        df = pd.DataFrame(response.data)
        if df.empty:
            raise ValueError("Tabela 'metas' está vazia no Supabase.")
        
        df['Data de Conclusão'] = pd.to_datetime(df['Data de Conclusão'], dayfirst=True, errors='coerce')
        df.dropna(subset=['Data de Conclusão'], inplace=True)
        df['Ano'] = df['Data de Conclusão'].dt.year
        df['Mês'] = df['Data de Conclusão'].dt.strftime('%B')
        meses_trad = {
            'January': 'Janeiro', 'February': 'Fevereiro', 'March': 'Março', 'April': 'Abril',
            'May': 'Maio', 'June': 'Junho', 'July': 'Julho', 'August': 'Agosto',
            'September': 'Setembro', 'October': 'Outubro', 'November': 'Novembro', 'December': 'Dezembro'
        }
        df['Mês'] = df['Mês'].map(meses_trad).fillna(df['Mês'])

        df['Comercial_Padronizado'] = df['Comercial/Capitão'].astype(str)
        for nome_ori, nome_pad in NOME_MAPPING.items():
            df.loc[df['Comercial/Capitão'].str.contains(nome_ori, case=False, na=False), 'Comercial_Padronizado'] = nome_pad

        nomes_validos = list(NOME_MAPPING.values())
        df = df[df['Comercial_Padronizado'].isin(nomes_validos)]
        return df

    except Exception as e:
        st.warning(f"⚠ Não foi possível carregar dados do Supabase: {str(e)}")
        st.info("Usando tabela de exemplo para o dashboard funcionar.")
        # TABELA DE EXEMPLO
        df_exemplo = pd.DataFrame({
            'Data de Conclusão': pd.to_datetime(['2025-01-15','2025-02-20','2025-03-10']),
            'Comercial/Capitão': ['Andressa','Rafael','Thaís']
        })
        df_exemplo['Ano'] = df_exemplo['Data de Conclusão'].dt.year
        df_exemplo['Mês'] = df_exemplo['Data de Conclusão'].dt.strftime('%B').map({
            'January':'Janeiro','February':'Fevereiro','March':'Março'
        }).fillna('Janeiro')
        df_exemplo['Comercial_Padronizado'] = df_exemplo['Comercial/Capitão']
        return df_exemplo

df = load_data()

# ----------------------------
# ESTILO CSS
# ----------------------------
st.markdown("""
<style>
.big-font { font-size:30px !important; font-weight: bold; color: #0d6efd; }
.stDataFrame div.row_heading, .stDataFrame div.col_heading { font-weight: bold; font-size: 16px; }
.stDataFrame td { padding: 8px; }
.metric-container {
    display: flex;
    justify-content: space-around;
    margin-bottom: 20px;
}
</style>
""", unsafe_allow_html=True)

# ----------------------------
# FUNÇÃO DE COR PARA KPI
# ----------------------------
def color_atingimento(val):
    if val >= 100:
        return 'background-color: #28a745; color: white; font-weight: bold'
    else:
        return 'background-color: #dc3545; color: white; font-weight: bold'

# ----------------------------
# DASHBOARD
# ----------------------------
if df.empty:
    st.error("❌ Nenhum dado disponível, nem mesmo a tabela de exemplo.")
else:
    tab_intro, tab_mensal, tab_anual, tab_totais, tab_explicacao = st.tabs([
        "✨ Apresentação", 
        "📊 Performance Mensal", 
        "📊 Consolidado Anual",
        "📈 Resultados Totais",
        "📘 Explicação"
    ])

    # ABA INTRO
    with tab_intro:
        st.markdown('<h1 class="big-font">🌱 Bem-vindo ao nosso painel de metas!</h1>', unsafe_allow_html=True)
        st.markdown("""
        Este não é apenas um lugar de números, mas um espaço para celebrarmos juntos o esforço e a superação diária.  
        Cada avanço é como uma semente que se transforma em fruto.  
        Aqui, transformamos resultados em **jogo coletivo**, onde a vitória é do **time todo**.  
        🚀 **Nosso objetivo: superar limites, crescer juntos e construir uma história de conquistas.**
        """)
        st.snow()

    # ABA PERFORMANCE MENSAL
    with tab_mensal:
        st.sidebar.header("Filtros - Mensal")
        anos_disponiveis = sorted(df['Ano'].unique())
        ano_selecionado = st.sidebar.selectbox("Ano", anos_disponiveis, index=len(anos_disponiveis)-1)
        ordem_meses = list(META_MENSAL_POR_COMERCIAL.keys())
        meses_disponiveis = sorted(df['Mês'].unique(), key=lambda x: ordem_meses.index(x) if x in ordem_meses else len(ordem_meses))
        meses_selecionados = st.sidebar.multiselect("Meses", meses_disponiveis, default=meses_disponiveis)
        df_filtrado = df[(df['Ano']==ano_selecionado) & (df['Mês'].isin(meses_selecionados))]

        if not df_filtrado.empty:
            tabela_mensal = df_filtrado.groupby('Comercial_Padronizado').size().reset_index(name='Realizado')
            tabela_mensal['Meta'] = tabela_mensal['Comercial_Padronizado'].apply(lambda x: meta_mensal_total(x, meses_selecionados))
            tabela_mensal['Atingimento (%)'] = (tabela_mensal['Realizado']/tabela_mensal['Meta']*100).round(2)
            
            st.dataframe(
                tabela_mensal.style.format({'Atingimento (%)':'{:.2f}%'}).applymap(color_atingimento, subset=['Atingimento (%)']),
                use_container_width=True
            )

            # Gráfico Barras
            fig_barras = px.bar(
                tabela_mensal, 
                x='Comercial_Padronizado', 
                y=['Realizado','Meta'],
                barmode='group',
                text_auto=True,
                title='Realizado vs Meta por Comercial'
            )
            st.plotly_chart(fig_barras, use_container_width=True)

            # Gráfico Pizza
            total_realizado = tabela_mensal['Realizado'].sum()
            total_meta = tabela_mensal['Meta'].sum()
            fig_pie = px.pie(
                names=['Atingido','Não atingido'],
                values=[total_realizado, max(0,total_meta-total_realizado)],
                color=['Atingido','Não atingido'],
                color_discrete_map={'Atingido':'#28a745','Não atingido':'#dc3545'},
                title="Progresso Mensal"
            )
            st.plotly_chart(fig_pie, use_container_width=True)
        else:
            st.warning("⚠ Nenhum dado encontrado para os filtros selecionados.")

    # ABA CONSOLIDADO ANUAL
    with tab_anual:
        st.sidebar.header("Filtros - Anual")
        meses_2_semestre_default = ["Julho","Agosto","Setembro","Outubro","Novembro","Dezembro"]
        meses_2_semestre = st.sidebar.multiselect("Meses (2º Semestre)", meses_2_semestre_default, default=meses_2_semestre_default)
        df_2_semestre = df[(df['Ano']==ano_selecionado) & (df['Mês'].isin(meses_2_semestre))]

        if not df_2_semestre.empty:
            tabela_anual = df_2_semestre.groupby('Comercial_Padronizado').size().reset_index(name='Realizado')
            tabela_anual['Meta'] = tabela_anual['Comercial_Padronizado'].apply(lambda x: meta_mensal_total(x, meses_2_semestre))
            tabela_anual['Atingimento (%)'] = (tabela_anual['Realizado']/tabela_anual['Meta']*100).round(2)

            st.dataframe(
                tabela_anual.style.format({'Atingimento (%)':'{:.2f}%'}).applymap(color_atingimento, subset=['Atingimento (%)']),
                use_container_width=True
            )

            # Gráfico Barras
            fig_barras_anual = px.bar(
                tabela_anual,
                x='Comercial_Padronizado',
                y=['Realizado','Meta'],
                barmode='group',
                text_auto=True,
                title="Realizado vs Meta - 2º Semestre"
            )
            st.plotly_chart(fig_barras_anual, use_container_width=True)

            # Radar Chart
            fig_radar = go.Figure()
            for i, row in tabela_anual.iterrows():
                fig_radar.add_trace(go.Scatterpolar(
                    r=[row['Realizado'], row['Meta']],
                    theta=['Realizado','Meta'],
                    fill='toself',
                    name=row['Comercial_Padronizado']
                ))
            fig_radar.update_layout(title='Comparativo Radar', polar=dict(radialaxis=dict(visible=True)))
            st.plotly_chart(fig_radar, use_container_width=True)
        else:
            st.warning("⚠ Nenhum dado encontrado para os filtros do 2º semestre.")

    # NOVA ABA - RESULTADOS TOTAIS
    with tab_totais:
        st.markdown("## 📈 Resumo Total")
        
        # Totais Mensais
        if not df_filtrado.empty:
            total_realizado_mensal = df_filtrado.shape[0]
            total_meta_mensal = sum(meta_mensal_total(nome, meses_selecionados) for nome in NOME_MAPPING.values())
            falta_mensal = max(0, total_meta_mensal - total_realizado_mensal)
            perc_mensal = (total_realizado_mensal / total_meta_mensal * 100) if total_meta_mensal > 0 else 0
            
            st.markdown("### 📊 Total Mensal")
            st.metric("Realizado", total_realizado_mensal)
            st.metric("Meta", total_meta_mensal)
            st.metric("Falta para atingir", falta_mensal)
            st.metric("Atingimento (%)", f"{perc_mensal:.2f}%")
        else:
            st.warning("⚠ Nenhum dado disponível para o total mensal.")

        st.markdown("---")

        # Totais Anuais
        if not df_2_semestre.empty:
            total_realizado_anual = df_2_semestre.shape[0]
            total_meta_anual = sum(meta_mensal_total(nome, meses_2_semestre) for nome in NOME_MAPPING.values())
            falta_anual = max(0, total_meta_anual - total_realizado_anual)
            perc_anual = (total_realizado_anual / total_meta_anual * 100) if total_meta_anual > 0 else 0
            
            st.markdown("### 🗓️ Total Anual (2º Semestre)")
            st.metric("Realizado", total_realizado_anual)
            st.metric("Meta", total_meta_anual)
            st.metric("Falta para atingir", falta_anual)
            st.metric("Atingimento (%)", f"{perc_anual:.2f}%")
        else:
            st.warning("⚠ Nenhum dado disponível para o total anual.")

    # ABA EXPLICAÇÃO
    with tab_explicacao:
        st.markdown("""
        # 📘 Como interpretar os resultados

        **1️⃣ Realizado:** Quantidade de contas ou tarefas concluídas pelo comercial no período selecionado.

        **2️⃣ Meta:** Valor esperado para o período de acordo com o planejamento.

        **3️⃣ Atingimento (%):** Percentual de conclusão da meta.  
        - ✅ Verde: meta atingida ou superada.  
        - ❌ Vermelho: meta não atingida.  

        **4️⃣ Gráficos de Barras:** Mostram comparação individual entre o realizado e a meta.

        **5️⃣ Gráfico de Pizza:** Indica de forma visual o quanto da meta foi cumprida pelo time.

        **6️⃣ Radar Chart:** Permite comparar desempenho entre comerciais de forma consolidada.

        **7️⃣ Aba Resultados Totais:** Mostra os totais mensais e anuais consolidados, incluindo o quanto falta para atingir a meta.

        > Dica: Sempre combine filtros de ano e meses para analisar tendências e evolução do time.
        """)
