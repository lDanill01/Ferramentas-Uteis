"""
Detector de Anomalias com Machine Learning
Identifica automaticamente dados atípicos em datasets
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import io

# Bibliotecas de Machine Learning
from sklearn.ensemble import IsolationForest
from sklearn.preprocessing import StandardScaler
from sklearn.covariance import EllipticEnvelope
from scipy import stats

# Importar configurações
import sys
sys.path.append('..')
from config import (
    configurar_pagina, aplicar_estilo_global, criar_header, 
    criar_divider, criar_botao_download_excel, criar_botao_download_csv
)

# Configuração da página
configurar_pagina("Detector de Anomalias", "🔍")
aplicar_estilo_global()

# Estilos adicionais
st.markdown("""
    <style>
    .anomaly-card {
        padding: 1.5rem;
        border-radius: 12px;
        margin: 1rem 0;
        box-shadow: 0 4px 15px rgba(0,0,0,0.08);
    }
    
    .method-selector {
        padding: 1rem;
        border-radius: 10px;
        margin: 0.5rem 0;
        cursor: pointer;
        transition: all 0.3s ease;
        border: 2px solid transparent;
    }
    
    .method-selector:hover {
        transform: translateY(-2px);
        border-color: #667eea;
    }
    
    .method-selected {
        border-color: #667eea;
        background: rgba(102, 126, 234, 0.1);
    }
    
    .stat-box {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 1.5rem;
        border-radius: 10px;
        text-align: center;
        margin: 0.5rem 0;
    }
    
    .stat-box h3 {
        color: white;
        margin: 0;
        font-size: 2rem;
    }
    
    .stat-box p {
        color: rgba(255,255,255,0.9);
        margin: 0.5rem 0 0 0;
    }
    
    .anomaly-badge {
        background: #dc3545;
        color: white;
        padding: 0.3rem 0.8rem;
        border-radius: 20px;
        font-size: 0.85rem;
        font-weight: 600;
    }
    
    .normal-badge {
        background: #28a745;
        color: white;
        padding: 0.3rem 0.8rem;
        border-radius: 20px;
        font-size: 0.85rem;
        font-weight: 600;
    }
    </style>
