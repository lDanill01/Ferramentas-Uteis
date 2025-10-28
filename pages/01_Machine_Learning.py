import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import warnings
import re
warnings.filterwarnings('ignore')

# Bibliotecas para Machine Learning
from sklearn.model_selection import train_test_split, GridSearchCV, TimeSeriesSplit
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score, mean_absolute_percentage_error
from sklearn.linear_model import LinearRegression, Ridge, Lasso
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
from sklearn.svm import SVR
import xgboost as xgb

# Bibliotecas para visualização
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots

# Importar configurações
import sys
sys.path.append('..')
from config import configurar_pagina, aplicar_estilo_global, criar_header, criar_divider

# Configuração da página
configurar_pagina("Previsão de Demanda", "📈")
aplicar_estilo_global()

# Estilos adicionais específicos desta página
st.markdown("""
    <style>
    .upload-section {
        padding: 2rem;
        border-radius: 12px;
        margin-bottom: 2rem;
    }
    .metric-card {
        background-color: #f8f9fa;
        padding: 1.5rem;
        border-radius: 10px;
        margin: 10px 0;
    }
    .feature-importance {
        padding: 15px;
        border-radius: 10px;
        margin: 10px 0;
    }
    .info-badge {
        display: inline-block;
        color: white;
        padding: 0.3rem 0.8rem;
        border-radius: 20px;
        font-size: 0.85rem;
        margin: 0.2rem;
        font-weight: 500;
    }
    </style>
""", unsafe_allow_html=True)

# Funções auxiliares
def convert_brazilian_number(value):
    if pd.isna(value):
        return np.nan
    
    if isinstance(value, (int, float)):
        return float(value)
    
    value = str(value).strip()
    value = value.replace('.', '').replace(',', '.')
    
    try:
        return float(value)
    except:
        return np.nan

# Classe DemandForecaster
class DemandForecasterStreamlit:    
    def __init__(self):
        self.data = None
        self.date_column = None
        self.target_column = None
        self.models = {}
        self.best_model = None
        self.scaler = StandardScaler()
        self.feature_importance = None
        self.processed_data = None
        self.X_train = None
        self.X_val = None
        self.X_test = None
        self.y_train = None
        self.y_val = None
        self.y_test = None
        self.dates_test = None
        self.results = None
        self.best_model_name = None
    
    def read_data_flexible(self, uploaded_file, file_type):
        df = None
        
        try:
            if file_type == "CSV":
                separators = [',', ';', '\\t', '|']
                encodings = ['utf-8', 'latin1', 'iso-8859-1', 'cp1252']
                
                for encoding in encodings:
                    for sep in separators:
                        try:
                            uploaded_file.seek(0)
                            df = pd.read_csv(uploaded_file, sep=sep, encoding=encoding)
                            if len(df.columns) > 1:
                                st.success(f"✅ Arquivo lido com sucesso! (Separador: '{sep}', Encoding: {encoding})")
                                break
                        except:
                            continue
                    if df is not None and len(df.columns) > 1:
                        break
                
                if df is None or len(df.columns) <= 1:
                    uploaded_file.seek(0)
                    df = pd.read_csv(uploaded_file, encoding='utf-8', sep=None, engine='python')
            else:
                df = pd.read_excel(uploaded_file, sheet_name=0)
            
            return df
            
        except Exception as e:
            st.error(f"❌ Erro ao ler arquivo: {str(e)}")
            return None
    
    def detect_columns(self, df):
        date_cols = []
        numeric_cols = []
        
        for col in df.columns:
            if df[col].dtype == 'object':
                try:
                    pd.to_datetime(df[col])
                    date_cols.append(col)
                except:
                    pass
            elif pd.api.types.is_numeric_dtype(df[col]):
                numeric_cols.append(col)
        
        return date_cols, numeric_cols
    
    def validate_data(self, df, date_col, target_col):
        issues = []
        
        null_dates = df[date_col].isnull().sum()
        null_targets = df[target_col].isnull().sum()
        
        if null_dates > 0:
            issues.append(f"⚠️ {null_dates} valores nulos na coluna de data")
        if null_targets > 0:
            issues.append(f"⚠️ {null_targets} valores nulos na coluna de valores")
        
        if (df[target_col] < 0).any():
            issues.append(f"⚠️ Valores negativos detectados na coluna de demanda")
        
        duplicates = df[date_col].duplicated().sum()
        if duplicates > 0:
            issues.append(f"⚠️ {duplicates} datas duplicadas encontradas")
        
        return issues
    
    def create_features(self, df):
        df = df.copy()
        df = df.sort_values(self.date_column)
        
        # Features temporais
        df['ano'] = df[self.date_column].dt.year
        df['mes'] = df[self.date_column].dt.month
        df['dia'] = df[self.date_column].dt.day
        df['dia_semana'] = df[self.date_column].dt.dayofweek
        df['dia_ano'] = df[self.date_column].dt.dayofyear
        df['trimestre'] = df[self.date_column].dt.quarter
        df['semana_mes'] = df[self.date_column].dt.day // 7 + 1
        df['fim_semana'] = (df['dia_semana'] >= 5).astype(int)
        
        # Features trigonométricas
        df['mes_sin'] = np.sin(2 * np.pi * df['mes'] / 12)
        df['mes_cos'] = np.cos(2 * np.pi * df['mes'] / 12)
        df['dia_semana_sin'] = np.sin(2 * np.pi * df['dia_semana'] / 7)
        df['dia_semana_cos'] = np.cos(2 * np.pi * df['dia_semana'] / 7)
        
        # Features de lag
        lag_features = [1, 2, 3, 6, 12]
        for lag in lag_features:
            df[f'lag_{lag}'] = df[self.target_column].shift(lag)
        
        # Médias móveis
        rolling_features = [3, 6, 12]
        for window in rolling_features:
            df[f'media_movel_{window}'] = df[self.target_column].rolling(window=window, min_periods=1).mean()
            df[f'std_movel_{window}'] = df[self.target_column].rolling(window=window, min_periods=1).std()
            df[f'min_movel_{window}'] = df[self.target_column].rolling(window=window, min_periods=1).min()
            df[f'max_movel_{window}'] = df[self.target_column].rolling(window=window, min_periods=1).max()
        
        # Features de tendência
        df['tendencia_3m'] = df[self.target_column].rolling(window=3).mean() - df[self.target_column].rolling(window=6).mean()
        df['variacao_percentual'] = df[self.target_column].pct_change()
        
        # Features de crescimento
        df['crescimento_mensal'] = (df[self.target_column] - df[self.target_column].shift(1)) / df[self.target_column].shift(1)
        df['crescimento_anual'] = (df[self.target_column] - df[self.target_column].shift(12)) / df[self.target_column].shift(12)
        
        df = df.replace([np.inf, -np.inf], np.nan)
        df = df.dropna()
        
        return df

