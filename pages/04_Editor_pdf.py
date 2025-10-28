"""
Editor de PDF Online
Página para edição avançada de arquivos PDF
"""

import streamlit as st
import PyPDF2
from PyPDF2 import PdfReader, PdfWriter
import fitz  # PyMuPDF
import io
from PIL import Image
import tempfile
import os

# Importar configurações
import sys
sys.path.append('..')
from config import configurar_pagina, aplicar_estilo_global, criar_header, criar_divider

# Configuração da página
configurar_pagina("Editor de PDF", "📄")
aplicar_estilo_global()

# Estilos adicionais
st.markdown("""
    <style>
    .editor-section {
        padding: 2rem;
        border-radius: 12px;
        margin-bottom: 2rem;
    }
    
    .operation-card {
        padding: 1.5rem;
        border-radius: 10px;
        margin: 1rem 0;
        transition: all 0.3s ease;
        cursor: pointer;
    }
    
    .operation-card:hover {
        transform: translateY(-3px);
        box-shadow: 0 6px 20px rgba(0,0,0,0.12);
    }
    
    .operation-card h4 {
        color: white;
        margin-bottom: 0.5rem;
    }
    
    .page-preview {
        border: 2px solid #667eea;
        border-radius: 8px;
        padding: 0.5rem;
        margin: 0.5rem;
        text-align: center;
        background: white;
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
    </style>
""", unsafe_allow_html=True)

# Cabeçalho
criar_header("📄 Editor de PDF Online", "Edite seus PDFs sem software externo")

# Inicializar session_state
if 'pdf_carregado' not in st.session_state:
    st.session_state.pdf_carregado = None
if 'pdf_info' not in st.session_state:
    st.session_state.pdf_info = None
if 'operacao_selecionada' not in st.session_state:
    st.session_state.operacao_selecionada = None

# ========================================
# UPLOAD DE PDF
# ========================================

st.markdown("### 📤 Upload do Arquivo PDF")

arquivo_pdf = st.file_uploader(
    "Selecione o arquivo PDF para editar",
    type=["pdf"],
    help="Faça upload do PDF que você deseja editar"
)

if arquivo_pdf:
    if st.session_state.pdf_carregado != arquivo_pdf.name:
        st.session_state.pdf_carregado = arquivo_pdf.name
        
        # Carregar informações do PDF
        try:
            pdf_reader = PdfReader(arquivo_pdf)
            num_pages = len(pdf_reader.pages)
            
            # Obter metadados
            metadata = pdf_reader.metadata if pdf_reader.metadata else {}
            
            st.session_state.pdf_info = {
                'nome': arquivo_pdf.name,
                'paginas': num_pages,
                'tamanho': arquivo_pdf.size / 1024,  # KB
                'metadata': metadata,
                'conteudo': arquivo_pdf.getvalue()
            }
            
            st.success(f"✅ PDF carregado: {arquivo_pdf.name}")
            
        except Exception as e:
            st.error(f"❌ Erro ao carregar PDF: {str(e)}")
            st.session_state.pdf_carregado = None

