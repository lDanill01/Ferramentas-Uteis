import streamlit as st
import requests
import pandas as pd
import json
from datetime import datetime, timedelta
import plotly.graph_objects as go
import plotly.express as px
import io

# Importar configurações
import sys
sys.path.append('..')
from config import (
    configurar_pagina, aplicar_estilo_global, criar_header, 
    criar_divider, criar_botao_download_excel, criar_botao_download_csv
)

# Configuração da página
configurar_pagina("Consultor de APIs", "🌐")
aplicar_estilo_global()

# Estilos adicionais
st.markdown("""
    <style>
    .api-card {
        padding: 1.5rem;
        border-radius: 12px;
        margin: 1rem 0;
        box-shadow: 0 4px 15px rgba(0,0,0,0.08);
        transition: all 0.3s ease;
        cursor: pointer;
    }
    
    .api-card:hover {
        transform: translateY(-3px);
        box-shadow: 0 6px 20px rgba(0,0,0,0.12);
    }
    
    .api-card h4 {
        color: white;
        margin-bottom: 0.5rem;
    }
    
    .result-box {
        background: #f8f9fa;
        padding: 1.5rem;
        border-radius: 10px;
        margin: 1rem 0;
        border-left: 4px solid #667eea;
    }
    
    .success-result {
        border-left-color: #28a745;
    }
    
    .error-result {
        border-left-color: #dc3545;
    }
    
    .info-badge {
        display: inline-block;
        background: #667eea;
        color: white;
        padding: 0.3rem 0.8rem;
        border-radius: 20px;
        font-size: 0.85rem;
        margin: 0.2rem;
        font-weight: 500;
    }
    
    .api-status {
        display: inline-block;
        width: 10px;
        height: 10px;
        border-radius: 50%;
        margin-right: 0.5rem;
    }
    
    .status-online {
        background-color: #28a745;
    }
    
    .status-offline {
        background-color: #dc3545;
    }
    </style>
""", unsafe_allow_html=True)

# Cabeçalho
criar_header("🌐 Consultor de APIs Públicas", "Consulte dados públicos de diversas fontes")

# Inicializar session_state
if 'api_selecionada' not in st.session_state:
    st.session_state.api_selecionada = None
if 'historico_consultas' not in st.session_state:
    st.session_state.historico_consultas = []
if 'dados_coletados' not in st.session_state:
    st.session_state.dados_coletados = []

# ========================================
# FUNÇÕES DE CONSULTA
# ========================================