# Inicializar estado da sessão
if 'forecaster' not in st.session_state:
    st.session_state.forecaster = DemandForecasterStreamlit()
if 'data_loaded' not in st.session_state:
    st.session_state.data_loaded = False
if 'models_trained' not in st.session_state:
    st.session_state.models_trained = False
if 'columns_configured' not in st.session_state:
    st.session_state.columns_configured = False

# Cabeçalho da página
criar_header("📈 Previsão de Demanda com Machine Learning avançado")

st.markdown('<div class="upload-section">', unsafe_allow_html=True)
st.markdown("### 📤 Upload de Dados")

# AJUSTE 2: Layout em 3 colunas
col1, col2, col3 = st.columns([1.5, 0.75, 0.4])

with col2:
        file_type = st.selectbox(
        "**📁 Tipo de arquivo:**",
        ["CSV", "XLSX"],
        help="Formato do arquivo a ser carregado"
    )

with col1:    
    uploaded_file = st.file_uploader(
    "**Escolha seu arquivo**",
    type=[file_type.lower()],
    help="Faça upload do arquivo com dados históricos de demanda"
    )

with col3:
    usar_exemplo = st.button("🎲 Usar Exemplo", use_container_width=True, type='primary')

st.markdown('</div>', unsafe_allow_html=True)
st.divider()

# Processar upload ou exemplo
if usar_exemplo:
    np.random.seed(42)
    dates = pd.date_range(start='2020-01-01', periods=48, freq='MS')
    trend = np.linspace(40000, 60000, 48)
    seasonal = 5000 * np.sin(2 * np.pi * np.arange(48) / 12)
    noise = np.random.normal(0, 2000, 48)
    demand = trend + seasonal + noise
    
    df = pd.DataFrame({
        'data': dates,
        'demanda': np.maximum(demand, 0)
    })
    
    st.session_state.data = df
    st.session_state.data_loaded = True
    st.session_state.date_col_selected = 'data'
    st.session_state.target_col_selected = 'demanda'
    st.session_state.columns_configured = True
    
    st.session_state.forecaster.date_column = 'data'
    st.session_state.forecaster.target_column = 'demanda'
    st.session_state.forecaster.data = df
    
    st.success("✅ Dados de exemplo gerados! (48 meses)")
    st.rerun()

if uploaded_file is not None and not st.session_state.data_loaded:
    try:
        df = st.session_state.forecaster.read_data_flexible(uploaded_file, file_type)
        
        if df is not None:
            st.write(f"📊 Dados carregados: {len(df)} registros, {len(df.columns)} colunas")
            st.session_state.data = df
            st.session_state.data_loaded = True
            st.rerun()
        
    except Exception as e:
        st.error(f"❌ Erro ao carregar arquivo: {str(e)}")

criar_divider()