if st.session_state.pdf_info:
    criar_divider()
    
    # Informações do PDF
    st.markdown("### 📊 Informações do Arquivo")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("📄 Páginas", st.session_state.pdf_info['paginas'])
    with col2:
        st.metric("💾 Tamanho", f"{st.session_state.pdf_info['tamanho']:.1f} KB")
    with col3:
        st.metric("📝 Nome", st.session_state.pdf_info['nome'][:15] + "...")
    with col4:
        st.metric("✅ Status", "Carregado")
    
    criar_divider()
    
    # ========================================
    # SELEÇÃO DE OPERAÇÃO
    # ========================================
    
    st.markdown("### 🎯 Selecione a Operação")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("✂️ Extrair Páginas", use_container_width=True, 
                    type="primary" if st.session_state.operacao_selecionada == "extrair" else "secondary"):
            st.session_state.operacao_selecionada = "extrair"
            st.rerun()
        
        if st.button("🔄 Reordenar Páginas", use_container_width=True,
                    type="primary" if st.session_state.operacao_selecionada == "reordenar" else "secondary"):
            st.session_state.operacao_selecionada = "reordenar"
            st.rerun()
    
    with col2:
        if st.button("🗑️ Remover Páginas", use_container_width=True,
                    type="primary" if st.session_state.operacao_selecionada == "remover" else "secondary"):
            st.session_state.operacao_selecionada = "remover"
            st.rerun()
        
        if st.button("🔄 Rotacionar Páginas", use_container_width=True,
                    type="primary" if st.session_state.operacao_selecionada == "rotacionar" else "secondary"):
            st.session_state.operacao_selecionada = "rotacionar"
            st.rerun()
    
    with col3:
        if st.button("🔐 Adicionar Senha", use_container_width=True,
                    type="primary" if st.session_state.operacao_selecionada == "senha" else "secondary"):
            st.session_state.operacao_selecionada = "senha"
            st.rerun()
        
        if st.button("🖼️ Extrair Imagens", use_container_width=True,
                    type="primary" if st.session_state.operacao_selecionada == "imagens" else "secondary"):
            st.session_state.operacao_selecionada = "imagens"
            st.rerun()
    
    criar_divider()
    
    # ========================================
    # OPERAÇÕES
    # ========================================
    
    if st.session_state.operacao_selecionada == "extrair":
        st.markdown("### ✂️ Extrair Páginas Específicas")
        
        st.info("💡 Selecione as páginas que você deseja extrair do PDF")
        
        col1, col2 = st.columns([2, 1])
        
        with col1:
            paginas_extrair = st.text_input(
                "Páginas para extrair",
                placeholder="Ex: 1,3,5-10,15",
                help="Use vírgulas para separar páginas individuais e hífen para intervalos"
            )
        
        with col2:
            st.markdown("<br>", unsafe_allow_html=True)
            if st.button("✂️ Extrair", use_container_width=True, type="primary"):
                if paginas_extrair:
                    try:
                        # Processar string de páginas
                        paginas = []
                        for parte in paginas_extrair.split(','):
                            if '-' in parte:
                                inicio, fim = map(int, parte.split('-'))
                                paginas.extend(range(inicio - 1, fim))
                            else:
                                paginas.append(int(parte) - 1)
                        
                        # Validar páginas
                        max_pag = st.session_state.pdf_info['paginas']
                        paginas = [p for p in paginas if 0 <= p < max_pag]
                        
                        if not paginas:
                            st.error("❌ Nenhuma página válida selecionada")
                        else:
                            # Extrair páginas
                            pdf_reader = PdfReader(io.BytesIO(st.session_state.pdf_info['conteudo']))
                            pdf_writer = PdfWriter()
                            
                            for pag in sorted(set(paginas)):
                                pdf_writer.add_page(pdf_reader.pages[pag])
                            
                            # Salvar resultado
                            output = io.BytesIO()
                            pdf_writer.write(output)
                            output.seek(0)
                            
                            st.success(f"✅ {len(set(paginas))} página(s) extraída(s) com sucesso!")
                            
                            st.download_button(
                                label="📥 Baixar PDF Extraído",
                                data=output,
                                file_name=f"extraido_{st.session_state.pdf_info['nome']}",
                                mime="application/pdf",
                                use_container_width=True
                            )
                    
                    except Exception as e:
                        st.error(f"❌ Erro ao extrair páginas: {str(e)}")
                else:
                    st.warning("⚠️ Digite as páginas que deseja extrair")
    
    elif st.session_state.operacao_selecionada == "reordenar":
        st.markdown("### 🔄 Reordenar Páginas")
        
        st.info("💡 Digite a nova ordem das páginas")
        
        col1, col2 = st.columns([2, 1])
        
        with col1:
            ordem_paginas = st.text_input(
                "Nova ordem das páginas",
                placeholder=f"Ex: 3,1,2,4 (total: {st.session_state.pdf_info['paginas']} páginas)",
                help="Insira a ordem desejada separada por vírgulas"
            )
        
        with col2:
            st.markdown("<br>", unsafe_allow_html=True)
            if st.button("🔄 Reordenar", use_container_width=True, type="primary"):
                if ordem_paginas:
                    try:
                        # Processar ordem
                        ordem = [int(p.strip()) - 1 for p in ordem_paginas.split(',')]
                        
                        # Validar
                        max_pag = st.session_state.pdf_info['paginas']
                        if any(p < 0 or p >= max_pag for p in ordem):
                            st.error(f"❌ Página(s) inválida(s). Use páginas de 1 a {max_pag}")
                        else:
                            # Reordenar
                            pdf_reader = PdfReader(io.BytesIO(st.session_state.pdf_info['conteudo']))
                            pdf_writer = PdfWriter()
                            
                            for pag in ordem:
                                pdf_writer.add_page(pdf_reader.pages[pag])
                            
                            # Salvar
                            output = io.BytesIO()
                            pdf_writer.write(output)
                            output.seek(0)
                            
                            st.success("✅ Páginas reordenadas com sucesso!")
                            
                            st.download_button(
                                label="📥 Baixar PDF Reordenado",
                                data=output,
                                file_name=f"reordenado_{st.session_state.pdf_info['nome']}",
                                mime="application/pdf",
                                use_container_width=True
                            )
                    
                    except Exception as e:
                        st.error(f"❌ Erro ao reordenar: {str(e)}")
                else:
                    st.warning("⚠️ Digite a nova ordem das páginas")
    
    elif st.session_state.operacao_selecionada == "remover":
        st.markdown("### 🗑️ Remover Páginas")
        
        st.info("💡 Selecione as páginas que você deseja remover")
        
        col1, col2 = st.columns([2, 1])
        
        with col1:
            paginas_remover = st.text_input(
                "Páginas para remover",
                placeholder="Ex: 2,4,7-9",
                help="Use vírgulas para separar e hífen para intervalos"
            )
        
        with col2:
            st.markdown("<br>", unsafe_allow_html=True)
            if st.button("🗑️ Remover", use_container_width=True, type="primary"):
                if paginas_remover:
                    try:
                        # Processar páginas
                        paginas = []
                        for parte in paginas_remover.split(','):
                            if '-' in parte:
                                inicio, fim = map(int, parte.split('-'))
                                paginas.extend(range(inicio - 1, fim))
                            else:
                                paginas.append(int(parte) - 1)
                        
                        # Remover
                        pdf_reader = PdfReader(io.BytesIO(st.session_state.pdf_info['conteudo']))
                        pdf_writer = PdfWriter()
                        
                        max_pag = len(pdf_reader.pages)
                        for i in range(max_pag):
                            if i not in paginas:
                                pdf_writer.add_page(pdf_reader.pages[i])
                        
                        if len(pdf_writer.pages) == 0:
                            st.error("❌ Não é possível remover todas as páginas")
                        else:
                            output = io.BytesIO()
                            pdf_writer.write(output)
                            output.seek(0)
                            
                            st.success(f"✅ {len(paginas)} página(s) removida(s). {len(pdf_writer.pages)} página(s) restante(s)")
                            
                            st.download_button(
                                label="📥 Baixar PDF Modificado",
                                data=output,
                                file_name=f"modificado_{st.session_state.pdf_info['nome']}",
                                mime="application/pdf",
                                use_container_width=True
                            )
                    
                    except Exception as e:
                        st.error(f"❌ Erro ao remover páginas: {str(e)}")
                else:
                    st.warning("⚠️ Digite as páginas que deseja remover")
    
    elif st.session_state.operacao_selecionada == "rotacionar":
        st.markdown("### 🔄 Rotacionar Páginas")
        
        st.info("💡 Selecione o ângulo de rotação e as páginas")
        
        col1, col2, col3 = st.columns([1, 2, 1])
        
        with col1:
            angulo = st.selectbox(
                "Ângulo de rotação",
                [90, 180, 270],
                help="Selecione o ângulo de rotação"
            )
        
        with col2:
            paginas_rotacionar = st.text_input(
                "Páginas para rotacionar",
                placeholder=f"Ex: 1-{st.session_state.pdf_info['paginas']} (todas)",
                help="Deixe em branco para rotacionar todas"
            )
        
        with col3:
            st.markdown("<br>", unsafe_allow_html=True)
            if st.button("🔄 Rotacionar", use_container_width=True, type="primary"):
                try:
                    pdf_reader = PdfReader(io.BytesIO(st.session_state.pdf_info['conteudo']))
                    pdf_writer = PdfWriter()
                    
                    # Determinar páginas
                    if not paginas_rotacionar:
                        paginas = list(range(len(pdf_reader.pages)))
                    else:
                        paginas = []
                        for parte in paginas_rotacionar.split(','):
                            if '-' in parte:
                                inicio, fim = map(int, parte.split('-'))
                                paginas.extend(range(inicio - 1, fim))
                            else:
                                paginas.append(int(parte) - 1)
                    
                    # Rotacionar
                    for i in range(len(pdf_reader.pages)):
                        page = pdf_reader.pages[i]
                        if i in paginas:
                            page.rotate(angulo)
                        pdf_writer.add_page(page)
                    
                    output = io.BytesIO()
                    pdf_writer.write(output)
                    output.seek(0)
                    
                    st.success(f"✅ Páginas rotacionadas em {angulo}°")
                    
                    st.download_button(
                        label="📥 Baixar PDF Rotacionado",
                        data=output,
                        file_name=f"rotacionado_{st.session_state.pdf_info['nome']}",
                        mime="application/pdf",
                        use_container_width=True
                    )
                
                except Exception as e:
                    st.error(f"❌ Erro ao rotacionar: {str(e)}")
    
    elif st.session_state.operacao_selecionada == "senha":
        st.markdown("### 🔐 Adicionar/Remover Senha")
        
        tab1, tab2 = st.tabs(["🔐 Adicionar Senha", "🔓 Remover Senha"])
        
        with tab1:
            st.info("💡 Proteja seu PDF com senha")
            
            col1, col2 = st.columns([2, 1])
            
            with col1:
                senha = st.text_input(
                    "Digite a senha",
                    type="password",
                    help="Senha para proteger o PDF"
                )
            
            with col2:
                st.markdown("<br>", unsafe_allow_html=True)
                if st.button("🔐 Proteger", use_container_width=True, type="primary"):
                    if senha:
                        try:
                            pdf_reader = PdfReader(io.BytesIO(st.session_state.pdf_info['conteudo']))
                            pdf_writer = PdfWriter()
                            
                            for page in pdf_reader.pages:
                                pdf_writer.add_page(page)
                            
                            pdf_writer.encrypt(senha)
                            
                            output = io.BytesIO()
                            pdf_writer.write(output)
                            output.seek(0)
                            
                            st.success("✅ PDF protegido com senha!")
                            
                            st.download_button(
                                label="📥 Baixar PDF Protegido",
                                data=output,
                                file_name=f"protegido_{st.session_state.pdf_info['nome']}",
                                mime="application/pdf",
                                use_container_width=True
                            )
                        
                        except Exception as e:
                            st.error(f"❌ Erro ao adicionar senha: {str(e)}")
                    else:
                        st.warning("⚠️ Digite uma senha")
        
        with tab2:
            st.info("💡 Remova a proteção por senha do PDF")
            
            col1, col2 = st.columns([2, 1])
            
            with col1:
                senha_remover = st.text_input(
                    "Senha atual do PDF",
                    type="password",
                    help="Digite a senha atual para desbloquear"
                )
            
            with col2:
                st.markdown("<br>", unsafe_allow_html=True)
                if st.button("🔓 Desbloquear", use_container_width=True, type="primary"):
                    if senha_remover:
                        try:
                            pdf_reader = PdfReader(io.BytesIO(st.session_state.pdf_info['conteudo']))
                            
                            if pdf_reader.is_encrypted:
                                if pdf_reader.decrypt(senha_remover):
                                    pdf_writer = PdfWriter()
                                    
                                    for page in pdf_reader.pages:
                                        pdf_writer.add_page(page)
                                    
                                    output = io.BytesIO()
                                    pdf_writer.write(output)
                                    output.seek(0)
                                    
                                    st.success("✅ Senha removida com sucesso!")
                                    
                                    st.download_button(
                                        label="📥 Baixar PDF Desbloqueado",
                                        data=output,
                                        file_name=f"desbloqueado_{st.session_state.pdf_info['nome']}",
                                        mime="application/pdf",
                                        use_container_width=True
                                    )
                                else:
                                    st.error("❌ Senha incorreta")
                            else:
                                st.warning("⚠️ Este PDF não está protegido por senha")
                        
                        except Exception as e:
                            st.error(f"❌ Erro: {str(e)}")
                    else:
                        st.warning("⚠️ Digite a senha")
    
    elif st.session_state.operacao_selecionada == "imagens":
        st.markdown("### 🖼️ Extrair Imagens do PDF")
        
        st.info("💡 Todas as imagens do PDF serão extraídas")
        
        if st.button("🖼️ Extrair Imagens", use_container_width=True, type="primary"):
            try:
                with st.spinner("Extraindo imagens..."):
                    doc = fitz.open(stream=st.session_state.pdf_info['conteudo'], filetype="pdf")
                    
                    imagens_extraidas = []
                    
                    for page_num in range(len(doc)):
                        page = doc[page_num]
                        image_list = page.get_images()
                        
                        for img_index, img in enumerate(image_list):
                            xref = img[0]
                            base_image = doc.extract_image(xref)
                            image_bytes = base_image["image"]
                            
                            imagens_extraidas.append({
                                'nome': f"pagina_{page_num + 1}_img_{img_index + 1}.png",
                                'dados': image_bytes
                            })
                    
                    if imagens_extraidas:
                        st.success(f"✅ {len(imagens_extraidas)} imagem(ns) extraída(s)!")
                        
                        # Exibir preview
                        st.markdown("### 🖼️ Preview das Imagens")
                        
                        cols = st.columns(3)
                        for idx, img_data in enumerate(imagens_extraidas[:9]):  # Mostrar até 9
                            with cols[idx % 3]:
                                img = Image.open(io.BytesIO(img_data['dados']))
                                st.image(img, caption=img_data['nome'], use_container_width=True)
                        
                        if len(imagens_extraidas) > 9:
                            st.info(f"Mostrando 9 de {len(imagens_extraidas)} imagens")
                        
                        criar_divider()
                        
                        # Downloads
                        st.markdown("### 📥 Download das Imagens")
                        
                        for img_data in imagens_extraidas:
                            st.download_button(
                                label=f"📥 {img_data['nome']}",
                                data=img_data['dados'],
                                file_name=img_data['nome'],
                                mime="image/png"
                            )
                    else:
                        st.warning("⚠️ Nenhuma imagem encontrada no PDF")
            
            except Exception as e:
                st.error(f"❌ Erro ao extrair imagens: {str(e)}")

