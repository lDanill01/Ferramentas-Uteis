"""
Sistema de União de Arquivos (PDF e Excel)
Página reorganizada com interface intuitiva
"""

import streamlit as st
import tempfile
import os
import PyPDF2
from streamlit_sortables import sort_items
import pandas as pd
import io

# Importar configurações
import sys
sys.path.append('..')
from config import configurar_pagina, aplicar_estilo_global, criar_header, criar_divider, criar_botao_download_excel, exibir_sucesso, exibir_erro

# Configuração da página
configurar_pagina("Unir Arquivos", "📁")
aplicar_estilo_global()

# Estilos adicionais
st.markdown("""
    <style>
    .feature-selector {
        padding: 2rem;
        border-radius: 12px;
        margin-bottom: 2rem;
        text-align: center;
    }
    
    .option-card {
        padding: 2rem;
        border-radius: 12px;
        transition: all 0.3s ease;
        cursor: pointer;
        height: 100%;
    }
    
    .option-card:hover {
        transform: translateY(-5px);
    }
    
    .option-card h3 {
        color:white;
        margin-bottom: 1rem;
    }
    
    .upload-zone {
        padding: 2rem;
        border-radius: 12px;
        border: 2px dashed #669eea;
        margin: 1.5rem 0;
    }
    
    .info-box {
        padding: 1.5rem;
        border-radius: 10px;
        margin: 1rem 0;
    }
    
    .info-box h4 {
        color: white;
        margin-bottom: 0.5rem;
    }
    
    .stats-container {
        display: flex;
        gap: 1rem;
        margin: 1rem 0;
    }
    
    .stat-box {
        padding: 1rem;
        border-radius: 8px;
        flex: 1;
        text-align: center;
    }
    </style>
""", unsafe_allow_html=True)

# Cabeçalho
criar_header("📁 Unir Arquivos", "Combine múltiplos PDFs ou consolide arquivos Excel")

# Inicializar session_state
if "tipo_uniao" not in st.session_state:
    st.session_state.tipo_uniao = None
if "resultado_excel" not in st.session_state:
    st.session_state.resultado_excel = None

# ========================================
# SELEÇÃO DO TIPO DE UNIÃO
# ========================================

st.markdown("### 🎯 Escolha o Tipo de União")

col1, col2 = st.columns(2)

with col1:
    if st.button("📄 Unir PDFs", use_container_width=True, type="primary" if st.session_state.tipo_uniao == "PDF" else "secondary"):
        st.session_state.tipo_uniao = "PDF"
        st.session_state.resultado_excel = None
        st.rerun()

with col2:
    if st.button("📊 Unir Arquivos Excel", use_container_width=True, type="primary" if st.session_state.tipo_uniao == "Excel" else "secondary"):
        st.session_state.tipo_uniao = "Excel"
        st.rerun()

criar_divider()

# ========================================
# UNIÃO DE PDFs
# ========================================

if st.session_state.tipo_uniao == "PDF":
    st.markdown("### 📄 União de Arquivos PDF")
    
    st.markdown("""
    <div class="info-box">
        <h4>📋 Como funciona:</h4>
        <ul>
            <li>✅ Faça upload de múltiplos arquivos PDF</li>
            <li>🔄 Arraste e solte para definir a ordem desejada</li>
            <li>📥 Baixe o PDF unificado final</li>
        </ul>
    </div>
    """, unsafe_allow_html=True)
    
    criar_divider()
    
    # Upload de PDFs
    st.markdown('<div class="upload-zone">', unsafe_allow_html=True)
    uploaded_files = st.file_uploader(
        "📤 Selecione os arquivos PDF para unir",
        type=["pdf"],
        accept_multiple_files=True,
        help="Você pode selecionar múltiplos arquivos PDF de uma vez"
    )
    st.markdown('</div>', unsafe_allow_html=True)
    
    if uploaded_files:
        st.success(f"✅ {len(uploaded_files)} arquivo(s) carregado(s)")
        
        # Exibir métricas dos arquivos
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("📄 Total de Arquivos", len(uploaded_files))
        with col2:
            total_size = sum(f.size for f in uploaded_files) / (1024 * 1024)
            st.metric("💾 Tamanho Total", f"{total_size:.2f} MB")
        with col3:
            st.metric("📊 Status", "Pronto para unir")
        
        criar_divider()
        
        with tempfile.TemporaryDirectory() as temp_dir:
            pdf_files = {}

            # Salvar arquivos temporariamente
            for uploaded_file in uploaded_files:
                file_path = os.path.join(temp_dir, uploaded_file.name)
                with open(file_path, "wb") as f:
                    f.write(uploaded_file.getvalue())
                pdf_files[uploaded_file.name] = file_path

            st.markdown("### 🔄 Defina a Ordem dos Arquivos")
            st.info("💡 Arraste os itens para cima ou para baixo para reordená-los")

            # Lista arrastável
            file_order = sort_items(
                list(pdf_files.keys()),
                direction="vertical",
                key="sortable_list"
            )
            
            criar_divider()

            if st.button("🔗 Unir PDFs", type="primary", use_container_width=True):
                try:
                    merger = PyPDF2.PdfMerger()
                    progress_bar = st.progress(0)
                    status_text = st.empty()

                    for i, filename in enumerate(file_order):
                        pdf_file = pdf_files[filename]
                        status_text.text(f"Processando {filename}...")
                        merger.append(pdf_file)
                        progress_bar.progress((i + 1) / len(file_order))

                    # Gerar arquivo final
                    output_path = os.path.join(temp_dir, "pdf_unificado.pdf")
                    merger.write(output_path)
                    merger.close()

                    # Preparar arquivo para download
                    with open(output_path, "rb") as f:
                        pdf_bytes = f.read()

                    st.success("✅ PDFs unidos com sucesso!")
                    
                    st.download_button(
                        label="📥 Baixar PDF Unificado",
                        data=pdf_bytes,
                        file_name="pdf_unificado.pdf",
                        mime="application/pdf",
                        use_container_width=True
                    )

                except Exception as e:
                    st.error(f"❌ Erro ao unir PDFs: {str(e)}")

                finally:
                    progress_bar.empty()
                    status_text.empty()

