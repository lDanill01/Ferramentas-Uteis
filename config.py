"""
CONFIG.PY - Configurações Globais e Funções Utilitárias
========================================================
Centraliza estilos, configurações e funções reutilizáveis
para todas as páginas do projeto Streamlit.
"""

import streamlit as st
import pandas as pd
import io
from typing import Tuple, Optional

# ==============================
# CONFIGURAÇÕES GLOBAIS
# ==============================

# Paleta de cores do projeto
COLORS = {
    'primary': "#110534",
    'secondary': "#22172d",
    'success': '#28a745',
    'warning': '#ffc107',
    'danger': '#dc3545',
    'info': '#17a2b8',
    'light': "#000000",
    'dark': '#343a40'
}

# Configurações de upload
MAX_FILE_SIZE_MB = 5
SUPPORTED_FORMATS = {
    'excel': ['xlsx', 'xls'],
    'pdf': ['pdf'],
    'image': ['png', 'jpg', 'jpeg'],
    'text': ['txt', 'csv']
}


# ==============================
# CONFIGURAÇÃO DE PÁGINA
# ==============================

def configurar_pagina(
    titulo: str = "Ferramentas de Processamento",
    icone: str = "🛠️",
    layout: str = "wide"
) -> None:
    """
    Define as configurações básicas da página do Streamlit.
    
    Args:
        titulo: Título da página
        icone: Ícone da página (emoji)
        layout: Layout da página ('wide' ou 'centered')
    """
    st.set_page_config(
        page_title=titulo,
        page_icon=icone,
        layout=layout,
        initial_sidebar_state="expanded"
    )


def aplicar_estilo_global() -> None:
    """
    Aplica CSS global customizado para todas as páginas.
    Inclui: tema, cards, botões, títulos e animações.
    """
    st.markdown(f"""
        <style>
            /* ========== OCULTAR ELEMENTOS PADRÃO ========== */
            #MainMenu {{visibility: hidden;}}
            footer {{visibility: hidden;}}
            .stDeployButton {{display: none;}}
            
            /* ========== TEMA GERAL ========== */
            .main {{
                background-color: #000000;
            }}
            
            /* ========== CARDS E CONTAINERS ========== */
            .custom-card {{
                padding: 1.5rem;
                border-radius: 12px;
                box-shadow: 0 4px 15px rgba(0,0,0,0.08);
                margin: 1rem 0;
                border-left: 4px solid {COLORS['primary']};
                transition: transform 0.3s ease, box-shadow 0.3s ease;
            }}
            
            .custom-card:hover {{
                transform: translateY(-3px);
                box-shadow: 0 6px 20px rgba(0,0,0,0.12);
            }}
            
            /* ========== CABEÇALHOS ========== */
            .page-header {{
                padding: 2rem;
                border-radius: 15px;
                color: white;
                text-align: center;
                margin-bottom: 2rem;
                box-shadow: 0 8px 20px rgba(0,0,0,0.15);
            }}
            
            .page-header h1 {{
                color: white !important;
                font-size: 2.2rem;
                margin: 0;
                font-weight: 700;
            }}
            
            .page-header p {{
                color: #f0f0f0;
                margin: 0.5rem 0 0 0;
                font-size: 1rem;
            }}
            
            /* ========== BOTÕES CUSTOMIZADOS ========== */
            .stButton > button {{
                color: white;
                border: none;
                border-radius: 8px;
                padding: 0.6rem 1.5rem;
                font-weight: 600;
                font-size: 1rem;
                transition: all 0.3s ease;
                box-shadow: 0 4px 10px rgba(102, 126, 234, 0.3);
            }}
            
            .stButton > button:hover {{
                transform: translateY(-2px);
                box-shadow: 0 6px 15px rgba(102, 126, 234, 0.4);
            }}
            
            .stButton > button:active {{
                transform: translateY(0);
            }}
            
            /* ========== SEÇÕES INFORMATIVAS ========== */
            .info-box {{
                background-color: {COLORS['dark']};
                padding: 1.2rem;
                border-radius: 10px;
                border-left: 4px solid {COLORS['info']};
                margin: 1rem 0;
            }}
            
            .warning-box {{
                padding: 1.2rem;
                border-radius: 10px;
                border-left: 4px solid {COLORS['warning']};
                margin: 1rem 0;
            }}
            
            .success-box {{
                padding: 1.2rem;
                border-radius: 10px;
                border-left: 4px solid {COLORS['success']};
                margin: 1rem 0;
            }}
            
            /* ========== DIVIDERS ========== */
            .custom-divider {{
                height: 2px;
                margin: 2rem 0;
                border: none;
            }}
            
            /* ========== MÉTRICAS ========== */
            .stMetric {{
                padding: 1rem;
                border-radius: 8px;
                box-shadow: 0 2px 8px rgba(0,0,0,0.05);
            }}
            
            /* ========== DATAFRAMES ========== */
            .dataframe {{
                border-radius: 8px;
                overflow: hidden;
            }}
            
            /* ========== EXPANDERS ========== */
            .streamlit-expanderHeader {{
                background-color: {COLORS['light']};
                border-radius: 8px;
                font-weight: 600;
            }}
            
            /* ========== PROGRESS BAR ========== */
            .stProgress > div > div > div {{
            }}
        </style>
    """, unsafe_allow_html=True)


