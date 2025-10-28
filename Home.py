import streamlit as st

# Configuração da página
st.set_page_config(
    page_title="Ferramentas de Processamento",
    page_icon="🛠️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Estilo global com HTML/CSS moderno
st.markdown("""
    <style>
        /* Ocultar elementos padrão */
        #MainMenu {visibility: hidden;}
        footer {visibility: hidden;}
        .stDeployButton {display:none;}
        
        /* Tema e aparência geral */
        .main-header {
            padding: 2rem;
            border-radius: 15px;
            color: white;
            text-align: center;
            margin-bottom: 2rem;
        }
        
        .main-header h1 {
            color: white;
            font-size: 2.5rem;
            margin-bottom: 0.5rem;
            font-weight: 700;
        }
        
        .main-header p {
            color:white;
            font-size: 1.1rem;
            margin: 0;
        }
        
        /* Cards das ferramentas */
        .tool-card {
            padding: 1.5rem;
            border-radius: 12px;
            margin-bottom: 1.5rem;
            transition: transform 0.3s ease, box-shadow 0.3s ease;
        }
        
        .tool-card:hover {
            transform: translateY(-5px);
        }
        
        .tool-card h3 {
            color: white;
            font-size: 1.4rem;
            margin-bottom: 0.8rem;
            font-weight: 600;
        }
        
        .tool-card ul {
            color: white;
            line-height: 1.8;
            margin-left: 1rem;
        }
        
        .tool-card li {
            margin-bottom: 0.4rem;
        }
        
        /* Seções informativas */
        .info-section {
            padding: 1.5rem;
            border-radius: 10px;
            margin: 1.5rem 0;
        }
        
        .info-section h3 {
            color:white;
            margin-bottom: 1rem;
            font-size: 1.3rem;
        }
        
        .warning-section {
            padding: 1.5rem;
            border-radius: 10px;
            margin: 1.5rem 0;
        }
        
        .warning-section h3 {
            color: white;
            margin-bottom: 1rem;
            font-size: 1.3rem;
        }
        
        /* Badge de feature */
        .feature-badge {
            display: inline-block;
            background: #667eea;
            color: white;
            padding: 0.3rem 0.5rem;
            border-radius: 5px;
            font-size: 0.85rem;
            margin: 0.2rem;
            font-weight: 500;
        }
        
        /* Divider personalizado */
        .custom-divider {
            height: 2px;
            background: linear-gradient(90deg, transparent, #667eea, transparent);
            margin: 2rem 0;
        }
        
        /* Lista de instruções */
        .instruction-list {
            padding: 1.5rem;
            border-radius: 10px;
        }
        
        .instruction-list ol {
            color: white;
            font-size: 1.05rem;
            line-height: 2;
        }
        
        .instruction-list li {
            margin-bottom: 0.5rem;
        }
        
        /* Destacar texto importante */
        strong {
            color: #ccff33;
        }
    </style>
""", unsafe_allow_html=True)

# Cabeçalho principal
st.markdown("""
    <div class="main-header">
        <h1>🛠️ Ferramentas de Processamento</h1>
    </div>
""", unsafe_allow_html=True)

# Introdução aprimorada
st.markdown("""
### 👋 Bem-vindo(a)!

Este conjunto de ferramentas foi desenvolvido para **simplificar** tarefas rotineiras de processamento de arquivos. 
Com interface intuitiva e funcionalidades robustas, você economiza tempo e reduz erros em operações do dia a dia.

<div class="custom-divider"></div>
""", unsafe_allow_html=True)

# Especificações técnicas
st.markdown("""
<div class="info-section">
    <h3>📋 Especificações Técnicas</h3>
    <ul>
        <li>✅ <strong>Formatos suportados:</strong> Excel (.xlsx), PDF, CSV, Imagens (PNG, JPG), Texto (.txt)</li>
        <li>✅ <strong>Limite de upload:</strong> Até 5MB por arquivo (pode variar conforme funcionalidade)</li>
        <li>✅ <strong>Processamento:</strong> Local no navegador - seus dados não são enviados para servidores externos</li>
        <li>✅ <strong>Machine Learning:</strong> Modelos avançados de previsão (XGBoost, Random Forest, Gradient Boosting)</li>
        <li>✅ <strong>APIs Integradas:</strong> ViaCEP, ReceitaWS, AwesomeAPI, Brasil API, IBGE</li>
        <li>✅ <strong>Total de Ferramentas:</strong> 7 funcionalidades completas e profissionais</li>
    </ul>
</div>
""", unsafe_allow_html=True)

# Cards das ferramentas
st.markdown("### 🎯 Ferramentas Disponíveis")

col1, col2, col3 = st.columns(3)

with col1:
    st.markdown("""
    <div class='tool-card'>
        <h3>📈 Previsão de Demanda com IA</h3>
        <ul>
            <li>🤖 <strong>6 algoritmos</strong> de Machine Learning disponíveis</li>
            <li>📊 Análise automática de sazonalidade e tendências</li>
            <li>🎯 Previsões futuras com intervalos de confiança (95%)</li>
            <li>📉 Métricas de precisão (MAE, RMSE, MAPE, R²)</li>
            <li>💡 Recomendações e insights automáticos</li>
        </ul>
        <span class="feature-badge">IA</span>
        <span class="feature-badge">Avançado</span>
    </div>
    
    <div class='tool-card'>
        <h3>📂 Unir Arquivos Excel</h3>
        <ul>
            <li>📑 Consolida múltiplos arquivos Excel em um único</li>
            <li>✅ Validação automática de estrutura e colunas</li>
            <li>📊 Estatísticas detalhadas do consolidado</li>
            <li>💾 Download do resultado em formato .xlsx</li>
            <li>⚡ Processamento rápido de grandes volumes</li>
        </ul>
        <span class="feature-badge">Excel</span>
        <span class="feature-badge">Básico</span>
    </div>
    
    <div class='tool-card'>
        <h3>📄 Editor de PDF</h3>
        <ul>
            <li>✂️ Extrair páginas específicas do PDF</li>
            <li>🔄 Reordenar e rotacionar páginas</li>
            <li>🗑️ Remover páginas indesejadas</li>
            <li>🔐 Adicionar/remover senha de proteção</li>
            <li>🖼️ Extrair todas as imagens do PDF</li>
        </ul>
        <span class="feature-badge">PDF</span>
        <span class="feature-badge">Intermediário</span>
    </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown("""
    <div class='tool-card'>
        <h3>📄 Unir PDFs</h3>
        <ul>
            <li>🔗 Combina múltiplos PDFs em um único documento</li>
            <li>↕️ Sistema de arrastar e soltar para definir ordem</li>
            <li>🎨 Preserva qualidade, formatação e metadados</li>
            <li>📥 Download do PDF unificado instantâneo</li>
            <li>🚀 Interface simples e intuitiva</li>
        </ul>
        <span class="feature-badge">PDF</span>
        <span class="feature-badge">Básico</span>
    </div>
    
    <div class='tool-card'>
        <h3>🔄 Conversor Universal</h3>
        <ul>
            <li>🖼️ <strong>PDF ↔ Imagem</strong> (PNG, JPEG)</li>
            <li>📝 <strong>Texto → PDF</strong> / LaTeX</li>
            <li>🎯 Conversão em lote (múltiplos arquivos)</li>
            <li>⚙️ Preserva qualidade e formatação</li>
            <li>💾 Download individual de cada resultado</li>
        </ul>
        <span class="feature-badge">Conversão</span>
        <span class="feature-badge">Intermediário</span>
    </div>
    
    <div class='tool-card'>
        <h3>🔍 Detector de Anomalias</h3>
        <ul>
            <li>🤖 <strong>4 algoritmos</strong> de detecção (IQR, Z-Score, ML)</li>
            <li>📊 Visualizações interativas e insights</li>
            <li>🎯 Detecção univariada e multivariada</li>
            <li>💡 Recomendações de ações e tratamento</li>
            <li>📥 Relatórios completos com estatísticas</li>
        </ul>
        <span class="feature-badge">IA</span>
        <span class="feature-badge">Avançado</span>
    </div>
    """, unsafe_allow_html=True)

with col3:
    st.markdown("""
    <div class='tool-card'>
        <h3>🌐 Consultor de APIs</h3>
        <ul>
            <li>📍 <strong>CEP:</strong> Consulta de endereços (individual/lote)</li>
            <li>🏢 <strong>CNPJ:</strong> Dados completos da Receita Federal</li>
            <li>💱 <strong>Câmbio:</strong> Cotações e histórico de moedas</li>
            <li>📅 <strong>Feriados:</strong> Calendário nacional completo</li>
            <li>🗺️ <strong>IBGE:</strong> Estados, municípios e dados geográficos</li>
        </ul>
        <span class="feature-badge">Integração</span>
        <span class="feature-badge">Básico</span>
    </div>
    
    <div class='tool-card'>
        <h3>🔢 Calculadora de Métricas</h3>
        <ul>
            <li>💰 <strong>Financeiras:</strong> ROI, Payback, VPL, TIR, Break-even</li>
            <li>📈 <strong>Vendas:</strong> Margem, Markup, Ticket Médio, Conversão</li>
            <li>🎯 <strong>Marketing:</strong> CAC, LTV, LTV/CAC, Churn, ROAS</li>
            <li>📊 Interpretações automáticas e benchmarks</li>
            <li>📥 Histórico de cálculos exportável</li>
        </ul>
        <span class="feature-badge">Negócio</span>
        <span class="feature-badge">Básico</span>
    </div>
    """, unsafe_allow_html=True)

st.markdown("<div class='custom-divider'></div>", unsafe_allow_html=True)

# Oportunidades
col1, col2 = st.columns(2)

with col1:
    st.markdown("""
    <div class="info-section">
        <h3>⚙️ Oportunidades de Uso</h3>
        <ul>
            <li>📊 <strong>Gerar previsões precisas</strong> para planejamento estratégico</li>
            <li>📝 <strong>Consolidar relatórios</strong> de diferentes fontes rapidamente</li>
            <li>🎯 <strong>Padronizar processos</strong> de conversão e união de arquivos</li>
            <li>📈 <strong>Melhorar qualidade</strong> das análises</li>
            <li>🔍 <strong>Identificar anomalias</strong> em dados e evitar erros</li>
            <li>🌐 <strong>Enriquecer bases de dados</strong> com APIs públicas</li>
            <li>📄 <strong>Editar PDFs profissionalmente</strong> sem software pago</li>
        </ul>
    </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown("""
    <div class="warning-section">
        <h3>⚠️ Limitações e Considerações</h3>
        <ul>
            <li>⏳ <strong>Tempo de processamento:</strong> Arquivos grandes podem levar alguns segundos</li>
            <li>📄 <strong>Formatação de PDFs:</strong> Conversões podem variar conforme complexidade</li>
            <li>📢 <strong>Previsão de Demanda:</strong> Requer mínimo de 12 meses de histórico</li>
            <li>📏 <strong>Tamanho máximo:</strong> 5MB por arquivo (limite do navegador)</li>
            <li>🎯 <strong>IA não prevê eventos extraordinários</strong> (crises, mudanças estruturais)</li>
            <li>💾 <strong>Backup recomendado:</strong> Sempre mantenha cópias dos originais</li>
            <li>🌐 <strong>APIs externas:</strong> Dependem de conexão com internet e disponibilidade dos serviços</li>
            <li>⏱️ <strong>Rate limits:</strong> Algumas APIs têm limite de consultas (ex: CNPJ 3/min)</li>
        </ul>
    </div>
    """, unsafe_allow_html=True)

st.markdown("<div class='custom-divider'></div>", unsafe_allow_html=True)

# Instruções de uso
st.markdown("""
<div class="instruction-list">
    <h3>📖 Como Usar as Ferramentas</h3>
    <ol>
        <li>🎯 <strong>Escolha a ferramenta</strong> desejada no <strong>menu lateral esquerdo</strong></li>
        <li>📤 <strong>Faça o upload</strong> dos arquivos conforme indicado em cada página</li>
        <li>⚙️ <strong>Configure as opções</strong> se necessário (ordem, formato, parâmetros)</li>
        <li>🚀 <strong>Clique em Processar</strong> e aguarde a execução (barra de progresso visível)</li>
        <li>📥 <strong>Baixe o resultado</strong> através do botão de download disponibilizado</li>
    </ol>
</div>
""", unsafe_allow_html=True)

st.markdown("<div class='custom-divider'></div>", unsafe_allow_html=True)

# Dicas importantes
st.markdown("""
### 💡 Dicas para Melhores Resultados

<div style="padding: 1.5rem; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.05);">

**📊 Para Previsão de Demanda:**
- ✅ Use dados mensais com pelo menos 24 meses de histórico
- ✅ Formato aceito: Ano | Mês | Volume (Toneladas)
- ✅ Valores com ponto como milhar (47.764,00) e vírgula como decimal
- ✅ Atenção com outliers extremos antes do upload

**📝 Para União de Arquivos:**
- ✅ Certifique-se de que todos os Excel têm as **mesmas colunas**
- ✅ Arquivos sem fórmulas externas (valores puros)
- ✅ Verifique tamanho antes de enviar (máx. 5MB cada)

**📄 Para PDFs:**
- ✅ Arraste e solte para definir a ordem desejada
- ✅ Arquivos sem proteção por senha (ou use o Editor de PDF primeiro)
- ✅ PDFs não escaneados para melhor qualidade
- ✅ Use o Editor de PDF para operações avançadas (extrair, rotacionar, proteger)

**🔄 Para Conversões:**
- ✅ Imagens em alta resolução para melhor resultado
- ✅ Textos simples convertem melhor que formatações complexas
- ✅ Teste com um arquivo antes de converter em lote

**🔍 Para Detector de Anomalias:**
- ✅ Comece com parâmetros padrão e ajuste conforme necessário
- ✅ IQR/Z-Score para análise de uma variável
- ✅ Isolation Forest para múltiplas variáveis correlacionadas
- ✅ Valide manualmente antes de remover dados

**🌐 Para Consultor de APIs:**
- ✅ CEP e CNPJ podem ser digitados com ou sem formatação
- ✅ Use consulta em lote para economizar tempo (CEP)
- ✅ CNPJ tem limite de 3 consultas por minuto (ReceitaWS)
- ✅ Exporte dados coletados antes de fechar a sessão

</div>
""", unsafe_allow_html=True)

# Footer
st.markdown("<div class='custom-divider'></div>", unsafe_allow_html=True)

st.markdown("""
<div style='text-align: center; color: white; padding: 2rem 0;'>
    <p style='font-size: 1.1rem; margin-bottom: 0.5rem;'>🚀 Ferramentas de Processamento Inteligente</p>
    <p style='font-size: 0.9rem;'>Desenvolvido pelo Time de Business Intelligence</p>
    <p style='font-size: 0.85rem; color: white;'>Versão 2.0 | 2025 | 7 Ferramentas Disponíveis</p>
</div>
""", unsafe_allow_html=True)