def consultar_cep(cep):
    """Consulta CEP via ViaCEP"""
    try:
        cep_limpo = cep.replace('-', '').replace('.', '').strip()
        
        if len(cep_limpo) != 8:
            return {'erro': 'CEP deve ter 8 dígitos'}
        
        url = f"https://viacep.com.br/ws/{cep_limpo}/json/"
        response = requests.get(url, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            if 'erro' in data:
                return {'erro': 'CEP não encontrado'}
            return data
        else:
            return {'erro': f'Erro na consulta: {response.status_code}'}
    
    except Exception as e:
        return {'erro': str(e)}

def consultar_cnpj(cnpj):
    """Consulta CNPJ via ReceitaWS"""
    try:
        cnpj_limpo = ''.join(filter(str.isdigit, cnpj))
        
        if len(cnpj_limpo) != 14:
            return {'erro': 'CNPJ deve ter 14 dígitos'}
        
        url = f"https://www.receitaws.com.br/v1/cnpj/{cnpj_limpo}"
        response = requests.get(url, timeout=15)
        
        if response.status_code == 200:
            data = response.json()
            if data.get('status') == 'ERROR':
                return {'erro': data.get('message', 'Erro na consulta')}
            return data
        else:
            return {'erro': f'Erro na consulta: {response.status_code}'}
    
    except Exception as e:
        return {'erro': str(e)}

def consultar_cotacao():
    """Consulta cotações de moedas via AwesomeAPI"""
    try:
        url = "https://economia.awesomeapi.com.br/json/last/USD-BRL,EUR-BRL,GBP-BRL,BTC-BRL"
        response = requests.get(url, timeout=10)
        
        if response.status_code == 200:
            return response.json()
        else:
            return {'erro': f'Erro na consulta: {response.status_code}'}
    
    except Exception as e:
        return {'erro': str(e)}

def consultar_cotacao_historico(moeda, dias=30):
    """Consulta histórico de cotações"""
    try:
        url = f"https://economia.awesomeapi.com.br/json/daily/{moeda}-BRL/{dias}"
        response = requests.get(url, timeout=10)
        
        if response.status_code == 200:
            return response.json()
        else:
            return {'erro': f'Erro na consulta: {response.status_code}'}
    
    except Exception as e:
        return {'erro': str(e)}

def consultar_feriados(ano):
    """Consulta feriados nacionais"""
    try:
        url = f"https://brasilapi.com.br/api/feriados/v1/{ano}"
        response = requests.get(url, timeout=10)
        
        if response.status_code == 200:
            return response.json()
        else:
            return {'erro': f'Erro na consulta: {response.status_code}'}
    
    except Exception as e:
        return {'erro': str(e)}

def consultar_bancos():
    """Consulta lista de bancos brasileiros"""
    try:
        url = "https://brasilapi.com.br/api/banks/v1"
        response = requests.get(url, timeout=10)
        
        if response.status_code == 200:
            return response.json()
        else:
            return {'erro': f'Erro na consulta: {response.status_code}'}
    
    except Exception as e:
        return {'erro': str(e)}

def consultar_ibge_estados():
    """Consulta estados brasileiros via IBGE"""
    try:
        url = "https://servicodados.ibge.gov.br/api/v1/localidades/estados"
        response = requests.get(url, timeout=10)
        
        if response.status_code == 200:
            return response.json()
        else:
            return {'erro': f'Erro na consulta: {response.status_code}'}
    
    except Exception as e:
        return {'erro': str(e)}

def consultar_ibge_municipios(uf):
    """Consulta municípios de um estado via IBGE"""
    try:
        url = f"https://servicodados.ibge.gov.br/api/v1/localidades/estados/{uf}/municipios"
        response = requests.get(url, timeout=10)
        
        if response.status_code == 200:
            return response.json()
        else:
            return {'erro': f'Erro na consulta: {response.status_code}'}
    
    except Exception as e:
        return {'erro': str(e)}

# ========================================
# SELEÇÃO DE API
# ========================================

st.markdown("### 🎯 Selecione a API")

col1, col2, col3 = st.columns(3)

with col1:
    if st.button("📍 Consultar CEP", use_container_width=True,
                type="primary" if st.session_state.api_selecionada == "CEP" else "secondary"):
        st.session_state.api_selecionada = "CEP"
        st.rerun()
    
    if st.button("💱 Cotações de Moedas", use_container_width=True,
                type="primary" if st.session_state.api_selecionada == "COTACAO" else "secondary"):
        st.session_state.api_selecionada = "COTACAO"
        st.rerun()

with col2:
    if st.button("🏢 Consultar CNPJ", use_container_width=True,
                type="primary" if st.session_state.api_selecionada == "CNPJ" else "secondary"):
        st.session_state.api_selecionada = "CNPJ"
        st.rerun()
    
    if st.button("📅 Feriados Nacionais", use_container_width=True,
                type="primary" if st.session_state.api_selecionada == "FERIADOS" else "secondary"):
        st.session_state.api_selecionada = "FERIADOS"
        st.rerun()

with col3:
    if st.button("🏦 Lista de Bancos", use_container_width=True,
                type="primary" if st.session_state.api_selecionada == "BANCOS" else "secondary"):
        st.session_state.api_selecionada = "BANCOS"
        st.rerun()
    
    if st.button("🗺️ Dados IBGE", use_container_width=True,
                type="primary" if st.session_state.api_selecionada == "IBGE" else "secondary"):
        st.session_state.api_selecionada = "IBGE"
        st.rerun()

criar_divider()

# ========================================
# CONSULTAS ESPECÍFICAS
# ========================================

if st.session_state.api_selecionada == "CEP":
    st.markdown("### 📍 Consulta de CEP")
    
    st.info("💡 Utilize a API ViaCEP para consultar endereços completos a partir do CEP")
    
    tab1, tab2 = st.tabs(["🔍 Consulta Individual", "📋 Consulta em Lote"])
    
    with tab1:
        col1, col2 = st.columns([3, 1])
        
        with col1:
            cep_input = st.text_input(
                "Digite o CEP",
                placeholder="Ex: 01310-100",
                help="CEP com ou sem formatação"
            )
        
        with col2:
            st.markdown("<br>", unsafe_allow_html=True)
            if st.button("🔍 Consultar", use_container_width=True, type="primary"):
                if cep_input:
                    with st.spinner("Consultando..."):
                        resultado = consultar_cep(cep_input)
                        
                        if 'erro' in resultado:
                            st.error(f"❌ {resultado['erro']}")
                        else:
                            st.success("✅ CEP encontrado!")
                            
                            # Exibir resultado
                            col1, col2 = st.columns(2)
                            
                            with col1:
                                st.markdown("**📍 Endereço:**")
                                st.write(f"**Logradouro:** {resultado.get('logradouro', 'N/A')}")
                                st.write(f"**Bairro:** {resultado.get('bairro', 'N/A')}")
                                st.write(f"**Cidade:** {resultado.get('localidade', 'N/A')}")
                            
                            with col2:
                                st.markdown("**🗺️ Localização:**")
                                st.write(f"**Estado:** {resultado.get('uf', 'N/A')}")
                                st.write(f"**CEP:** {resultado.get('cep', 'N/A')}")
                                st.write(f"**DDD:** {resultado.get('ddd', 'N/A')}")
                            
                            # Adicionar ao histórico
                            st.session_state.historico_consultas.append({
                                'tipo': 'CEP',
                                'consulta': cep_input,
                                'data': datetime.now(),
                                'resultado': resultado
                            })
                            
                            # Adicionar aos dados coletados
                            st.session_state.dados_coletados.append({
                                'CEP': resultado.get('cep', ''),
                                'Logradouro': resultado.get('logradouro', ''),
                                'Bairro': resultado.get('bairro', ''),
                                'Cidade': resultado.get('localidade', ''),
                                'UF': resultado.get('uf', ''),
                                'DDD': resultado.get('ddd', '')
                            })
                else:
                    st.warning("⚠️ Digite um CEP")
    
    with tab2:
        st.markdown("**📋 Consulta em Lote**")
        
        ceps_lote = st.text_area(
            "Digite os CEPs (um por linha)",
            placeholder="01310-100\n01310-200\n01310-300",
            height=150
        )
        
        if st.button("🔍 Consultar Lote", use_container_width=True, type="primary"):
            if ceps_lote:
                ceps = [c.strip() for c in ceps_lote.split('\n') if c.strip()]
                
                if ceps:
                    progress_bar = st.progress(0)
                    status_text = st.empty()
                    
                    resultados = []
                    
                    for i, cep in enumerate(ceps):
                        status_text.text(f"Consultando {i+1}/{len(ceps)}: {cep}")
                        resultado = consultar_cep(cep)
                        
                        if 'erro' not in resultado:
                            resultados.append({
                                'CEP': resultado.get('cep', ''),
                                'Logradouro': resultado.get('logradouro', ''),
                                'Bairro': resultado.get('bairro', ''),
                                'Cidade': resultado.get('localidade', ''),
                                'UF': resultado.get('uf', ''),
                                'DDD': resultado.get('ddd', '')
                            })
                        
                        progress_bar.progress((i + 1) / len(ceps))
                    
                    progress_bar.empty()
                    status_text.empty()
                    
                    if resultados:
                        df_resultados = pd.DataFrame(resultados)
                        
                        st.success(f"✅ {len(resultados)} CEPs consultados com sucesso!")
                        st.dataframe(df_resultados, use_container_width=True)
                        
                        # Adicionar aos dados coletados
                        st.session_state.dados_coletados.extend(resultados)
                        
                        criar_divider()
                        
                        # Download
                        col1, col2 = st.columns(2)
                        
                        with col1:
                            csv = df_resultados.to_csv(index=False).encode('utf-8')
                            st.download_button(
                                label="📥 Baixar CSV",
                                data=csv,
                                file_name="consulta_ceps.csv",
                                mime="text/csv",
                                use_container_width=True
                            )
                        
                        with col2:
                            output = io.BytesIO()
                            with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
                                df_resultados.to_excel(writer, index=False, sheet_name='CEPs')
                            output.seek(0)
                            
                            st.download_button(
                                label="📥 Baixar Excel",
                                data=output,
                                file_name="consulta_ceps.xlsx",
                                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                                use_container_width=True
                            )
                    else:
                        st.warning("⚠️ Nenhum CEP válido encontrado")
            else:
                st.warning("⚠️ Digite os CEPs")

elif st.session_state.api_selecionada == "CNPJ":
    st.markdown("### 🏢 Consulta de CNPJ")
    
    st.info("💡 Consulte dados de empresas através do CNPJ na Receita Federal")
    
    col1, col2 = st.columns([3, 1])
    
    with col1:
        cnpj_input = st.text_input(
            "Digite o CNPJ",
            placeholder="Ex: 00.000.000/0001-00",
            help="CNPJ com ou sem formatação"
        )
    
    with col2:
        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("🔍 Consultar", use_container_width=True, type="primary"):
            if cnpj_input:
                with st.spinner("Consultando Receita Federal..."):
                    resultado = consultar_cnpj(cnpj_input)
                    
                    if 'erro' in resultado:
                        st.error(f"❌ {resultado['erro']}")
                    else:
                        st.success("✅ CNPJ encontrado!")
                        
                        # Dados da empresa
                        st.markdown("### 🏢 Dados da Empresa")
                        
                        col1, col2 = st.columns(2)
                        
                        with col1:
                            st.markdown("**Informações Básicas:**")
                            st.write(f"**Razão Social:** {resultado.get('nome', 'N/A')}")
                            st.write(f"**Nome Fantasia:** {resultado.get('fantasia', 'N/A')}")
                            st.write(f"**CNPJ:** {resultado.get('cnpj', 'N/A')}")
                            st.write(f"**Situação:** {resultado.get('situacao', 'N/A')}")
                            st.write(f"**Porte:** {resultado.get('porte', 'N/A')}")
                        
                        with col2:
                            st.markdown("**Atividade:**")
                            st.write(f"**Natureza Jurídica:** {resultado.get('natureza_juridica', 'N/A')}")
                            st.write(f"**Abertura:** {resultado.get('abertura', 'N/A')}")
                            st.write(f"**Capital Social:** R$ {resultado.get('capital_social', 'N/A')}")
                        
                        # Endereço
                        st.markdown("### 📍 Endereço")
                        endereco = f"{resultado.get('logradouro', '')}, {resultado.get('numero', '')} - {resultado.get('bairro', '')}"
                        st.write(f"**Logradouro:** {endereco}")
                        st.write(f"**Município:** {resultado.get('municipio', 'N/A')} - {resultado.get('uf', 'N/A')}")
                        st.write(f"**CEP:** {resultado.get('cep', 'N/A')}")
                        
                        # Contato
                        st.markdown("### 📞 Contato")
                        st.write(f"**Telefone:** {resultado.get('telefone', 'N/A')}")
                        st.write(f"**Email:** {resultado.get('email', 'N/A')}")
                        
                        # Adicionar ao histórico
                        st.session_state.historico_consultas.append({
                            'tipo': 'CNPJ',
                            'consulta': cnpj_input,
                            'data': datetime.now(),
                            'resultado': resultado
                        })
            else:
                st.warning("⚠️ Digite um CNPJ")

elif st.session_state.api_selecionada == "COTACAO":
    st.markdown("### 💱 Cotações de Moedas")
    
    st.info("💡 Consulte cotações atuais e históricas de moedas estrangeiras")
    
    tab1, tab2 = st.tabs(["📊 Cotação Atual", "📈 Histórico"])
    
    with tab1:
        if st.button("🔄 Atualizar Cotações", use_container_width=True, type="primary"):
            with st.spinner("Consultando..."):
                resultado = consultar_cotacao()
                
                if 'erro' in resultado:
                    st.error(f"❌ {resultado['erro']}")
                else:
                    st.success(f"✅ Cotações atualizadas em {datetime.now().strftime('%d/%m/%Y %H:%M')}")
                    
                    # Criar DataFrame
                    dados_cotacao = []
                    
                    moedas_map = {
                        'USDBRL': {'nome': 'Dólar Americano', 'simbolo': 'USD', 'emoji': '🇺🇸'},
                        'EURBRL': {'nome': 'Euro', 'simbolo': 'EUR', 'emoji': '🇪🇺'},
                        'GBPBRL': {'nome': 'Libra Esterlina', 'simbolo': 'GBP', 'emoji': '🇬🇧'},
                        'BTCBRL': {'nome': 'Bitcoin', 'simbolo': 'BTC', 'emoji': '₿'}
                    }
                    
                    for codigo, info in moedas_map.items():
                        if codigo in resultado:
                            dados = resultado[codigo]
                            dados_cotacao.append({
                                'Moeda': f"{info['emoji']} {info['nome']}",
                                'Código': info['simbolo'],
                                'Compra': float(dados.get('bid', 0)),
                                'Venda': float(dados.get('ask', 0)),
                                'Variação': float(dados.get('pctChange', 0))
                            })
                    
                    df_cotacao = pd.DataFrame(dados_cotacao)
                    
                    # Exibir com formatação
                    st.markdown("### 💰 Cotações Atuais (BRL)")
                    
                    for idx, row in df_cotacao.iterrows():
                        col1, col2, col3, col4 = st.columns([2, 1, 1, 1])
                        
                        with col1:
                            st.metric(row['Moeda'], row['Código'])
                        with col2:
                            st.metric("Compra", f"R$ {row['Compra']:.2f}")
                        with col3:
                            st.metric("Venda", f"R$ {row['Venda']:.2f}")
                        with col4:
                            delta_color = "normal" if row['Variação'] >= 0 else "inverse"
                            st.metric("Variação", f"{row['Variação']:.2f}%", delta=f"{row['Variação']:.2f}%")
                    
                    # Adicionar aos dados coletados
                    st.session_state.dados_coletados.extend(dados_cotacao)
    
    with tab2:
        st.markdown("**📈 Histórico de Cotações**")
        
        col1, col2 = st.columns([2, 1])
        
        with col1:
            moeda_historico = st.selectbox(
                "Selecione a moeda",
                ["USD", "EUR", "GBP", "BTC"],
                format_func=lambda x: {
                    'USD': '🇺🇸 Dólar Americano',
                    'EUR': '🇪🇺 Euro',
                    'GBP': '🇬🇧 Libra Esterlina',
                    'BTC': '₿ Bitcoin'
                }[x]
            )
        
        with col2:
            dias_historico = st.selectbox(
                "Período",
                [7, 15, 30, 60, 90],
                format_func=lambda x: f"{x} dias"
            )
        
        if st.button("📊 Gerar Gráfico", use_container_width=True, type="primary"):
            with st.spinner("Carregando histórico..."):
                resultado = consultar_cotacao_historico(moeda_historico, dias_historico)
                
                if isinstance(resultado, dict) and 'erro' in resultado:
                    st.error(f"❌ {resultado['erro']}")
                else:
                    # Processar dados
                    datas = [datetime.fromtimestamp(int(item['timestamp'])) for item in resultado]
                    valores = [float(item['bid']) for item in resultado]
                    
                    # Criar gráfico
                    fig = go.Figure()
                    
                    fig.add_trace(go.Scatter(
                        x=datas,
                        y=valores,
                        mode='lines+markers',
                        name=f'{moeda_historico}/BRL',
                        line=dict(color='#667eea', width=2),
                        marker=dict(size=6)
                    ))
                    
                    fig.update_layout(
                        title=f"Histórico de Cotação: {moeda_historico}/BRL ({dias_historico} dias)",
                        xaxis_title="Data",
                        yaxis_title="Valor (BRL)",
                        height=500,
                        hovermode='x unified'
                    )
                    
                    st.plotly_chart(fig, use_container_width=True)
                    
                    # Estatísticas
                    col1, col2, col3, col4 = st.columns(4)
                    
                    with col1:
                        st.metric("Mínimo", f"R$ {min(valores):.4f}")
                    with col2:
                        st.metric("Máximo", f"R$ {max(valores):.4f}")
                    with col3:
                        st.metric("Média", f"R$ {sum(valores)/len(valores):.4f}")
                    with col4:
                        variacao = ((valores[0] - valores[-1]) / valores[-1]) * 100
                        st.metric("Variação", f"{variacao:.2f}%")

elif st.session_state.api_selecionada == "FERIADOS":
    st.markdown("### 📅 Feriados Nacionais")
    
    st.info("💡 Consulte feriados nacionais brasileiros por ano")
    
    col1, col2 = st.columns([3, 1])
    
    with col1:
        ano_feriado = st.number_input(
            "Ano",
            min_value=2020,
            max_value=2030,
            value=datetime.now().year,
            step=1
        )
    
    with col2:
        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("🔍 Consultar", use_container_width=True, type="primary"):
            with st.spinner("Consultando..."):
                resultado = consultar_feriados(ano_feriado)
                
                if isinstance(resultado, dict) and 'erro' in resultado:
                    st.error(f"❌ {resultado['erro']}")
                else:
                    st.success(f"✅ {len(resultado)} feriados encontrados para {ano_feriado}")
                    
                    # Criar DataFrame
                    df_feriados = pd.DataFrame(resultado)
                    df_feriados['date'] = pd.to_datetime(df_feriados['date'])
                    df_feriados = df_feriados.sort_values('date')
                    
                    # Adicionar dia da semana
                    df_feriados['dia_semana'] = df_feriados['date'].dt.day_name()
                    
                    # Traduzir dias
                    dias_map = {
                        'Monday': 'Segunda',
                        'Tuesday': 'Terça',
                        'Wednesday': 'Quarta',
                        'Thursday': 'Quinta',
                        'Friday': 'Sexta',
                        'Saturday': 'Sábado',
                        'Sunday': 'Domingo'
                    }
                    df_feriados['dia_semana'] = df_feriados['dia_semana'].map(dias_map)
                    
                    # Formatar data
                    df_feriados['Data'] = df_feriados['date'].dt.strftime('%d/%m/%Y')
                    
                    # Renomear colunas
                    df_display = df_feriados[['Data', 'name', 'dia_semana', 'type']].copy()
                    df_display.columns = ['Data', 'Feriado', 'Dia da Semana', 'Tipo']
                    
                    # Traduzir tipo
                    tipo_map = {
                        'national': 'Nacional',
                        'optional': 'Opcional',
                        'religious': 'Religioso'
                    }
                    df_display['Tipo'] = df_display['Tipo'].map(tipo_map)
                    
                    st.dataframe(df_display, use_container_width=True)
                    
                    criar_divider()
                    
                    # Estatísticas
                    col1, col2, col3 = st.columns(3)
                    
                    with col1:
                        st.metric("Total de Feriados", len(df_feriados))
                    with col2:
                        feriados_fim_semana = len(df_feriados[df_feriados['dia_semana'].isin(['Sábado', 'Domingo'])])
                        st.metric("Finais de Semana", feriados_fim_semana)
                    with col3:
                        feriados_uteis = len(df_feriados) - feriados_fim_semana
                        st.metric("Dias Úteis", feriados_uteis)
                    
                    # Download
                    criar_divider()
                    
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        csv = df_display.to_csv(index=False).encode('utf-8')
                        st.download_button(
                            label="📥 Baixar CSV",
                            data=csv,
                            file_name=f"feriados_{ano_feriado}.csv",
                            mime="text/csv",
                            use_container_width=True
                        )
                    
                    with col2:
                        output = io.BytesIO()
                        with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
                            df_display.to_excel(writer, index=False, sheet_name='Feriados')
                        output.seek(0)
                        
                        st.download_button(
                            label="📥 Baixar Excel",
                            data=output,
                            file_name=f"feriados_{ano_feriado}.xlsx",
                            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                            use_container_width=True
                        )

elif st.session_state.api_selecionada == "BANCOS":
    st.markdown("### 🏦 Lista de Bancos Brasileiros")
    
    st.info("💡 Consulte a lista completa de bancos cadastrados no Banco Central")
    
    if st.button("🔍 Carregar Lista de Bancos", use_container_width=True, type="primary"):
        with st.spinner("Consultando..."):
            resultado = consultar_bancos()
            
            if isinstance(resultado, dict) and 'erro' in resultado:
                st.error(f"❌ {resultado['erro']}")
            else:
                st.success(f"✅ {len(resultado)} bancos encontrados")
                
                # Criar DataFrame
                df_bancos = pd.DataFrame(resultado)
                
                # Renomear colunas
                if 'code' in df_bancos.columns:
                    df_bancos = df_bancos.rename(columns={
                        'code': 'Código',
                        'name': 'Nome',
                        'fullName': 'Nome Completo'
                    })
                
                # Filtro de pesquisa
                criar_divider()
                
                pesquisa = st.text_input(
                    "🔍 Pesquisar banco",
                    placeholder="Digite o nome ou código do banco"
                )
                
                if pesquisa:
                    df_filtrado = df_bancos[
                        df_bancos['Nome'].str.contains(pesquisa, case=False, na=False) |
                        df_bancos['Código'].astype(str).str.contains(pesquisa, case=False)
                    ]
                    st.write(f"**Resultados:** {len(df_filtrado)} banco(s) encontrado(s)")
                    st.dataframe(df_filtrado, use_container_width=True)
                else:
                    st.dataframe(df_bancos, use_container_width=True)
                
                criar_divider()
                
                # Estatísticas
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    st.metric("Total de Bancos", len(df_bancos))
                with col2:
                    st.metric("Menor Código", df_bancos['Código'].min())
                with col3:
                    st.metric("Maior Código", df_bancos['Código'].max())
                
                criar_divider()
                
                # Download
                col1, col2 = st.columns(2)
                
                with col1:
                    csv = df_bancos.to_csv(index=False).encode('utf-8')
                    st.download_button(
                        label="📥 Baixar CSV",
                        data=csv,
                        file_name="bancos_brasil.csv",
                        mime="text/csv",
                        use_container_width=True
                    )
                
                with col2:
                    output = io.BytesIO()
                    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
                        df_bancos.to_excel(writer, index=False, sheet_name='Bancos')
                    output.seek(0)
                    
                    st.download_button(
                        label="📥 Baixar Excel",
                        data=output,
                        file_name="bancos_brasil.xlsx",
                        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                        use_container_width=True
                    )

elif st.session_state.api_selecionada == "IBGE":
    st.markdown("### 🗺️ Dados do IBGE")
    
    st.info("💡 Consulte dados geográficos do Instituto Brasileiro de Geografia e Estatística")
    
    tab1, tab2 = st.tabs(["📍 Estados", "🏙️ Municípios"])
    
    with tab1:
        if st.button("🔍 Carregar Estados", use_container_width=True, type="primary"):
            with st.spinner("Consultando IBGE..."):
                resultado = consultar_ibge_estados()
                
                if isinstance(resultado, dict) and 'erro' in resultado:
                    st.error(f"❌ {resultado['erro']}")
                else:
                    st.success(f"✅ {len(resultado)} estados encontrados")
                    
                    # Criar DataFrame
                    estados_data = []
                    for estado in resultado:
                        estados_data.append({
                            'ID': estado['id'],
                            'Sigla': estado['sigla'],
                            'Nome': estado['nome'],
                            'Região': estado['regiao']['nome']
                        })
                    
                    df_estados = pd.DataFrame(estados_data)
                    df_estados = df_estados.sort_values('Nome')
                    
                    st.dataframe(df_estados, use_container_width=True)
                    
                    criar_divider()
                    
                    # Estatísticas por região
                    st.markdown("### 📊 Estados por Região")
                    
                    regiao_count = df_estados['Região'].value_counts()
                    
                    fig = px.bar(
                        x=regiao_count.index,
                        y=regiao_count.values,
                        labels={'x': 'Região', 'y': 'Quantidade de Estados'},
                        title="Distribuição de Estados por Região",
                        color=regiao_count.values,
                        color_continuous_scale='Blues'
                    )
                    
                    st.plotly_chart(fig, use_container_width=True)
                    
                    criar_divider()
                    
                    # Download
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        csv = df_estados.to_csv(index=False).encode('utf-8')
                        st.download_button(
                            label="📥 Baixar CSV",
                            data=csv,
                            file_name="estados_brasil.csv",
                            mime="text/csv",
                            use_container_width=True
                        )
                    
                    with col2:
                        output = io.BytesIO()
                        with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
                            df_estados.to_excel(writer, index=False, sheet_name='Estados')
                        output.seek(0)
                        
                        st.download_button(
                            label="📥 Baixar Excel",
                            data=output,
                            file_name="estados_brasil.xlsx",
                            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                            use_container_width=True
                        )
    
    with tab2:
        st.markdown("**🏙️ Consultar Municípios por Estado**")
        
        col1, col2 = st.columns([3, 1])
        
        with col1:
            uf_select = st.selectbox(
                "Selecione o Estado",
                ['AC', 'AL', 'AP', 'AM', 'BA', 'CE', 'DF', 'ES', 'GO', 'MA', 
                 'MT', 'MS', 'MG', 'PA', 'PB', 'PR', 'PE', 'PI', 'RJ', 'RN', 
                 'RS', 'RO', 'RR', 'SC', 'SP', 'SE', 'TO']
            )
        
        with col2:
            st.markdown("<br>", unsafe_allow_html=True)
            if st.button("🔍 Consultar", use_container_width=True, type="primary"):
                with st.spinner(f"Consultando municípios de {uf_select}..."):
                    resultado = consultar_ibge_municipios(uf_select)
                    
                    if isinstance(resultado, dict) and 'erro' in resultado:
                        st.error(f"❌ {resultado['erro']}")
                    else:
                        st.success(f"✅ {len(resultado)} municípios encontrados")
                        
                        # Criar DataFrame
                        municipios_data = []
                        for municipio in resultado:
                            municipios_data.append({
                                'ID': municipio['id'],
                                'Nome': municipio['nome'],
                                'Microrregião': municipio.get('microrregiao', {}).get('nome', 'N/A'),
                                'Mesorregião': municipio.get('microrregiao', {}).get('mesorregiao', {}).get('nome', 'N/A')
                            })
                        
                        df_municipios = pd.DataFrame(municipios_data)
                        df_municipios = df_municipios.sort_values('Nome')
                        
                        # Filtro de pesquisa
                        pesquisa_mun = st.text_input(
                            "🔍 Pesquisar município",
                            placeholder="Digite o nome do município"
                        )
                        
                        if pesquisa_mun:
                            df_filtrado = df_municipios[
                                df_municipios['Nome'].str.contains(pesquisa_mun, case=False, na=False)
                            ]
                            st.write(f"**Resultados:** {len(df_filtrado)} município(s)")
                            st.dataframe(df_filtrado, use_container_width=True)
                        else:
                            st.dataframe(df_municipios, use_container_width=True)
                        
                        criar_divider()
                        
                        # Estatísticas
                        col1, col2 = st.columns(2)
                        
                        with col1:
                            st.metric("Total de Municípios", len(df_municipios))
                        with col2:
                            mesorregioes = df_municipios['Mesorregião'].nunique()
                            st.metric("Mesorregiões", mesorregioes)
                        
                        criar_divider()
                        
                        # Download
                        col1, col2 = st.columns(2)
                        
                        with col1:
                            csv = df_municipios.to_csv(index=False).encode('utf-8')
                            st.download_button(
                                label="📥 Baixar CSV",
                                data=csv,
                                file_name=f"municipios_{uf_select}.csv",
                                mime="text/csv",
                                use_container_width=True
                            )
                        
                        with col2:
                            output = io.BytesIO()
                            with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
                                df_municipios.to_excel(writer, index=False, sheet_name='Municípios')
                            output.seek(0)
                            
                            st.download_button(
                                label="📥 Baixar Excel",
                                data=output,
                                file_name=f"municipios_{uf_select}.xlsx",
                                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                                use_container_width=True
                            )

else:
    st.info("👆 Selecione uma API acima para começar as consultas")
    
    criar_divider()
    
    # Informações sobre as APIs
    st.markdown("### 📚 Sobre as APIs Disponíveis")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("""
        #### 📍 ViaCEP
        **Consulta de CEP**
        
        - ✅ Gratuita e sem limites
        - ✅ Dados atualizados dos Correios
        - ✅ Retorna endereço completo
        - ✅ Suporta consulta em lote
        
        **Dados retornados:**
        - Logradouro, Bairro, Cidade
        - UF, CEP, DDD
        
        ---
        
        #### 🏢 ReceitaWS
        **Consulta de CNPJ**
        
        - ✅ Dados da Receita Federal
        - ✅ Informações completas da empresa
        - ⚠️ Limite de 3 consultas/minuto
        - ✅ Dados de sócios e atividades
        
        **Dados retornados:**
        - Razão social, Nome fantasia
        - Situação cadastral, Capital social
        - Endereço completo, Atividades
        
        ---
        
        #### 💱 AwesomeAPI
        **Cotações de Moedas**
        
        - ✅ Cotações em tempo real
        - ✅ Histórico disponível
        - ✅ Múltiplas moedas (USD, EUR, GBP, BTC)
        - ✅ Atualização frequente
        
        **Dados retornados:**
        - Valores de compra e venda
        - Variação percentual
        - Histórico de até 365 dias
        """)
    
    with col2:
        st.markdown("""
        #### 📅 Brasil API - Feriados
        **Feriados Nacionais**
        
        - ✅ Feriados nacionais brasileiros
        - ✅ Dados por ano
        - ✅ Tipos: nacional, opcional, religioso
        - ✅ Fácil integração com calendários
        
        **Dados retornados:**
        - Data do feriado
        - Nome e tipo
        - Classificação
        
        ---
        
        #### 🏦 Brasil API - Bancos
        **Lista de Bancos**
        
        - ✅ Todos os bancos do Brasil
        - ✅ Dados do Banco Central
        - ✅ Códigos oficiais
        - ✅ Nomes completos
        
        **Dados retornados:**
        - Código do banco
        - Nome e nome completo
        - Informações cadastrais
        
        ---
        
        #### 🗺️ IBGE API
        **Dados Geográficos**
        
        - ✅ Estados brasileiros
        - ✅ Municípios por estado
        - ✅ Regiões e divisões
        - ✅ Dados oficiais do IBGE
        
        **Dados retornados:**
        - Estados e regiões
        - Municípios e microrregiões
        - IDs oficiais do IBGE
        """)
    
    criar_divider()
    
    # Guia de uso
    st.markdown("### 🚀 Como Usar")
    
    st.markdown("""
    #### Passo a Passo
    
    1. **🎯 Selecione a API** que você deseja consultar
    2. **📝 Preencha os dados** solicitados (CEP, CNPJ, etc)
    3. **🔍 Clique em Consultar** para obter os resultados
    4. **📊 Visualize os dados** retornados
    5. **📥 Exporte os resultados** em CSV ou Excel
    
    #### 💡 Dicas
    
    - **CEP:** Aceita formato com ou sem hífen (01310-100 ou 01310100)
    - **CNPJ:** Aceita formato com ou sem pontuação
    - **Cotações:** Histórico limitado a 365 dias
    - **Lote:** Use consultas em lote para economizar tempo
    - **Cache:** Alguns resultados são armazenados temporariamente
    
    #### ⚠️ Limitações
    
    - **ReceitaWS (CNPJ):** Máximo 3 consultas por minuto
    - **AwesomeAPI:** Dados de cotação podem ter delay de alguns minutos
    - **Todas APIs:** Dependem de conexão com internet ativa
    - **IBGE:** Dados estáticos, atualizados periodicamente
    """)

# ========================================
# HISTÓRICO E DADOS COLETADOS
# ========================================

if st.session_state.historico_consultas or st.session_state.dados_coletados:
    criar_divider()
    
    st.markdown("### 📋 Dados da Sessão")
    
    tab1, tab2 = st.tabs(["📊 Dados Coletados", "🕐 Histórico de Consultas"])
    
    with tab1:
        if st.session_state.dados_coletados:
            st.write(f"**Total de registros coletados:** {len(st.session_state.dados_coletados)}")
            
            df_coletados = pd.DataFrame(st.session_state.dados_coletados)
            st.dataframe(df_coletados, use_container_width=True)
            
            criar_divider()
            
            # Download consolidado
            col1, col2, col3 = st.columns([2, 2, 1])
            
            with col1:
                csv = df_coletados.to_csv(index=False).encode('utf-8')
                st.download_button(
                    label="📥 Baixar Todos os Dados (CSV)",
                    data=csv,
                    file_name="dados_coletados.csv",
                    mime="text/csv",
                    use_container_width=True
                )
            
            with col2:
                output = io.BytesIO()
                with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
                    df_coletados.to_excel(writer, index=False, sheet_name='Dados')
                output.seek(0)
                
                st.download_button(
                    label="📥 Baixar Todos os Dados (Excel)",
                    data=output,
                    file_name="dados_coletados.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                    use_container_width=True
                )
            
            with col3:
                if st.button("🗑️ Limpar", use_container_width=True):
                    st.session_state.dados_coletados = []
                    st.rerun()
        else:
            st.info("Nenhum dado coletado ainda")
    
    with tab2:
        if st.session_state.historico_consultas:
            st.write(f"**Total de consultas:** {len(st.session_state.historico_consultas)}")
            
            for i, consulta in enumerate(reversed(st.session_state.historico_consultas[-10:]), 1):
                with st.expander(f"{i}. {consulta['tipo']} - {consulta['data'].strftime('%d/%m/%Y %H:%M')}"):
                    st.write(f"**Consulta:** {consulta['consulta']}")
                    st.json(consulta['resultado'])
            
            if len(st.session_state.historico_consultas) > 10:
                st.info(f"Mostrando últimas 10 de {len(st.session_state.historico_consultas)} consultas")
            
            criar_divider()
            
            if st.button("🗑️ Limpar Histórico", use_container_width=True):
                st.session_state.historico_consultas = []
                st.rerun()
        else:
            st.info("Nenhuma consulta realizada ainda")

# Footer
criar_divider()
st.markdown("""
<div style='text-align: center; color: #666; padding: 1rem 0;'>
    <p>🌐 Consultor de APIs Públicas | Integração e Enriquecimento de Dados</p>
</div>
""", unsafe_allow_html=True)