# ========================================
# UNIÃO DE ARQUIVOS EXCEL
# ========================================

elif st.session_state.tipo_uniao == "Excel":
    st.markdown("### 📊 União de Arquivos Excel")
    
    st.markdown("""
    <div class="info-box">
        <h4>📋 Como funciona:</h4>
        <ul>
            <li>✅ Faça upload de múltiplos arquivos Excel (.xlsx)</li>
            <li>🔍 O sistema valida se as colunas são compatíveis</li>
            <li>📊 Todos os arquivos são consolidados em um único</li>
            <li>📥 Baixe o arquivo Excel consolidado</li>
        </ul>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("""
    <div style="padding: 1rem; margin: 1rem 0;">
        <strong>⚠️ Requisitos Importantes:</strong>
        <ul>
            <li>Todos os arquivos devem ter as <strong>mesmas colunas</strong></li>
            <li>Os nomes das colunas devem ser <strong>idênticos</strong></li>
            <li>Tamanho máximo: <strong>5MB por arquivo</strong></li>
        </ul>
    </div>
    """, unsafe_allow_html=True)
    
    criar_divider()
    
    # Upload de arquivos
    st.markdown('<div class="upload-zone">', unsafe_allow_html=True)
    uploaded_files = st.file_uploader(
        "📤 Faça o upload de arquivos Excel",
        type=["xlsx"],
        accept_multiple_files=True,
        help="Selecione múltiplos arquivos Excel para consolidar"
    )
    st.markdown('</div>', unsafe_allow_html=True)

    if uploaded_files:
        st.success(f"✅ {len(uploaded_files)} arquivo(s) carregado(s)")
        
        # Métricas gerais
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("📄 Total de Arquivos", len(uploaded_files))
        with col2:
            total_size = sum(f.size for f in uploaded_files) / (1024 * 1024)
            st.metric("💾 Tamanho Total", f"{total_size:.2f} MB")
        with col3:
            st.metric("📊 Status", "Validando...")
        
        criar_divider()
        
        lista_df = []
        colunas_iguais = True
        colunas_referencia = None
        arquivos_processados = []
        arquivos_ignorados = []

        for file in uploaded_files:
            # Validação de tamanho
            if file.size > 5 * 1024 * 1024:
                st.error(f"❌ O arquivo **{file.name}** excede o limite de 5MB e não será processado.")
                arquivos_ignorados.append(file.name)
                continue
            
            try:
                df = pd.read_excel(file)
                
                # Verificação das colunas
                if colunas_referencia is None:     
                    colunas_referencia = df.columns
                elif not df.columns.equals(colunas_referencia):
                    colunas_iguais = False
                    st.error(f"❌ O arquivo **{file.name}** possui colunas diferentes e não será processado.")
                    arquivos_ignorados.append(file.name)
                    continue
                
                lista_df.append(df)
                arquivos_processados.append(file.name)

                # Exibir informações do arquivo
                with st.expander(f"📊 Informações de {file.name}"):
                    col1, col2, col3 = st.columns(3)
                    col1.metric("Linhas", f"{df.shape[0]:,}")
                    col2.metric("Colunas", f"{df.shape[1]:,}")
                    col3.metric("Memória", f"{df.memory_usage(deep=True).sum() / 1024:.1f} KB")
                    
                    if st.checkbox(f"Visualizar primeiras linhas de {file.name}", key=f"preview_{file.name}"):
                        st.dataframe(df.head(), use_container_width=True)
            
            except Exception as e:
                st.error(f"❌ Erro ao processar {file.name}: {str(e)}")
                arquivos_ignorados.append(file.name)

        criar_divider()
        
        # Resumo do processamento
        if arquivos_processados:
            st.markdown("### 📈 Resumo do Processamento")
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("""
                <div style="padding: 1rem;">
                    <strong>✅ Arquivos Processados:</strong>
                </div>
                """, unsafe_allow_html=True)
                for nome in arquivos_processados:
                    st.markdown(f"- {nome}")
            
            with col2:
                if arquivos_ignorados:
                    st.markdown("""
                    <div style="padding: 1rem;">
                        <strong>❌ Arquivos Ignorados:</strong>
                    </div>
                    """, unsafe_allow_html=True)
                    for nome in arquivos_ignorados:
                        st.markdown(f"- {nome}")
            
            criar_divider()

        # Se todas as colunas forem compatíveis
        if colunas_iguais and lista_df:
            percentual_realizado = len(lista_df) / len(uploaded_files) * 100
            
            st.info(f"✅ {len(lista_df)} de {len(uploaded_files)} arquivos prontos para consolidação ({percentual_realizado:.1f}%)")
            
            if st.button("🔗 Consolidar Arquivos", type="primary", use_container_width=True):
                try:
                    with st.spinner("Consolidando arquivos..."):
                        st.session_state.resultado_excel = pd.concat(lista_df, ignore_index=True)
                        st.success("✅ Arquivos consolidados com sucesso!")
                        st.rerun()
                except Exception as e:
                    st.error(f"❌ Erro na consolidação: {str(e)}")

    # Exibir resultado se já consolidado
    if st.session_state.resultado_excel is not None:
        criar_divider()
        
        st.markdown("### 📊 Resultado da Consolidação")
        
        resultado = st.session_state.resultado_excel
        
        # Estatísticas do consolidado
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("📄 Total de Linhas", f"{resultado.shape[0]:,}")
        with col2:
            st.metric("📋 Total de Colunas", f"{resultado.shape[1]:,}")
        with col3:
            st.metric("💾 Tamanho", f"{resultado.memory_usage(deep=True).sum() / 1024:.1f} KB")
        with col4:
            st.metric("✅ Status", "Concluído")
        
        criar_divider()
        
        # Preview do resultado
        if st.checkbox("👁️ Visualizar Arquivo Consolidado"):
            st.dataframe(resultado.head(20), use_container_width=True)
            
            with st.expander("📊 Estatísticas Descritivas"):
                st.dataframe(resultado.describe(), use_container_width=True)
        
        criar_divider()
        
        # Download
        st.markdown("### 📥 Download do Resultado")
        
        output = io.BytesIO()
        with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
            resultado.to_excel(writer, index=False, sheet_name="Consolidado")
        output.seek(0)

        st.download_button(
            label="📥 Baixar Arquivo Consolidado (.xlsx)",
            data=output,
            file_name="resultado_consolidado.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            use_container_width=True
        )
        
        # Botão para resetar
        if st.button("🔄 Nova Consolidação", use_container_width=True):
            st.session_state.resultado_excel = None
            st.rerun()

# ========================================
# PÁGINA INICIAL (SEM SELEÇÃO)
# ========================================

else:
    st.markdown("""
    <div style="text-align: center; padding: 3rem 0;">
        <h2>👆 Selecione uma opção acima para começar</h2>
        <p style="font-size: 1.1rem; margin-top: 1rem;">
            Escolha entre unir PDFs ou consolidar arquivos Excel
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    criar_divider()
    
    # Cards informativos
    col1, col2, col3 = st.columns([2,7,5])
    
    with col1:
        st.markdown("""
        <div class="option-card">
            <h3>📄 União de PDFs</h3>
            <p><strong>Use quando precisar:</strong></p>
            <ul style="text-align: left;">
                <li>Combinar múltiplos PDFs em um único arquivo</li>
                <li>Organizar ordem de documentos</li>
                <li>Criar compilações de relatórios</li>
                <li>Unificar documentos para impressão</li>
            </ul>
            <p style="margin-top: 1rem;"><strong>✅ Simples e Rápido</strong></p>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div class="option-card">
            <h3>📊 União de Excel</h3>
            <p><strong>Use quando precisar:</strong></p>
            <ul style="text-align: left;">
                <li>Consolidar múltiplas planilhas em uma</li>
                <li>Unir dados de diferentes departamentos</li>
                <li>Agregar relatórios periódicos</li>
                <li>Criar base de dados unificada</li>
            </ul>
            <p style="margin-top: 1rem;"><strong>✅ Validação Automática</strong></p>
        </div>
        """, unsafe_allow_html=True)
    with col3:
        st.markdown(
            """""", unsafe_allow_html=True
        )

# Footer
criar_divider()
st.markdown("""
<div style='text-align: center; color: #666; padding: 1rem 0;'>
    <p>📁 Sistema de União de Arquivos</p>
</div>
""", unsafe_allow_html=True)