else:
    st.info("👆 Faça upload de um arquivo PDF para começar")
    
    criar_divider()
    
    # Informações sobre funcionalidades
    st.markdown("### 💡 Funcionalidades Disponíveis")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("""
        #### ✂️ Extrair Páginas
        - Selecione páginas específicas
        - Suporta intervalos (ex: 5-10)
        - Gera novo PDF com páginas selecionadas
        """)
        
        st.markdown("""
        #### 🔄 Reordenar
        - Reorganize páginas livremente
        - Nova ordem personalizada
        - Mantém qualidade original
        """)
    
    with col2:
        st.markdown("""
        #### 🗑️ Remover Páginas
        - Delete páginas indesejadas
        - Suporta múltiplas seleções
        - PDF limpo e otimizado
        """)
        
        st.markdown("""
        #### 🔄 Rotacionar
        - Rotação em 90°, 180° ou 270°
        - Aplique em páginas específicas
        - Correção de orientação
        """)
    
    with col3:
        st.markdown("""
        #### 🔐 Proteger com Senha
        - Adicione senha de segurança
        - Remova senha existente
        - Proteção de conteúdo
        """)
        
        st.markdown("""
        #### 🖼️ Extrair Imagens
        - Todas as imagens do PDF
        - Download individual
        - Formato PNG
        """)

# Footer
criar_divider()
st.markdown("""
<div style='text-align: center; color: #666; padding: 1rem 0;'>
    <p>📄 Editor de PDF Online | Edição Completa e Segura</p>
</div>
""", unsafe_allow_html=True)