if st.session_state.data_loaded:
    df = st.session_state.data
    
    tabs = st.tabs([
        "📊 Análise de Dados",
        "⚙️ Configuração & Validação",
        "🤖 Treinamento de Modelos",
        "📈 Resultados & Métricas",
        "🔮 Previsões Futuras",
        "📚 Documentação"
    ])
    
    # TAB 1: ANÁLISE DE DADOS
    with tabs[0]:
        st.header("📊 Análise Exploratória dos Dados")
        
        col1, col2 = st.columns([2,2.5])
        
        with col1:
            st.subheader("Dataset")
            st.dataframe(df.head(10), use_container_width=True)
        
        with col2:
            st.subheader("📈 Estatísticas Descritivas")
            st.dataframe(df.describe(), use_container_width=True)

        
        # Visualização da série temporal
        if st.session_state.columns_configured:
            st.subheader("📊 Série Temporal - Dataset")
            
            fig = go.Figure()
            fig.add_trace(go.Scatter(
                x=df[st.session_state.date_col_selected],
                y=df[st.session_state.target_col_selected],
                mode='lines+markers',
                name='Demanda',
                line=dict(color='#667eea', width=2),
                marker=dict(size=6)
            ))
            
            fig.update_layout(
                xaxis_title="Data",
                yaxis_title="Demanda",
                height=420,
                hovermode='x unified',
                margin=dict(l=40, r=40, t=60, b=40)
            )
            
            st.plotly_chart(fig, use_container_width=True)
            criar_divider()
    
    # TAB 2: CONFIGURAÇÃO
    with tabs[1]:
        st.header("⚙️ Configuração e Validação")
        
        if not st.session_state.columns_configured:
            st.info("🔧 Configure as colunas de Data e Valor")
            
            date_cols, numeric_cols = st.session_state.forecaster.detect_columns(df)
            
            col1, col2 = st.columns(2, gap="large")
            
            with col1:
                st.subheader("Coluna de Data")
                if date_cols:
                    st.info(f"📅 Colunas de data detectadas: {', '.join(date_cols)}")
                    date_col = st.selectbox("Selecione a coluna de data:", date_cols)
                else:
                    date_col = st.selectbox("Selecione a coluna de data:", df.columns)
                
                st.session_state.date_col_selected = date_col
                
            with col2:
                st.subheader("Coluna de Valores (Demanda)")
                if numeric_cols:
                    st.info(f"🔢 Colunas numéricas detectadas: {', '.join(numeric_cols)}")
                    target_col = st.selectbox("Selecione a coluna de valores:", numeric_cols)
                else:
                    target_col = st.selectbox("Selecione a coluna de valores:", df.columns)
                
                st.session_state.target_col_selected = target_col
            
            if st.button("✅ Confirmar Configuração", type="primary"):
                try:
                    df[date_col] = pd.to_datetime(df[date_col])
                    
                    st.session_state.forecaster.date_column = date_col
                    st.session_state.forecaster.target_column = target_col
                    st.session_state.forecaster.data = df
                    st.session_state.columns_configured = True
                    
                    st.success("✅ Configuração salva com sucesso!")
                    st.rerun()
                    
                except Exception as e:
                    st.error(f"❌ Erro na configuração: {str(e)}")
        
        else:
            st.success(f"""
            ✅ **Configuração Detectada:**
            - Coluna de Data: `{st.session_state.date_col_selected}`
            - Coluna de Demanda: `{st.session_state.target_col_selected}`
            """)
            
            if st.button("✅ Validar Configuração", type='primary'):
                try:
                    issues = st.session_state.forecaster.validate_data(
                        df, 
                        st.session_state.date_col_selected, 
                        st.session_state.date_col_selected and st.session_state.target_col_selected and st.session_state.forecaster.target_column or st.session_state.date_col_selected
                    )
                    
                    # Use the actual target column in the standard case
                    issues = st.session_state.forecaster.validate_data(
                        df, 
                        st.session_state.date_col_selected, 
                        st.session_state.target_col_selected
                    )
                    
                    if issues:
                        st.warning("Problemas encontrados nos dados:")
                        for issue in issues:
                            st.write(issue)
                    else:
                        st.success("✅ Dados validados com sucesso!")
                    
                    st.subheader("📊 Análise de Sazonalidade")
                    
                    col1, col2 = st.columns(2, gap="large")
                    
                    with col1:
                        df_temp = df.copy()
                        df_temp['mes'] = pd.to_datetime(df_temp[st.session_state.date_col_selected]).dt.month
                        
                        fig_box = px.box(df_temp, x='mes', y=st.session_state.target_col_selected,
                                        title="Distribuição por Mês")
                        st.plotly_chart(fig_box, use_container_width=True)
                    
                    with col2:
                        media_mensal = df_temp.groupby('mes')[st.session_state.target_col_selected].mean().reset_index()
                        
                        fig_media = px.line(media_mensal, x='mes', y=st.session_state.target_col_selected,
                                          title="Média por Mês",
                                          markers=True)
                        st.plotly_chart(fig_media, use_container_width=True)
                    
                    st.subheader("📈 Análise de Tendência")
                    
                    df_temp = df.copy()
                    df_temp = df_temp.set_index(st.session_state.date_col_selected)
                    df_temp['media_movel_3'] = df_temp[st.session_state.target_col_selected].rolling(window=3).mean()
                    df_temp['media_movel_6'] = df_temp[st.session_state.target_col_selected].rolling(window=6).mean()
                    
                    fig_trend = go.Figure()
                    fig_trend.add_trace(go.Scatter(
                        x=df_temp.index, y=df_temp[st.session_state.target_col_selected],
                        mode='lines+markers', name='Demanda Real',
                        line=dict(color='#667eea', width=1), opacity=0.7
                    ))
                    fig_trend.add_trace(go.Scatter(
                        x=df_temp.index, y=df_temp['media_movel_3'],
                        mode='lines', name='Média Móvel 3 Meses',
                        line=dict(color='#ff7f0e', width=2)
                    ))
                    fig_trend.add_trace(go.Scatter(
                        x=df_temp.index, y=df_temp['media_movel_6'],
                        mode='lines', name='Média Móvel 6 Meses',
                        line=dict(color='#2ca02c', width=2)
                    ))
                    
                    fig_trend.update_layout(
                        title="Tendência com Médias Móveis",
                        xaxis_title="Data", yaxis_title="Demanda", height=420
                    )
                    
                    st.plotly_chart(fig_trend, use_container_width=True)
                    criar_divider()
                    
                except Exception as e:
                    st.error(f"❌ Erro na validação: {str(e)}")
    
    # TAB 3: TREINAMENTO
    with tabs[2]:
        st.header("🤖 Treinamento dos Modelos")
        
        # AJUSTE 3: Verificar se as colunas foram configuradas
        if st.session_state.columns_configured and st.session_state.forecaster.date_column and st.session_state.forecaster.target_column:
            
            st.markdown("### ⚙️ Configurações de Treinamento")
            
            col1, col2, col3 = st.columns(3, gap="large")
            
            with col1:
                test_size = st.slider(
                    "Tamanho do conjunto de teste (%)",
                    10, 40, 20,
                    help="Percentual de dados para teste final"
                ) / 100
            
            with col2:
                val_size = st.slider(
                    "Tamanho do conjunto de validação (%)",
                    5, 20, 10,
                    help="Percentual de dados para validação"
                ) / 100
            
            with col3:
                st.metric("Tamanho do treino (%)", f"{int((1-test_size-val_size)*100)}%")
            
            criar_divider()
            
            st.markdown("### 🎯 Seleção de Modelos")
            
            col1, col2, col3 = st.columns(3, gap="large")
            
            with col1:
                use_linear = st.checkbox("Linear Regression", value=True)
                use_ridge = st.checkbox("Ridge Regression", value=True)
            
            with col2:
                use_lasso = st.checkbox("Lasso Regression", value=True)
                use_rf = st.checkbox("Random Forest", value=True)
            
            with col3:
                use_gb = st.checkbox("Gradient Boosting", value=True)
                use_xgb = st.checkbox("XGBoost", value=True)
            
            criar_divider()
            
            if st.button("🚀 Iniciar Treinamento", type="primary", use_container_width=True):
                with st.spinner("Processando dados e treinando modelos..."):
                    try:
                        st.info("📊 Criando features...")
                        processed_df = st.session_state.forecaster.create_features(st.session_state.forecaster.data)
                        st.session_state.forecaster.processed_data = processed_df
                        
                        st.info("✂️ Dividindo dados...")
                        feature_columns = [col for col in processed_df.columns 
                                        if col not in [st.session_state.forecaster.date_column, 
                                                    st.session_state.forecaster.target_column]]
                        
                        X = processed_df[feature_columns]
                        y = processed_df[st.session_state.forecaster.target_column]
                        dates = processed_df[st.session_state.forecaster.date_column]
                        
                        n_samples = len(X)
                        train_size = int(n_samples * (1 - test_size - val_size))
                        val_size_n = int(n_samples * val_size)
                        
                        X_train = X[:train_size]
                        X_val = X[train_size:train_size + val_size_n]
                        X_test = X[train_size + val_size_n:]
                        
                        y_train = y[:train_size]
                        y_val = y[train_size:train_size + val_size_n]
                        y_test = y[train_size + val_size_n:]
                        
                        dates_test = dates[train_size + val_size_n:]
                        
                        scaler = StandardScaler()
                        X_train_scaled = scaler.fit_transform(X_train)
                        X_val_scaled = scaler.transform(X_val)
                        X_test_scaled = scaler.transform(X_test)
                        
                        st.session_state.forecaster.X_train = X_train
                        st.session_state.forecaster.X_val = X_val
                        st.session_state.forecaster.X_test = X_test
                        st.session_state.forecaster.y_train = y_train
                        st.session_state.forecaster.y_val = y_val
                        st.session_state.forecaster.y_test = y_test
                        st.session_state.forecaster.dates_test = dates_test
                        st.session_state.forecaster.scaler = scaler
                        
                        st.info("🤖 Treinando modelos...")
                        
                        models_to_train = {}
                        if use_linear:
                            models_to_train['Linear Regression'] = LinearRegression()
                        if use_ridge:
                            models_to_train['Ridge Regression'] = Ridge(alpha=1.0)
                        if use_lasso:
                            models_to_train['Lasso Regression'] = Lasso(alpha=1.0)
                        if use_rf:
                            models_to_train['Random Forest'] = RandomForestRegressor(n_estimators=100, random_state=42)
                        if use_gb:
                            models_to_train['Gradient Boosting'] = GradientBoostingRegressor(n_estimators=100, random_state=42)
                        if use_xgb:
                            models_to_train['XGBoost'] = xgb.XGBRegressor(n_estimators=100, random_state=42, verbosity=0)
                        
                        results = {}
                        progress_bar = st.progress(0)
                        status_text = st.empty()
                        
                        for i, (name, model) in enumerate(models_to_train.items()):
                            progress_bar.progress((i + 1) / len(models_to_train))
                            status_text.text(f'🔄 Treinando modelo: {name}')
                            
                            model.fit(X_train, y_train)
                            y_pred_val = model.predict(X_val)
                            y_pred_test = model.predict(X_test)
                            
                            mae = mean_absolute_error(y_val, y_pred_val)
                            rmse = np.sqrt(mean_squared_error(y_val, y_pred_val))
                            mape = mean_absolute_percentage_error(y_val, y_pred_val) * 100
                            r2 = r2_score(y_val, y_pred_val)
                            
                            results[name] = {
                                'model': model,
                                'mae': mae,
                                'rmse': rmse,
                                'mape': mape,
                                'r2': r2,
                                'predictions_val': y_pred_val,
                                'predictions_test': y_pred_test
                            }
                            
                            st.session_state.forecaster.models[name] = model

                        status_text.text('✅ Todos os modelos foram treinados!')

                        best_model_name = min(results.keys(), key=lambda x: results[x]['mape'])
                        st.session_state.forecaster.best_model = results[best_model_name]['model']
                        st.session_state.forecaster.best_model_name = best_model_name
                        st.session_state.forecaster.results = results
                        
                        if hasattr(st.session_state.forecaster.best_model, 'feature_importances_'):
                            importance = st.session_state.forecaster.best_model.feature_importances_
                            feature_names = X_train.columns
                            
                            importance_df = pd.DataFrame({
                                'feature': feature_names,
                                'importance': importance
                            }).sort_values('importance', ascending=False)
                            
                            st.session_state.forecaster.feature_importance = importance_df
                        
                        st.session_state.models_trained = True
                        st.success(f"✅ Treinamento concluído! Melhor modelo: {best_model_name} (MAPE: {results[best_model_name]['mape']:.2f}%)")
                        
                        st.subheader("📊 Estatísticas do Conjunto Processado")
                        col1, col2, col3, col4 = st.columns(4, gap="large")
                        
                        with col1:
                            st.metric("Total de Amostras", len(processed_df))
                        with col2:
                            st.metric("Features Criadas", len(feature_columns))
                        with col3:
                            st.metric("Amostras Treino", len(X_train))
                        with col4:
                            st.metric("Amostras Teste", len(X_test))
                            
                    except Exception as e:
                        st.error(f"❌ Erro no treinamento: {str(e)}")
                        import traceback
                        st.code(traceback.format_exc())
                    
                    finally:
                        progress_bar.empty()
                        status_text.empty()
        else:
            st.warning("⚠️ Configure as colunas na aba 'Configuração & Validação' primeiro")
    
    # TAB 4: RESULTADOS
    with tabs[3]:
        st.header("📈 Resultados e Métricas")
        
        if st.session_state.models_trained:
            results = st.session_state.forecaster.results
            
            st.markdown("### 🏆 Performance dos Modelos")
            
            results_df = pd.DataFrame({
                'Modelo': results.keys(),
                'MAE': [results[m]['mae'] for m in results.keys()],
                'RMSE': [results[m]['rmse'] for m in results.keys()],
                'MAPE (%)': [results[m]['mape'] for m in results.keys()],
                'R²': [results[m]['r2'] for m in results.keys()]
            }).sort_values('MAPE (%)')

            st.dataframe(
                results_df.style.highlight_min(subset=['MAE', 'RMSE', 'MAPE (%)'])
                    .highlight_max(subset=['R²']),
                use_container_width=True
            )
            
            criar_divider()

            col1, col2 = st.columns(2, gap="large")
            with col1:
                st.markdown("### 🕸️ Comparativo Geral dos Modelos (Radar Chart)")
                radar_df = results_df.copy()
                radar_df.set_index('Modelo', inplace=True)
                radar_df_norm = (radar_df - radar_df.min()) / (radar_df.max() - radar_df.min())
                radar_df_norm = radar_df_norm.reset_index()

                fig_radar = go.Figure()
                for _, row in radar_df_norm.iterrows():
                    fig_radar.add_trace(go.Scatterpolar(
                        r=row[['MAE', 'RMSE', 'MAPE (%)', 'R²']],
                        theta=['MAE', 'RMSE', 'MAPE (%)', 'R²'],
                        fill='toself',
                        name=row['Modelo']
                    ))

                fig_radar.update_layout(
                    polar=dict(radialaxis=dict(visible=True, range=[0, 1])),
                    showlegend=True,
                    height=500,
                    title="Radar Chart - Comparativo entre Modelos"
                )
                st.plotly_chart(fig_radar, use_container_width=True)

            with col2:
                st.markdown("### 📉 Distribuição dos Erros por Modelo")
                error_data = []
                for m, res in results.items():
                    erros = st.session_state.forecaster.y_val.values - res['predictions_val']
                    error_data.extend(zip([m]*len(erros), erros))
                error_df = pd.DataFrame(error_data, columns=['Modelo', 'Erro'])
                fig_box = px.box(error_df, x='Modelo', y='Erro', color='Modelo', title="Distribuição dos Erros (Validação)")
                st.plotly_chart(fig_box, use_container_width=True)
            criar_divider()
            
            col1, col2 = st.columns(2, gap="large")
            
            with col1:
                fig_comparison = go.Figure()
                fig_comparison.add_trace(go.Bar(
                    x=results_df['Modelo'],
                    y=results_df['MAPE (%)'],
                    text=results_df['MAPE (%)'].round(2),
                    textposition='auto',
                    marker_color=['#28a745' if m == st.session_state.forecaster.best_model_name else '#667eea' 
                                for m in results_df['Modelo']]
                ))
                fig_comparison.update_layout(
                    title="Comparação de MAPE entre Modelos",
                    xaxis_title="Modelo",
                    yaxis_title="MAPE (%)",
                    height=420
                )
                st.plotly_chart(fig_comparison, use_container_width=True)
            
            with col2:
                fig_r2 = go.Figure()
                fig_r2.add_trace(go.Bar(
                    x=results_df['Modelo'],
                    y=results_df['R²'],
                    text=results_df['R²'].round(3),
                    textposition='auto',
                    marker_color=['#28a745' if m == st.session_state.forecaster.best_model_name else '#667eea' 
                                for m in results_df['Modelo']]
                ))
                fig_r2.update_layout(
                    title="Comparação de R² entre Modelos",
                    xaxis_title="Modelo",
                    yaxis_title="R²",
                    height=420
                )
                st.plotly_chart(fig_r2, use_container_width=True)
                        
            st.markdown("### 📊 Previsões vs Valores Reais")
            selected_model = st.selectbox("Selecione o modelo:", list(results.keys()))

            fig_predictions = go.Figure()
            fig_predictions.add_trace(go.Scatter(
                x=st.session_state.forecaster.dates_test,
                y=st.session_state.forecaster.y_test,
                mode='lines+markers',
                name='Real',
                line=dict(color="#66eae8", width=2),
                marker=dict(size=8)
            ))
            fig_predictions.add_trace(go.Scatter(
                x=st.session_state.forecaster.dates_test,
                y=results[selected_model]['predictions_test'],
                mode='lines+markers',
                name=f'Previsto ({selected_model})',
                line=dict(color='#ff7f0e', width=2, dash='dash'),
                marker=dict(size=8)
            ))
            fig_predictions.update_layout(
                title=f"Previsões vs Valores Reais - {selected_model}",
                xaxis_title="Data",
                yaxis_title="Demanda",
                height=500,
                hovermode='x unified'
            )
            st.plotly_chart(fig_predictions, use_container_width=True)

            if st.session_state.forecaster.feature_importance is not None:
                criar_divider()
                st.markdown("### 🔍 Importância das Features")
                top_n = st.slider("Número de features a exibir:", 5, 20, 10)
                top_features = st.session_state.forecaster.feature_importance.head(top_n)
                fig_importance = go.Figure()
                fig_importance.add_trace(go.Bar(
                    y=top_features['feature'][::-1],
                    x=top_features['importance'][::-1],
                    orientation='h',
                    marker_color='#667eea'
                ))
                fig_importance.update_layout(
                    title=f"Top {top_n} Features Mais Importantes",
                    xaxis_title="Importância",
                    yaxis_title="Feature",
                    height=420
                )
                st.plotly_chart(fig_importance, use_container_width=True)

        else:
            st.info("📊 Treine os modelos na aba 'Treinamento de Modelos' para visualizar os resultados")
    
    # TAB 5: PREVISÕES
    with tabs[4]:
        st.header("🔮 Previsões Futuras")
        
        if st.session_state.models_trained:
            st.markdown("### ⚙️ Configurações de Previsão")
            
            col1, col2 = st.columns([2,7], gap="large")
            
            with col1:
                periodo_previsao = st.number_input(
                    "Número de meses para prever:",
                    min_value=1,
                    max_value=24,
                    value=6,
                    help="Quantos meses você deseja prever"
                )

            with col2:
                modelo_previsao = st.selectbox(
                    "Modelo para previsão:",
                    list(st.session_state.forecaster.models.keys())
                )
            
            if st.button("🔮 Gerar Previsões", type="primary", use_container_width=True):
                with st.spinner("Gerando previsões..."):
                    try:
                        model = st.session_state.forecaster.models[modelo_previsao]
                        last_date = st.session_state.forecaster.processed_data[st.session_state.forecaster.date_column].max()
                        
                        future_dates = pd.date_range(
                            start=last_date + pd.DateOffset(months=1),
                            periods=periodo_previsao,
                            freq='MS'
                        )
                        
                        last_row = st.session_state.forecaster.processed_data.iloc[-1:].copy()
                        future_predictions = []
                        
                        for i in range(periodo_previsao):
                            current_date = future_dates[i]
                            last_row['ano'] = current_date.year
                            last_row['mes'] = current_date.month
                            last_row['dia'] = current_date.day
                            last_row['dia_semana'] = current_date.dayofweek
                            last_row['dia_ano'] = current_date.dayofyear
                            last_row['trimestre'] = current_date.quarter
                            last_row['semana_mes'] = current_date.day // 7 + 1
                            last_row['fim_semana'] = int(current_date.dayofweek >= 5)
                            
                            last_row['mes_sin'] = np.sin(2 * np.pi * current_date.month / 12)
                            last_row['mes_cos'] = np.cos(2 * np.pi * current_date.month / 12)
                            last_row['dia_semana_sin'] = np.sin(2 * np.pi * current_date.dayofweek / 7)
                            last_row['dia_semana_cos'] = np.cos(2 * np.pi * current_date.dayofweek / 7)
                            
                            for lag in [1, 2, 3, 6, 12]:
                                if i < lag:
                                    idx = len(st.session_state.forecaster.processed_data) - lag + i
                                    if idx >= 0:
                                        last_row[f'lag_{lag}'] = st.session_state.forecaster.processed_data[
                                            st.session_state.forecaster.target_column].iloc[idx]
                                else:
                                    last_row[f'lag_{lag}'] = future_predictions[i - lag]
                            
                            X_future = last_row.drop(columns=[st.session_state.forecaster.date_column, 
                                                             st.session_state.forecaster.target_column])
                            
                            pred = model.predict(X_future)[0]
                            future_predictions.append(max(pred, 0))
                        
                        future_df = pd.DataFrame({
                            'data': future_dates,
                            'previsao': future_predictions
                        })
                        
                        std_error = np.std(st.session_state.forecaster.y_test.values - 
                                         st.session_state.forecaster.results[modelo_previsao]['predictions_test'])
                        
                        future_df['limite_inferior'] = np.maximum(future_df['previsao'] - 1.96 * std_error, 0)
                        future_df['limite_superior'] = future_df['previsao'] + 1.96 * std_error
                        
                        ultimo_real = st.session_state.forecaster.processed_data[st.session_state.forecaster.target_column].iloc[-1]
                        media_prev = future_df['previsao'].mean()
                        crescimento_pct = ((media_prev - ultimo_real) / ultimo_real) * 100 if ultimo_real != 0 else np.nan
                        
                        taxa_erro = st.session_state.forecaster.results[modelo_previsao]['mape']
                        conf_interval = 95
                        std_prev = future_df['previsao'].std()
                        max_prev = future_df['previsao'].max()
                        min_prev = future_df['previsao'].min()
                        
                        cor_badge = "#2881a7" if (not np.isnan(crescimento_pct) and crescimento_pct > 0) else "#dc3545"
                        icone = "📈" if (not np.isnan(crescimento_pct) and crescimento_pct > 0) else "📉"

                        col1, col2 = st.columns(2)

                        with col2:
                            st.markdown("### 📋 Tabela de Previsões")
                            
                            display_df = future_df.copy()
                            display_df['data'] = display_df['data'].dt.strftime('%m/%Y')
                            display_df['previsao'] = display_df['previsao'].round(2)
                            display_df['limite_inferior'] = display_df['limite_inferior'].round(2)
                            display_df['limite_superior'] = display_df['limite_superior'].round(2)
                            display_df.columns = ['Data', 'Previsão', 'Limite Inferior (95%)', 'Limite Superior (95%)']
                            
                            st.dataframe(display_df, use_container_width=True)

                        with col1:
                            st.markdown(f"""
                            <div style="
                                background-color:{cor_badge};
                                color:white;
                                padding:1rem;
                                border-radius:12px;
                                text-align:left;
                                font-size:1rem;
                                margin-bottom:1.5rem;">
                                <b>{icone} Previsão Resumida ({modelo_previsao})</b><br>
                                Crescimento Previsto: <b>{crescimento_pct:.2f}%</b><br>
                                Volume Médio Previsto: <b>{media_prev:,.2f}</b><br>
                                Desvio Padrão: <b>{std_prev:,.2f}</b><br>
                                Intervalo [Min, Max]: <b>{min_prev:,.2f} — {max_prev:,.2f}</b><br>
                                Confiança: <b>{conf_interval}%</b> | Taxa de Erro: <b>{taxa_erro:.2f}%</b>
                            </div>
                            """, unsafe_allow_html=True)
                            
                            st.markdown("<div style='margin-top: 10px;'></div>", unsafe_allow_html=True)
                            
                            csv = display_df.to_csv(index=False)
                            st.download_button(
                                label="📥 Download Previsões (CSV)",
                                data=csv,
                                file_name=f'previsoes_{datetime.now().strftime("%Y%m%d_%H%M%S")}.csv',
                                mime='text/csv',
                                use_container_width=True,
                                type='primary'
                            )


                        st.markdown("### 📈 Visualização das Previsões")
                        
                        fig_future = go.Figure()
                        
                        fig_future.add_trace(go.Scatter(
                            x=st.session_state.forecaster.processed_data[st.session_state.forecaster.date_column],
                            y=st.session_state.forecaster.processed_data[st.session_state.forecaster.target_column],
                            mode='lines+markers',
                            name='Histórico',
                            line=dict(color='#667eea', width=2),
                            marker=dict(size=6)
                        ))
                        
                        fig_future.add_trace(go.Scatter(
                            x=future_df['data'],
                            y=future_df['previsao'],
                            mode='lines+markers',
                            name='Previsão',
                            line=dict(color='#ff7f0e', width=2, dash='dash'),
                            marker=dict(size=8)
                        ))
                        
                        fig_future.add_trace(go.Scatter(
                            x=future_df['data'],
                            y=future_df['limite_superior'],
                            fill=None,
                            mode='lines',
                            line_color='rgba(0,0,0,0)',
                            showlegend=False
                        ))
                        
                        fig_future.add_trace(go.Scatter(
                            x=future_df['data'],
                            y=future_df['limite_inferior'],
                            fill='tonexty',
                            mode='lines',
                            line_color='rgba(0,0,0,0)',
                            name='Intervalo de Confiança 95%',
                            fillcolor='rgba(255, 127, 14, 0.2)'
                        ))
                        
                        fig_future.update_layout(
                            title=f"Previsões para os Próximos {periodo_previsao} Meses",
                            xaxis_title="Data",
                            yaxis_title="Demanda",
                            height=500,
                            hovermode='x unified'
                        )
                        
                        st.plotly_chart(fig_future, use_container_width=True)
                                                
                    except Exception as e:
                        st.error(f"❌ Erro ao gerar previsões: {str(e)}")
                        import traceback
                        st.code(traceback.format_exc())
        else:
            st.info("🤖 Treine os modelos primeiro para gerar previsões")
    
    # TAB 6: DOCUMENTAÇÃO
    with tabs[5]:
        st.header("📚 Documentação e Ajuda")
        
        st.markdown("""
        ## 📖 Guia Completo do Sistema
        
        ### 🎯 Formato de Dados Suportado
        
        **Formato Data | Valor:**
        ```
        Data       | Valor
        2022-01-01 | 47764.00
        2022-02-01 | 49651.43
        2022-03-01 | 59543.25
        ```
        
        ### 🔢 Métricas de Avaliação
        
        | Métrica | O que significa | Valor ideal |
        |---------|----------------|-------------|
        | **MAE** | Erro médio absoluto | Quanto menor, melhor |
        | **RMSE** | Erro quadrático médio | Quanto menor, melhor |
        | **MAPE** | Erro percentual | < 10% = Excelente |
        | **R²** | Variância explicada | Próximo a 1 = Ótimo |
        
        ### 💡 Dicas para Melhores Resultados
        
        #### 1. Qualidade dos Dados
        - ✅ Mínimo de 24 meses de histórico
        - ✅ Dados mensais consistentes
        - ✅ Sem outliers extremos
        
        #### 2. Escolha do Modelo
        - **Sazonalidade forte**: Random Forest ou XGBoost
        - **Tendências lineares**: Linear ou Ridge
        - **Dados complexos**: Gradient Boosting
        
        ### 🚀 Passo a Passo
        
        1. **Upload** → Faça upload do arquivo
        2. **Configuração** → Selecione as colunas de Data e Valor
        3. **Validação** → Verifique os dados
        4. **Treinamento** → Selecione modelos
        5. **Análise** → Compare resultados
        6. **Previsão** → Gere previsões futuras
        """)