""", unsafe_allow_html=True)

# Cabeçalho
criar_header("🔍 Detector de Anomalias", "Identifique automaticamente dados atípicos com Machine Learning")

# Inicializar session_state
if 'df_anomalias' not in st.session_state:
    st.session_state.df_anomalias = None
if 'resultados_deteccao' not in st.session_state:
    st.session_state.resultados_deteccao = None
if 'metodo_selecionado' not in st.session_state:
    st.session_state.metodo_selecionado = None

# ========================================
# FUNÇÕES DE DETECÇÃO
# ========================================

def detectar_anomalias_iqr(df, coluna, multiplicador=1.5):
    """Detecção usando Intervalo Interquartil (IQR)"""
    Q1 = df[coluna].quantile(0.25)
    Q3 = df[coluna].quantile(0.75)
    IQR = Q3 - Q1
    
    limite_inferior = Q1 - multiplicador * IQR
    limite_superior = Q3 + multiplicador * IQR
    
    anomalias = (df[coluna] < limite_inferior) | (df[coluna] > limite_superior)
    
    return anomalias, limite_inferior, limite_superior

def detectar_anomalias_zscore(df, coluna, threshold=3):
    """Detecção usando Z-Score"""
    z_scores = np.abs(stats.zscore(df[coluna].dropna()))
    anomalias = z_scores > threshold
    
    # Ajustar para o tamanho original
    resultado = pd.Series([False] * len(df), index=df.index)
    resultado.loc[df[coluna].notna()] = anomalias
    
    return resultado

def detectar_anomalias_isolation_forest(df, colunas, contaminacao=0.1):
    """Detecção usando Isolation Forest"""
    # Preparar dados
    X = df[colunas].copy()
    
    # Remover NaN
    mask_valido = X.notna().all(axis=1)
    X_clean = X[mask_valido]
    
    if len(X_clean) == 0:
        return pd.Series([False] * len(df), index=df.index)
    
    # Normalizar
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X_clean)
    
    # Detectar
    iso_forest = IsolationForest(contamination=contaminacao, random_state=42)
    predicoes = iso_forest.fit_predict(X_scaled)
    
    # Criar série de resultados
    resultado = pd.Series([False] * len(df), index=df.index)
    resultado.loc[mask_valido] = predicoes == -1
    
    return resultado

def detectar_anomalias_elliptic(df, colunas, contaminacao=0.1):
    """Detecção usando Elliptic Envelope"""
    X = df[colunas].copy()
    
    mask_valido = X.notna().all(axis=1)
    X_clean = X[mask_valido]
    
    if len(X_clean) < 2:
        return pd.Series([False] * len(df), index=df.index)
    
    try:
        scaler = StandardScaler()
        X_scaled = scaler.fit_transform(X_clean)
        
        envelope = EllipticEnvelope(contamination=contaminacao, random_state=42)
        predicoes = envelope.fit_predict(X_scaled)
        
        resultado = pd.Series([False] * len(df), index=df.index)
        resultado.loc[mask_valido] = predicoes == -1
        
        return resultado
    except:
        return pd.Series([False] * len(df), index=df.index)

# ========================================
# UPLOAD DE DADOS
# ========================================

st.markdown("### 📤 Upload dos Dados")

col1, col2 = st.columns([3, 1])

with col1:
    arquivo = st.file_uploader(
        "Selecione o arquivo (CSV ou Excel)",
        type=["csv", "xlsx", "xls"],
        help="Faça upload do arquivo com os dados para análise"
    )

with col2:
    st.markdown("<br>", unsafe_allow_html=True)
    usar_exemplo = st.button("🎲 Usar Exemplo", use_container_width=True, type="primary")

# Processar dados de exemplo
if usar_exemplo:
    np.random.seed(42)
    n_samples = 200
    
    # Dados normais
    valores_normais = np.random.normal(100, 15, n_samples - 20)
    
    # Adicionar anomalias
    anomalias = np.random.uniform(150, 200, 10)
    anomalias_baixas = np.random.uniform(20, 40, 10)
    
    valores = np.concatenate([valores_normais, anomalias, anomalias_baixas])
    
    df_exemplo = pd.DataFrame({
        'ID': range(1, len(valores) + 1),
        'Valor': valores,
        'Categoria': np.random.choice(['A', 'B', 'C'], len(valores)),
        'Data': pd.date_range('2024-01-01', periods=len(valores), freq='D')
    })
    
    st.session_state.df_anomalias = df_exemplo
    st.success("✅ Dados de exemplo carregados! (200 registros com 20 anomalias)")
    st.rerun()

# Processar upload
if arquivo and st.session_state.df_anomalias is None:
    try:
        if arquivo.name.endswith('.csv'):
            df = pd.read_csv(arquivo)
        else:
            df = pd.read_excel(arquivo)
        
        st.session_state.df_anomalias = df
        st.success(f"✅ Arquivo carregado: {len(df)} registros, {len(df.columns)} colunas")
        st.rerun()
    
    except Exception as e:
        st.error(f"❌ Erro ao carregar arquivo: {str(e)}")

if st.session_state.df_anomalias is not None:
    df = st.session_state.df_anomalias
    
    criar_divider()
    
    # Informações do dataset
    st.markdown("### 📊 Informações do Dataset")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("📄 Registros", f"{len(df):,}")
    with col2:
        st.metric("📋 Colunas", f"{len(df.columns):,}")
    with col3:
        colunas_numericas = df.select_dtypes(include=[np.number]).columns
        st.metric("🔢 Colunas Numéricas", len(colunas_numericas))
    with col4:
        st.metric("💾 Memória", f"{df.memory_usage(deep=True).sum() / 1024:.1f} KB")
    
    criar_divider()
    
    # Preview dos dados
    with st.expander("👁️ Preview dos Dados", expanded=False):
        st.dataframe(df.head(10), use_container_width=True)
    
    criar_divider()
    
    # ========================================
    # CONFIGURAÇÃO DA DETECÇÃO
    # ========================================
    
    st.markdown("### ⚙️ Configuração da Detecção")
    
    # Seleção de método
    st.markdown("#### 🎯 Método de Detecção")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        if st.button("📊 IQR\n(Interquartil)", use_container_width=True, 
                    type="primary" if st.session_state.metodo_selecionado == "IQR" else "secondary"):
            st.session_state.metodo_selecionado = "IQR"
            st.rerun()
    
    with col2:
        if st.button("📈 Z-Score\n(Estatístico)", use_container_width=True,
                    type="primary" if st.session_state.metodo_selecionado == "ZScore" else "secondary"):
            st.session_state.metodo_selecionado = "ZScore"
            st.rerun()
    
    with col3:
        if st.button("🤖 Isolation Forest\n(ML)", use_container_width=True,
                    type="primary" if st.session_state.metodo_selecionado == "IsolationForest" else "secondary"):
            st.session_state.metodo_selecionado = "IsolationForest"
            st.rerun()
    
    with col4:
        if st.button("🎯 Elliptic Envelope\n(ML)", use_container_width=True,
                    type="primary" if st.session_state.metodo_selecionado == "Elliptic" else "secondary"):
            st.session_state.metodo_selecionado = "Elliptic"
            st.rerun()
    
    # Descrição dos métodos
    if st.session_state.metodo_selecionado:
        criar_divider()
        
        descricoes = {
            "IQR": """
            **📊 Intervalo Interquartil (IQR)**
            - Método estatístico clássico
            - Baseado em quartis (Q1 e Q3)
            - Ideal para distribuições unimodais
            - Rápido e interpretável
            - Melhor para dados univariados
            """,
            "ZScore": """
            **📈 Z-Score**
            - Mede desvio da média em desvios-padrão
            - Assume distribuição normal
            - Threshold típico: 3 desvios
            - Sensível a outliers extremos
            - Simples e eficiente
            """,
            "IsolationForest": """
            **🤖 Isolation Forest**
            - Algoritmo de Machine Learning
            - Não assume distribuição específica
            - Excelente para dados multivariados
            - Detecta anomalias complexas
            - Recomendado para datasets grandes
            """,
            "Elliptic": """
            **🎯 Elliptic Envelope**
            - Assume distribuição gaussiana multivariada
            - Cria envelope elíptico dos dados normais
            - Bom para correlações entre variáveis
            - Robusto a ruído
            - Ideal para 2+ dimensões
            """
        }
        
        st.info(descricoes[st.session_state.metodo_selecionado])
    
    criar_divider()
    
    # Seleção de colunas
    st.markdown("#### 🎯 Seleção de Colunas para Análise")
    
    colunas_numericas = df.select_dtypes(include=[np.number]).columns.tolist()
    
    if not colunas_numericas:
        st.error("❌ Nenhuma coluna numérica encontrada no dataset")
    else:
        if st.session_state.metodo_selecionado in ["IQR", "ZScore"]:
            # Métodos univariados
            coluna_analise = st.selectbox(
                "Selecione a coluna para análise",
                colunas_numericas,
                help="Análise será feita nesta coluna"
            )
        else:
            # Métodos multivariados
            colunas_analise = st.multiselect(
                "Selecione as colunas para análise",
                colunas_numericas,
                default=colunas_numericas[:3] if len(colunas_numericas) >= 3 else colunas_numericas,
                help="Selecione uma ou mais colunas para análise multivariada"
            )
        
        criar_divider()
        
        # Parâmetros específicos
        st.markdown("#### ⚙️ Parâmetros de Detecção")
        
        col1, col2 = st.columns(2)
        
        with col1:
            if st.session_state.metodo_selecionado == "IQR":
                multiplicador_iqr = st.slider(
                    "Multiplicador IQR",
                    min_value=1.0,
                    max_value=3.0,
                    value=1.5,
                    step=0.1,
                    help="Quanto maior, menos sensível (1.5 é padrão)"
                )
            
            elif st.session_state.metodo_selecionado == "ZScore":
                threshold_zscore = st.slider(
                    "Threshold Z-Score",
                    min_value=2.0,
                    max_value=4.0,
                    value=3.0,
                    step=0.1,
                    help="Número de desvios-padrão (3 é padrão)"
                )
            
            elif st.session_state.metodo_selecionado in ["IsolationForest", "Elliptic"]:
                contaminacao = st.slider(
                    "Taxa de Contaminação Esperada",
                    min_value=0.01,
                    max_value=0.30,
                    value=0.10,
                    step=0.01,
                    format="%.2f",
                    help="Proporção esperada de anomalias (10% é padrão)"
                )
        
        with col2:
            st.markdown("**💡 Dicas:**")
            if st.session_state.metodo_selecionado == "IQR":
                st.markdown("""
                - 1.5: Mais sensível (mais anomalias)
                - 2.0-3.0: Menos sensível
                - Recomendado: 1.5 para maioria dos casos
                """)
            elif st.session_state.metodo_selecionado == "ZScore":
                st.markdown("""
                - 2.0: Muito sensível (5% de anomalias)
                - 3.0: Padrão (0.3% de anomalias)
                - 4.0: Pouco sensível
                """)
            else:
                st.markdown("""
                - 0.05: Poucos outliers esperados
                - 0.10: Proporção moderada (padrão)
                - 0.20+: Muitos outliers esperados
                """)
        
        criar_divider()
        
        # Botão de detecção
        if st.button("🔍 Detectar Anomalias", type="primary", use_container_width=True):
            with st.spinner("Processando detecção..."):
                try:
                    df_resultado = df.copy()
                    
                    # Executar detecção
                    if st.session_state.metodo_selecionado == "IQR":
                        anomalias, limite_inf, limite_sup = detectar_anomalias_iqr(
                            df_resultado, coluna_analise, multiplicador_iqr
                        )
                        df_resultado['Anomalia'] = anomalias
                        
                        info_metodo = {
                            'limite_inferior': limite_inf,
                            'limite_superior': limite_sup,
                            'coluna': coluna_analise
                        }
                    
                    elif st.session_state.metodo_selecionado == "ZScore":
                        anomalias = detectar_anomalias_zscore(
                            df_resultado, coluna_analise, threshold_zscore
                        )
                        df_resultado['Anomalia'] = anomalias
                        
                        info_metodo = {
                            'threshold': threshold_zscore,
                            'coluna': coluna_analise
                        }
                    
                    elif st.session_state.metodo_selecionado == "IsolationForest":
                        if not colunas_analise:
                            st.error("❌ Selecione pelo menos uma coluna")
                            st.stop()
                        
                        anomalias = detectar_anomalias_isolation_forest(
                            df_resultado, colunas_analise, contaminacao
                        )
                        df_resultado['Anomalia'] = anomalias
                        
                        info_metodo = {
                            'contaminacao': contaminacao,
                            'colunas': colunas_analise
                        }
                    
                    elif st.session_state.metodo_selecionado == "Elliptic":
                        if not colunas_analise or len(colunas_analise) < 2:
                            st.error("❌ Selecione pelo menos 2 colunas para Elliptic Envelope")
                            st.stop()
                        
                        anomalias = detectar_anomalias_elliptic(
                            df_resultado, colunas_analise, contaminacao
                        )
                        df_resultado['Anomalia'] = anomalias
                        
                        info_metodo = {
                            'contaminacao': contaminacao,
                            'colunas': colunas_analise
                        }
                    
                    # Salvar resultados
                    st.session_state.resultados_deteccao = {
                        'df': df_resultado,
                        'metodo': st.session_state.metodo_selecionado,
                        'info': info_metodo,
                        'n_anomalias': anomalias.sum(),
                        'n_normais': (~anomalias).sum(),
                        'percentual': (anomalias.sum() / len(df_resultado)) * 100
                    }
                    
                    st.success(f"✅ Detecção concluída! {anomalias.sum()} anomalia(s) encontrada(s)")
                    st.rerun()
                
                except Exception as e:
                    st.error(f"❌ Erro na detecção: {str(e)}")
                    import traceback
                    st.code(traceback.format_exc())

# ========================================
# RESULTADOS
# ========================================

if st.session_state.resultados_deteccao:
    criar_divider()
    
    resultados = st.session_state.resultados_deteccao
    df_resultado = resultados['df']
    
    st.markdown("### 📊 Resultados da Detecção")
    
    # Estatísticas
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown(f"""
        <div class="stat-box">
            <h3>{resultados['n_anomalias']}</h3>
            <p>Anomalias Detectadas</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown(f"""
        <div class="stat-box" style="background: linear-gradient(135deg, #28a745 0%, #20c997 100%);">
            <h3>{resultados['n_normais']}</h3>
            <p>Dados Normais</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown(f"""
        <div class="stat-box" style="background: linear-gradient(135deg, #ffc107 0%, #ff9800 100%);">
            <h3>{resultados['percentual']:.1f}%</h3>
            <p>Taxa de Anomalias</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col4:
        st.markdown(f"""
        <div class="stat-box" style="background: linear-gradient(135deg, #17a2b8 0%, #138496 100%);">
            <h3>{resultados['metodo']}</h3>
            <p>Método Utilizado</p>
        </div>
        """, unsafe_allow_html=True)
    
    criar_divider()
    
    # Visualizações
    tabs = st.tabs(["📊 Visualizações", "📋 Dados Detalhados", "💡 Recomendações", "📥 Download"])
    
    with tabs[0]:
        st.markdown("### 📈 Visualização das Anomalias")
        
        # Gráfico 1: Scatter plot (univariado ou bivariado)
        if resultados['metodo'] in ["IQR", "ZScore"]:
            col_analise = resultados['info']['coluna']
            
            fig = go.Figure()
            
            # Dados normais
            df_normal = df_resultado[~df_resultado['Anomalia']]
            fig.add_trace(go.Scatter(
                x=df_normal.index,
                y=df_normal[col_analise],
                mode='markers',
                name='Normal',
                marker=dict(color='#28a745', size=8, opacity=0.6)
            ))
            
            # Anomalias
            df_anomalo = df_resultado[df_resultado['Anomalia']]
            fig.add_trace(go.Scatter(
                x=df_anomalo.index,
                y=df_anomalo[col_analise],
                mode='markers',
                name='Anomalia',
                marker=dict(color='#dc3545', size=12, symbol='x')
            ))
            
            # Limites (se IQR)
            if resultados['metodo'] == "IQR":
                fig.add_hline(
                    y=resultados['info']['limite_superior'],
                    line_dash="dash",
                    line_color="red",
                    annotation_text="Limite Superior"
                )
                fig.add_hline(
                    y=resultados['info']['limite_inferior'],
                    line_dash="dash",
                    line_color="red",
                    annotation_text="Limite Inferior"
                )
            
            fig.update_layout(
                title=f"Detecção de Anomalias - {col_analise}",
                xaxis_title="Índice",
                yaxis_title=col_analise,
                height=500,
                hovermode='closest'
            )
            
            st.plotly_chart(fig, use_container_width=True)
        
        else:
            # Gráfico bivariado para métodos ML
            colunas = resultados['info']['colunas']
            
            if len(colunas) >= 2:
                col1, col2 = colunas[0], colunas[1]
                
                fig = go.Figure()
                
                df_normal = df_resultado[~df_resultado['Anomalia']]
                fig.add_trace(go.Scatter(
                    x=df_normal[col1],
                    y=df_normal[col2],
                    mode='markers',
                    name='Normal',
                    marker=dict(color='#28a745', size=8, opacity=0.6)
                ))
                
                df_anomalo = df_resultado[df_resultado['Anomalia']]
                fig.add_trace(go.Scatter(
                    x=df_anomalo[col1],
                    y=df_anomalo[col2],
                    mode='markers',
                    name='Anomalia',
                    marker=dict(color='#dc3545', size=12, symbol='x')
                ))
                
                fig.update_layout(
                    title=f"Detecção Multivariada - {col1} vs {col2}",
                    xaxis_title=col1,
                    yaxis_title=col2,
                    height=500
                )
                
                st.plotly_chart(fig, use_container_width=True)
        
        criar_divider()
        
        # Gráfico 2: Distribuição
        st.markdown("### 📊 Distribuição dos Dados")
        
        col_plot = resultados['info'].get('coluna') or resultados['info']['colunas'][0]
        
        fig = make_subplots(rows=1, cols=2, subplot_titles=("Histograma", "Boxplot"))
        
        # Histograma
        fig.add_trace(
            go.Histogram(
                x=df_resultado[~df_resultado['Anomalia']][col_plot],
                name='Normal',
                marker_color='#28a745',
                opacity=0.7
            ),
            row=1, col=1
        )
        
        fig.add_trace(
            go.Histogram(
                x=df_resultado[df_resultado['Anomalia']][col_plot],
                name='Anomalia',
                marker_color='#dc3545',
                opacity=0.7
            ),
            row=1, col=1
        )
        
        # Boxplot
        fig.add_trace(
            go.Box(
                y=df_resultado[~df_resultado['Anomalia']][col_plot],
                name='Normal',
                marker_color='#28a745'
            ),
            row=1, col=2
        )
        
        fig.add_trace(
            go.Box(
                y=df_resultado[df_resultado['Anomalia']][col_plot],
                name='Anomalia',
                marker_color='#dc3545'
            ),
            row=1, col=2
        )
        
        fig.update_layout(height=400, showlegend=True)
        st.plotly_chart(fig, use_container_width=True)
    
    with tabs[1]:
        st.markdown("### 📋 Registros com Anomalias")
        
        df_anomalias = df_resultado[df_resultado['Anomalia']].copy()
        
        if len(df_anomalias) > 0:
            st.dataframe(df_anomalias, use_container_width=True)
            
            criar_divider()
            
            st.markdown("### 📊 Estatísticas Comparativas")
            
            col_comparacao = resultados['info'].get('coluna') or resultados['info']['colunas'][0]
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("**Dados Normais:**")
                st.dataframe(
                    df_resultado[~df_resultado['Anomalia']][col_comparacao].describe(),
                    use_container_width=True
                )
            
            with col2:
                st.markdown("**Anomalias:**")
                st.dataframe(
                    df_resultado[df_resultado['Anomalia']][col_comparacao].describe(),
                    use_container_width=True
                )
        else:
            st.info("✅ Nenhuma anomalia detectada no dataset")
    
    with tabs[2]:
        st.markdown("### 💡 Recomendações e Insights")
        
        if resultados['n_anomalias'] > 0:
            st.markdown(f"""
            #### 🔍 Análise Geral
            
            - **Total de anomalias:** {resultados['n_anomalias']} ({resultados['percentual']:.1f}% do dataset)
            - **Método utilizado:** {resultados['metodo']}
            - **Dados normais:** {resultados['n_normais']}
            
            #### 🎯 Possíveis Causas das Anomalias
            
            1. **Erros de Coleta/Digitação**
               - Valores digitados incorretamente
               - Falhas em sensores ou sistemas
               - Conversão de unidades incorreta
            
            2. **Eventos Reais Atípicos**
               - Picos de demanda/vendas
               - Períodos de baixa atividade
               - Eventos extraordinários
            
            3. **Problemas Técnicos**
               - Duplicação de registros
               - Valores default incorretos
               - Problemas de integração
            
            #### ✅ Ações Recomendadas
            
            1. **Investigar registros anômalos individualmente**
            2. **Validar com fontes originais** se possível
            3. **Considerar contexto do negócio** antes de remover
            4. **Documentar decisões** sobre tratamento
            5. **Criar regras de validação** para dados futuros
            
            #### ⚠️ Cuidados Importantes
            
            - **Nem toda anomalia é erro:** Alguns outliers são legítimos
            - **Contexto importa:** Analise o significado dos dados
            - **Não remova automaticamente:** Investigue antes de excluir
            - **Considere sazonalidade:** Picos podem ser normais em certos períodos
            """)
            
            # Análise específica do método
            if resultados['metodo'] == "IQR":
                st.markdown(f"""
                #### 📊 Detalhes do Método IQR
                
                - **Limite Inferior:** {resultados['info']['limite_inferior']:.2f}
                - **Limite Superior:** {resultados['info']['limite_superior']:.2f}
                - **Coluna analisada:** {resultados['info']['coluna']}
                
                **Interpretação:** Valores fora desses limites foram considerados anômalos.
                """)
            
            elif resultados['metodo'] == "ZScore":
                st.markdown(f"""
                #### 📈 Detalhes do Método Z-Score
                
                - **Threshold:** {resultados['info']['threshold']} desvios-padrão
                - **Coluna analisada:** {resultados['info']['coluna']}
                
                **Interpretação:** Valores com Z-Score > {resultados['info']['threshold']} foram flagados.
                """)
            
            elif resultados['metodo'] in ["IsolationForest", "Elliptic"]:
                st.markdown(f"""
                #### 🤖 Detalhes do Método {resultados['metodo']}
                
                - **Taxa de contaminação:** {resultados['info']['contaminacao']:.1%}
                - **Colunas analisadas:** {', '.join(resultados['info']['colunas'])}
                
                **Interpretação:** Algoritmo identificou padrões multivariados anômalos.
                """)
        
        else:
            st.success("""
            ✅ **Nenhuma anomalia detectada!**
            
            Isso pode significar:
            - Dados de alta qualidade
            - Processo de coleta bem controlado
            - Parâmetros de detecção muito conservadores
            
            **Sugestão:** Experimente ajustar os parâmetros para aumentar a sensibilidade.
            """)
    
    with tabs[3]:
        st.markdown("### 📥 Download dos Resultados")
        
        st.info("💡 Exporte os dados com a coluna 'Anomalia' adicionada")
        
        col1, col2 = st.columns(2)
        
        with col1:
            # Excel
            output_excel = io.BytesIO()
            with pd.ExcelWriter(output_excel, engine='xlsxwriter') as writer:
                # Aba completa
                df_resultado.to_excel(writer, sheet_name='Dados Completos', index=False)
                
                # Aba só anomalias
                if len(df_resultado[df_resultado['Anomalia']]) > 0:
                    df_resultado[df_resultado['Anomalia']].to_excel(
                        writer, sheet_name='Apenas Anomalias', index=False
                    )
                
                # Aba de estatísticas
                stats_df = pd.DataFrame({
                    'Métrica': ['Total de Registros', 'Anomalias', 'Dados Normais', 'Taxa de Anomalias'],
                    'Valor': [
                        len(df_resultado),
                        resultados['n_anomalias'],
                        resultados['n_normais'],
                        f"{resultados['percentual']:.2f}%"
                    ]
                })
                stats_df.to_excel(writer, sheet_name='Estatísticas', index=False)
            
            output_excel.seek(0)
            
            st.download_button(
                label="📥 Baixar Excel Completo",
                data=output_excel,
                file_name="deteccao_anomalias.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                use_container_width=True
            )
        
        with col2:
            # CSV
            csv = df_resultado.to_csv(index=False).encode('utf-8')
            
            st.download_button(
                label="📥 Baixar CSV",
                data=csv,
                file_name="deteccao_anomalias.csv",
                mime="text/csv",
                use_container_width=True
            )
        
        criar_divider()
        
        # Relatório resumido
        st.markdown("### 📄 Relatório Resumido")
        
        relatorio = f"""
# RELATÓRIO DE DETECÇÃO DE ANOMALIAS

## Informações Gerais
- **Data da Análise:** {pd.Timestamp.now().strftime('%d/%m/%Y %H:%M')}
- **Método Utilizado:** {resultados['metodo']}
- **Total de Registros:** {len(df_resultado):,}

## Resultados
- **Anomalias Detectadas:** {resultados['n_anomalias']} ({resultados['percentual']:.2f}%)
- **Dados Normais:** {resultados['n_normais']} ({100 - resultados['percentual']:.2f}%)

## Parâmetros da Detecção
"""
        
        if resultados['metodo'] == "IQR":
            relatorio += f"""
- Coluna Analisada: {resultados['info']['coluna']}
- Limite Inferior: {resultados['info']['limite_inferior']:.2f}
- Limite Superior: {resultados['info']['limite_superior']:.2f}
"""
        elif resultados['metodo'] == "ZScore":
            relatorio += f"""
- Coluna Analisada: {resultados['info']['coluna']}
- Threshold Z-Score: {resultados['info']['threshold']}
"""
        else:
            relatorio += f"""
- Colunas Analisadas: {', '.join(resultados['info']['colunas'])}
- Taxa de Contaminação: {resultados['info']['contaminacao']:.1%}
"""
        
        relatorio += """

## Recomendações
1. Investigar individualmente os registros flagados como anômalos
2. Validar com fontes originais quando possível
3. Considerar contexto do negócio antes de tomar ações
4. Documentar decisões sobre tratamento das anomalias

## Próximos Passos
- [ ] Revisar anomalias detectadas
- [ ] Validar com responsáveis pelos dados
- [ ] Decidir tratamento (corrigir, remover ou manter)
- [ ] Implementar regras de validação
"""
        
        st.download_button(
            label="📄 Baixar Relatório (TXT)",
            data=relatorio,
            file_name="relatorio_anomalias.txt",
            mime="text/plain",
            use_container_width=True
        )

else:
    st.info("👆 Faça upload de um arquivo ou use dados de exemplo para começar")
    
    criar_divider()
    
    # Informações sobre os métodos
    st.markdown("### 📚 Sobre os Métodos de Detecção")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("""
        #### 📊 IQR (Intervalo Interquartil)
        
        **Como funciona:**
        - Calcula Q1 (25%) e Q3 (75%)
        - Define intervalo: Q1 - 1.5×IQR a Q3 + 1.5×IQR
        - Valores fora são anomalias
        
        **Vantagens:**
        - ✅ Simples e intuitivo
        - ✅ Robusto a outliers moderados
        - ✅ Não assume distribuição normal
        
        **Quando usar:**
        - Análise univariada (1 coluna)
        - Dados com distribuição assimétrica
        - Necessidade de interpretação clara
        
        ---
        
        #### 📈 Z-Score
        
        **Como funciona:**
        - Mede distância da média em desvios-padrão
        - Z = (x - μ) / σ
        - |Z| > threshold = anomalia
        
        **Vantagens:**
        - ✅ Estatisticamente fundamentado
        - ✅ Fácil interpretação
        - ✅ Rápido computacionalmente
        
        **Quando usar:**
        - Dados aproximadamente normais
        - Uma variável por vez
        - Threshold bem definido (geralmente 3)
        """)
    
    with col2:
        st.markdown("""
        #### 🤖 Isolation Forest
        
        **Como funciona:**
        - Isola observações usando árvores aleatórias
        - Anomalias são isoladas mais rapidamente
        - Score baseado em profundidade de isolamento
        
        **Vantagens:**
        - ✅ Não assume distribuição
        - ✅ Excelente para múltiplas dimensões
        - ✅ Eficiente para grandes datasets
        - ✅ Detecta padrões complexos
        
        **Quando usar:**
        - Análise multivariada (várias colunas)
        - Distribuições complexas/desconhecidas
        - Grandes volumes de dados
        - Anomalias não-lineares
        
        ---
        
        #### 🎯 Elliptic Envelope
        
        **Como funciona:**
        - Assume distribuição gaussiana
        - Cria envelope elíptico dos dados normais
        - Pontos fora do envelope = anomalias
        
        **Vantagens:**
        - ✅ Captura correlações entre variáveis
        - ✅ Robusto a pequenas contaminações
        - ✅ Bom para dados multivariados
        
        **Quando usar:**
        - 2+ variáveis correlacionadas
        - Distribuição aproximadamente normal
        - Quando correlações importam
        """)
    
    criar_divider()
    
    # Guia de uso
    st.markdown("### 🚀 Como Usar o Detector")
    
    st.markdown("""
    #### Passo a Passo
    
    1. **📤 Upload dos Dados**
       - Carregue arquivo CSV ou Excel
       - Ou use dados de exemplo para testar
    
    2. **🎯 Escolha o Método**
       - IQR/Z-Score: Para análise de uma coluna
       - Isolation Forest/Elliptic: Para múltiplas colunas
    
    3. **⚙️ Configure Parâmetros**
       - Selecione colunas para análise
       - Ajuste sensibilidade conforme necessidade
    
    4. **🔍 Execute a Detecção**
       - Clique em "Detectar Anomalias"
       - Aguarde processamento
    
    5. **📊 Analise Resultados**
       - Visualize gráficos e estatísticas
       - Revise registros anômalos
       - Leia recomendações
    
    6. **📥 Exporte Resultados**
       - Baixe dados com flag de anomalia
       - Salve relatório de análise
    
    #### 💡 Dicas Importantes
    
    - **Comece conservador:** Use parâmetros padrão primeiro
    - **Valide manualmente:** Nem toda anomalia é erro
    - **Contexto importa:** Considere características do negócio
    - **Documente decisões:** Registre o que fez com anomalias
    - **Itere:** Ajuste parâmetros se necessário
    """)
    
    criar_divider()
    
    # Casos de uso
    st.markdown("### 🎯 Casos de Uso Comuns")
    
    with st.expander("💰 Detecção de Fraudes Financeiras"):
        st.markdown("""
        **Cenário:** Identificar transações suspeitas
        
        **Recomendação:**
        - Método: **Isolation Forest**
        - Colunas: Valor, horário, frequência, localização
        - Contaminação: 0.01-0.05 (1-5%)
        
        **Por quê?**
        - Fraudes são raras mas complexas
        - Múltiplas variáveis envolvidas
        - Padrões não-lineares
        """)
    
    with st.expander("📊 Controle de Qualidade Industrial"):
        st.markdown("""
        **Cenário:** Identificar produtos defeituosos
        
        **Recomendação:**
        - Método: **Z-Score** ou **IQR**
        - Colunas: Medidas de qualidade (peso, dimensões)
        - Threshold: 3 desvios (Z-Score)
        
        **Por quê?**
        - Medidas tendem a seguir distribuição normal
        - Limites de especificação claros
        - Interpretação direta para operadores
        """)
    
    with st.expander("🏥 Análise de Dados Médicos"):
        st.markdown("""
        **Cenário:** Identificar exames atípicos
        
        **Recomendação:**
        - Método: **Elliptic Envelope**
        - Colunas: Múltiplos biomarcadores correlacionados
        - Contaminação: 0.05-0.10
        
        **Por quê?**
        - Biomarcadores são correlacionados
        - Distribuição aproximadamente gaussiana
        - Anomalias multivariadas importantes
        """)
    
    with st.expander("🛒 E-commerce: Detecção de Comportamento Anômalo"):
        st.markdown("""
        **Cenário:** Identificar padrões suspeitos de compra
        
        **Recomendação:**
        - Método: **Isolation Forest**
        - Colunas: Valor, quantidade, frequência, horário
        - Contaminação: 0.10
        
        **Por quê?**
        - Comportamentos variados
        - Múltiplas dimensões relevantes
        - Padrões de fraude complexos
        """)

# Footer
criar_divider()
st.markdown("""
<div style='text-align: center; color: #666; padding: 1rem 0;'>
    <p>🔍 Detector de Anomalias | Powered by Machine Learning</p>
</div>
""", unsafe_allow_html=True)