def criar_header(titulo: str, subtitulo: str = "") -> None:
    """
    Cria um cabeçalho visual padronizado.
    
    Args:
        titulo: Título principal
        subtitulo: Subtítulo opcional
    """
    if subtitulo:
        st.markdown(f"""
            <div class="page-header">
                <h1>{titulo}</h1>
                <p>{subtitulo}</p>
            </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown(f"""
            <div class="page-header">
                <h1>{titulo}</h1>
            </div>
        """, unsafe_allow_html=True)


def criar_card(conteudo: str) -> None:
    """
    Cria um card visual com conteúdo HTML.
    
    Args:
        conteudo: Conteúdo HTML do card
    """
    st.markdown(f"""
        <div class="custom-card">
            {conteudo}
        </div>
    """, unsafe_allow_html=True)


def criar_divider() -> None:
    """Adiciona um separador visual customizado."""
    st.markdown('<div class="custom-divider"></div>', unsafe_allow_html=True)


# ==============================
# FUNÇÕES DE VALIDAÇÃO
# ==============================

def validar_tamanho_arquivo(arquivo, tamanho_maximo_mb: int = MAX_FILE_SIZE_MB) -> bool:
    """
    Valida se o tamanho do arquivo está dentro do limite permitido.
    
    Args:
        arquivo: Arquivo do Streamlit file_uploader
        tamanho_maximo_mb: Tamanho máximo em MB
        
    Returns:
        bool: True se válido, False caso contrário
    """
    if arquivo.size > tamanho_maximo_mb * 1024 * 1024:
        st.error(f"❌ O arquivo **{arquivo.name}** excede {tamanho_maximo_mb}MB.")
        return False
    return True


def validar_colunas_df(df: pd.DataFrame, colunas_obrigatorias: list) -> Tuple[bool, list]:
    """
    Valida se o DataFrame contém as colunas obrigatórias.
    
    Args:
        df: DataFrame para validar
        colunas_obrigatorias: Lista de colunas obrigatórias
        
    Returns:
        Tuple[bool, list]: (válido, lista de colunas faltantes)
    """
    colunas_faltantes = [col for col in colunas_obrigatorias if col not in df.columns]
    return len(colunas_faltantes) == 0, colunas_faltantes


# ==============================
# FUNÇÕES DE VISUALIZAÇÃO
# ==============================

def exibir_metricas_arquivo(df: pd.DataFrame, nome_arquivo: str) -> None:
    """
    Exibe métricas básicas de um DataFrame em colunas.
    
    Args:
        df: DataFrame para exibir métricas
        nome_arquivo: Nome do arquivo
    """
    with st.expander(f"📊 Informações sobre {nome_arquivo}"):
        col1, col2, col3 = st.columns(3)
        col1.metric("📄 Linhas", f"{df.shape[0]:,}")
        col2.metric("📋 Colunas", f"{df.shape[1]:,}")
        col3.metric("💾 Memória", f"{df.memory_usage(deep=True).sum() / 1024:.1f} KB")


def exibir_preview(df: pd.DataFrame, titulo: str = "Prévia do Arquivo", linhas: int = 5) -> None:
    """
    Exibe uma prévia do DataFrame.
    
    Args:
        df: DataFrame para exibir
        titulo: Título da prévia
        linhas: Número de linhas a exibir
    """
    st.subheader(titulo)
    st.dataframe(df.head(linhas), use_container_width=True)


# ==============================
# FUNÇÕES DE DOWNLOAD
# ==============================

def criar_botao_download_excel(
    df: pd.DataFrame,
    nome_arquivo: str = "resultado.xlsx",
    sheet_name: str = "Dados"
) -> None:
    """
    Cria botão de download para arquivo Excel.
    
    Args:
        df: DataFrame para download
        nome_arquivo: Nome do arquivo de saída
        sheet_name: Nome da planilha
    """
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        df.to_excel(writer, index=False, sheet_name=sheet_name)
    output.seek(0)
    
    st.download_button(
        label="📥 Baixar Arquivo Excel",
        data=output,
        file_name=nome_arquivo,
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )


def criar_botao_download_csv(
    df: pd.DataFrame,
    nome_arquivo: str = "resultado.csv"
) -> None:
    """
    Cria botão de download para arquivo CSV.
    
    Args:
        df: DataFrame para download
        nome_arquivo: Nome do arquivo de saída
    """
    csv = df.to_csv(index=False).encode("utf-8")
    
    st.download_button(
        label="📥 Baixar Arquivo CSV",
        data=csv,
        file_name=nome_arquivo,
        mime="text/csv"
    )


def criar_botao_download_pdf(
    pdf_bytes: bytes,
    nome_arquivo: str = "resultado.pdf"
) -> None:
    """
    Cria botão de download para arquivo PDF.
    
    Args:
        pdf_bytes: Bytes do PDF
        nome_arquivo: Nome do arquivo de saída
    """
    st.download_button(
        label="📥 Baixar PDF",
        data=pdf_bytes,
        file_name=nome_arquivo,
        mime="application/pdf"
    )


# ==============================
# MENSAGENS PADRONIZADAS
# ==============================

def exibir_sucesso(mensagem: str) -> None:
    """Exibe mensagem de sucesso."""
    st.success(f"✅ {mensagem}")


def exibir_erro(mensagem: str) -> None:
    """Exibe mensagem de erro."""
    st.error(f"❌ {mensagem}")


def exibir_aviso(mensagem: str) -> None:
    """Exibe mensagem de aviso."""
    st.warning(f"⚠️ {mensagem}")


def exibir_info(mensagem: str) -> None:
    """Exibe mensagem informativa."""
    st.info(f"ℹ️ {mensagem}")


# ==============================
# FUNÇÕES DE LAYOUT
# ==============================

def criar_colunas(num_colunas: int = 2, espacamento: str = "medium") -> Tuple:
    """
    Cria layout de colunas com espaçamento customizável.
    
    Args:
        num_colunas: Número de colunas
        espacamento: 'small', 'medium' ou 'large'
        
    Returns:
        Tuple de colunas do Streamlit
    """
    gaps = {'small': [1]*num_colunas, 'medium': [2]*num_colunas, 'large': [3]*num_colunas}
    return st.columns(gaps.get(espacamento, [2]*num_colunas))


# ==============================
# UTILITÁRIOS DE CONVERSÃO
# ==============================

def converter_numero_brasileiro(valor) -> Optional[float]:
    """
    Converte números no formato brasileiro (47.764,00) para float.
    
    Args:
        valor: Valor a converter
        
    Returns:
        float ou None se conversão falhar
    """
    if pd.isna(valor):
        return None
    
    if isinstance(valor, (int, float)):
        return float(valor)
    
    try:
        valor = str(valor).strip()
        valor = valor.replace('.', '').replace(',', '.')
        return float(valor)
    except:
        return None


# ==============================
# FUNÇÕES DE PROGRESSO
# ==============================

def criar_barra_progresso(mensagem: str = "Processando..."):
    """
    Cria e retorna barra de progresso com mensagem.
    
    Args:
        mensagem: Mensagem a exibir
        
    Returns:
        Tuple[progress_bar, status_text]
    """
    status_text = st.empty()
    status_text.text(mensagem)
    progress_bar = st.progress(0)
    return progress_bar, status_text


def atualizar_progresso(progress_bar, status_text, progresso: float, mensagem: str):
    """
    Atualiza barra de progresso.
    
    Args:
        progress_bar: Objeto de barra de progresso
        status_text: Objeto de texto de status
        progresso: Valor entre 0 e 1
        mensagem: Mensagem a exibir
    """
    progress_bar.progress(progresso)
    status_text.text(mensagem)


def limpar_progresso(progress_bar, status_text):
    """
    Remove barra de progresso e status.
    
    Args:
        progress_bar: Objeto de barra de progresso
        status_text: Objeto de texto de status
    """
    progress_bar.empty()
    status_text.empty()