else:
    # Página inicial quando não há dados carregados
    st.info("👆 Por favor, faça upload de um arquivo ou use dados de exemplo acima")
    
    with st.expander("📖 Como usar este sistema", expanded=True):
        st.markdown("""
        ### 🚀 Início Rápido
        
        1. **Upload de Dados**: Faça upload de um arquivo com seu histórico de demanda
        2. **Formato**: O sistema aceita arquivos CSV ou XLSX no formato Data | Valor
        3. **Configuração**: Selecione as colunas de data e valor
        4. **Validação**: Valide os dados carregados
        5. **Treinamento**: Selecione os modelos e clique em treinar
        6. **Análise**: Visualize métricas, gráficos e insights
        7. **Previsão**: Gere previsões para os próximos meses
        
        ### 📊 Formato esperado dos dados
        
        O sistema aceita dados no formato:
        
        | Data       | Demanda  |
        |------------|----------|
        | 2022-01-01 | 47764.00 |
        | 2022-02-01 | 49651.43 |
        | 2022-03-01 | 59543.25 |
        """)

# Footer
criar_divider()
st.markdown("""
<div style='text-align: center; color:white; padding: 1rem 0;'>
    <p>🚀 Sistema de Previsão de Demanda com Machine Learning</p>
</div>
""", unsafe_allow_html=True)
