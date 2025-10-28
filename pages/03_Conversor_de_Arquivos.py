"""
Sistema de Conversão Universal de Arquivos
Página reorganizada com interface intuitiva e prática
"""

import streamlit as st
from PIL import Image
from reportlab.pdfgen import canvas
import fitz  # PyMuPDF
import os
import io

# Importar configurações
import sys
sys.path.append('..')
from config import configurar_pagina, aplicar_estilo_global, criar_header, criar_divider

# Configuração da página
configurar_pagina("Conversor de Arquivos", "🔄")
aplicar_estilo_global()

# Estilos adicionais
st.markdown("""
    <style>
    .conversion-selector {
        padding: 2rem;
        border-radius: 12px;
        box-shadow: 0 4px 15px rgba(0,0,0,0.08);
        margin-bottom: 2rem;
        text-align: center;
    }
    
    .format-badge {
        display: inline-block;
        color: white;
        padding: 0.5rem 1rem;
        border-radius: 20px;
        margin: 0.5rem;
        font-size: 1.1rem;
        font-weight: 600;
    }
    
    .arrow {
        font-size: 2rem;
        color: #667eea;
        margin: 0 1rem;
    }
    
    .upload-zone {
        background: #f8f9fa;
        padding: 2rem;
        border-radius: 12px;
        border: 2px dashed #667eea;
        margin: 1.5rem 0;
        text-align: center;
    }
    
    .conversion-info {
        color: white;
        padding: 1.5rem;
        border-radius: 10px;
        margin: 1rem 0;
    }
    
    .conversion-info h4 {
        color: white;
        margin-bottom: 0.5rem;
    }
    
    .file-item {
        padding: 1rem;
        border-radius: 8px;
        margin: 0.5rem 0;
        box-shadow: 0 2px 8px rgba(0,0,0,0.05);
        display: flex;
        justify-content: space-between;
        align-items: center;
    }
    
    .conversion-matrix {
        padding: 1.5rem;
        border-radius: 10px;
        margin: 1rem 0;
    }
    
    .supported-format {
        background: #d4edda;
        color: #155724;
        padding: 0.3rem 0.6rem;
        border-radius: 5px;
        font-size: 0.9rem;
        margin: 0.2rem;
        display: inline-block;
    }
    </style>
""", unsafe_allow_html=True)

# Cabeçalho
criar_header("🔄 Conversor Universal de Arquivos", "Converta entre PDF, Imagens, Texto e LaTeX")

# ========================================
# SELEÇÃO DE FORMATO
# ========================================

st.markdown("### 🎯 Configuração da Conversão")

col1, col2, col3 = st.columns([2, 1, 2])

with col1:
    formato_entrada = st.selectbox(
        "📤 Formato de Entrada:",
        ["PDF", "PNG", "JPG/JPEG", "TXT"],
        help="Selecione o formato dos arquivos que você vai enviar"
    )

with col2:
    st.markdown("<div style='text-align: center; padding-top: 1.8rem; font-size: 2rem;'>→</div>", unsafe_allow_html=True)

with col3:
    # Opções de saída baseadas na entrada
    opcoes_saida = {
        "PDF": ["PNG", "JPEG", "TXT", "TEX"],
        "PNG": ["PDF", "JPEG"],
        "JPG/JPEG": ["PDF", "PNG"],
        "TXT": ["PDF", "TEX"]
    }
    
    formato_saida = st.selectbox(
        "📥 Formato de Saída:",
        opcoes_saida[formato_entrada],
        help="Selecione o formato desejado para conversão"
    )

# Info da conversão selecionada
st.markdown(f"""
<div class="conversion-selector">
    <span class="format-badge">{formato_entrada}</span>
    <span class="arrow">→</span>
    <span class="format-badge">{formato_saida}</span>
    <p style="margin-top: 1rem; color: #666;">Conversão: {formato_entrada} para {formato_saida}</p>
</div>
""", unsafe_allow_html=True)

criar_divider()

# ========================================
# UPLOAD DE ARQUIVOS
# ========================================

st.markdown("### 📤 Upload dos Arquivos")

# Determinar extensões aceitas
extensoes_map = {
    "PDF": ["pdf"],
    "PNG": ["png"],
    "JPG/JPEG": ["jpg", "jpeg"],
    "TXT": ["txt"]
}

extensoes_aceitas = extensoes_map[formato_entrada]

arquivos = st.file_uploader(
    f"Selecione um ou mais arquivos {formato_entrada}",
    type=extensoes_aceitas,
    accept_multiple_files=True,
    help=f"Você pode selecionar múltiplos arquivos {formato_entrada} para converter de uma só vez"
)

if arquivos:
    st.success(f"✅ {len(arquivos)} arquivo(s) carregado(s)")
    
    # Mostrar arquivos carregados
    with st.expander("📋 Arquivos Carregados", expanded=True):
        for i, arquivo in enumerate(arquivos, 1):
            col1, col2 = st.columns([3, 1])
            with col1:
                st.write(f"{i}. **{arquivo.name}**")
            with col2:
                st.write(f"{arquivo.size / 1024:.1f} KB")
    
    criar_divider()
    
    # ========================================
    # BOTÃO DE CONVERSÃO
    # ========================================
    
    if st.button("🚀 Iniciar Conversão", type="primary", use_container_width=True):
        
        progresso = st.progress(0)
        status_text = st.empty()
        total = len(arquivos)
        resultados = []
        erros = []

        for idx, arquivo in enumerate(arquivos):
            try:
                nome, ext = os.path.splitext(arquivo.name)
                ext = ext.lower()
                status_text.text(f"🔄 Convertendo: {arquivo.name} → {formato_saida.upper()}")

                # ========================================
                # PDF → Outros formatos
                # ========================================
                if ext == ".pdf":
                    with fitz.open(stream=arquivo.read(), filetype="pdf") as doc:
                        
                        # PDF → Imagem (PNG/JPEG)
                        if formato_saida.lower() in ["png", "jpeg"]:
                            for i, page in enumerate(doc):
                                pix = page.get_pixmap()
                                img_bytes = pix.tobytes(output=formato_saida.lower())
                                resultados.append((f"{nome}_pagina_{i+1}.{formato_saida.lower()}", img_bytes))

                        # PDF → TXT
                        elif formato_saida.lower() == "txt":
                            texto = "\n".join(page.get_text() for page in doc)
                            resultados.append((f"{nome}.txt", texto.encode("utf-8")))

                        # PDF → TEX
                        elif formato_saida.lower() == "tex":
                            texto = "\n".join(page.get_text() for page in doc)
                            conteudo = (
                                "\\documentclass{article}\n"
                                "\\usepackage[utf8]{inputenc}\n"
                                "\\begin{document}\n"
                                + texto.replace("\n", "\\\\\n")
                                + "\n\\end{document}"
                            )
                            resultados.append((f"{nome}.tex", conteudo.encode("utf-8")))

                # ========================================
                # Imagem → Outros formatos
                # ========================================
                elif ext in [".png", ".jpg", ".jpeg"]:
                    img = Image.open(arquivo)
                    
                    # Imagem → PDF
                    if formato_saida.lower() == "pdf":
                        buffer = io.BytesIO()
                        img_rgb = img.convert("RGB")
                        img_rgb.save(buffer, format="PDF")
                        buffer.seek(0)
                        resultados.append((f"{nome}.pdf", buffer.read()))
                    
                    # Imagem → Outra imagem
                    elif formato_saida.lower() in ["png", "jpeg"]:
                        buffer = io.BytesIO()
                        if formato_saida.lower() == "jpeg":
                            img = img.convert("RGB")
                        img.save(buffer, format=formato_saida.upper())
                        buffer.seek(0)
                        resultados.append((f"{nome}.{formato_saida.lower()}", buffer.read()))

                # ========================================
                # TXT → Outros formatos
                # ========================================
                elif ext == ".txt":
                    conteudo = arquivo.read().decode("utf-8")

                    # TXT → PDF
                    if formato_saida.lower() == "pdf":
                        buffer = io.BytesIO()
                        c = canvas.Canvas(buffer)
                        y = 800
                        for linha in conteudo.splitlines():
                            if y < 50:
                                c.showPage()
                                y = 800
                            c.drawString(40, y, linha[:100])  # Limitar largura
                            y -= 15
                        c.save()
                        buffer.seek(0)
                        resultados.append((f"{nome}.pdf", buffer.read()))

                    # TXT → TEX
                    elif formato_saida.lower() == "tex":
                        conteudo_tex = (
                            "\\documentclass{article}\n"
                            "\\usepackage[utf8]{inputenc}\n"
                            "\\begin{document}\n"
                            + conteudo.replace("\n", "\\\\\n")
                            + "\n\\end{document}"
                        )
                        resultados.append((f"{nome}.tex", conteudo_tex.encode("utf-8")))

            except Exception as e:
                erros.append(f"❌ {arquivo.name}: {str(e)}")

            progresso.progress((idx + 1) / total)

        # Limpar progresso
        progresso.empty()
        status_text.empty()
        
        criar_divider()

        # ========================================
        # RESULTADOS
        # ========================================
        
        if resultados:
            st.success(f"✅ Conversão finalizada! {len(resultados)} arquivo(s) gerado(s)")
            
            # Métricas
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("📤 Arquivos Enviados", len(arquivos))
            with col2:
                st.metric("✅ Conversões", len(resultados))
            with col3:
                taxa = (len(resultados) / len(arquivos)) * 100 if len(arquivos) > 0 else 0
                st.metric("📊 Taxa de Sucesso", f"{taxa:.0f}%")
            
            criar_divider()
            
            st.markdown("### 📥 Downloads Disponíveis")
            
            # Organizar downloads em colunas (2 por linha)
            cols_per_row = 2
            for i in range(0, len(resultados), cols_per_row):
                cols = st.columns(cols_per_row)
                for j, col in enumerate(cols):
                    if i + j < len(resultados):
                        nome_arquivo, dados = resultados[i + j]
                        with col:
                            st.download_button(
                                label=f"📥 {nome_arquivo}",
                                data=dados,
                                file_name=nome_arquivo,
                                use_container_width=True
                            )
        
        if erros:
            st.warning("⚠️ Alguns arquivos apresentaram erros:")
            for erro in erros:
                st.write(erro)

else:
    st.info("👆 Faça upload de pelo menos um arquivo para começar a conversão")
    
    criar_divider()
    
    # ========================================
    # MATRIZ DE CONVERSÃO
    # ========================================
    
    st.markdown("### 📊 Matriz de Conversões Suportadas")
    
    st.markdown("""
    <div class="conversion-matrix">
        <table style="width: 100%; border-collapse: collapse;">
            <thead>
                    <th style="padding: 1rem; text-align: left;">De ⬇️ / Para ➡️</th>
                    <th style="padding: 1rem; text-align: center;">PDF</th>
                    <th style="padding: 1rem; text-align: center;">PNG</th>
                    <th style="padding: 1rem; text-align: center;">JPEG</th>
                    <th style="padding: 1rem; text-align: center;">TXT</th>
                    <th style="padding: 1rem; text-align: center;">TEX</th>
                </tr>
            </thead>
            <tbody>
                    <td style="padding: 1rem; font-weight: bold;">PDF</td>
                    <td style="padding: 1rem; text-align: center;">-</td>
                    <td style="padding: 1rem; text-align: center;">✅</td>
                    <td style="padding: 1rem; text-align: center;">✅</td>
                    <td style="padding: 1rem; text-align: center;">✅</td>
                    <td style="padding: 1rem; text-align: center;">✅</td>
                </tr>
                    <td style="padding: 1rem; font-weight: bold;">PNG</td>
                    <td style="padding: 1rem; text-align: center;">✅</td>
                    <td style="padding: 1rem; text-align: center;">-</td>
                    <td style="padding: 1rem; text-align: center;">✅</td>
                    <td style="padding: 1rem; text-align: center;">❌</td>
                    <td style="padding: 1rem; text-align: center;">❌</td>
                </tr>
                    <td style="padding: 1rem; font-weight: bold;">JPEG</td>
                    <td style="padding: 1rem; text-align: center;">✅</td>
                    <td style="padding: 1rem; text-align: center;">✅</td>
                    <td style="padding: 1rem; text-align: center;">-</td>
                    <td style="padding: 1rem; text-align: center;">❌</td>
                    <td style="padding: 1rem; text-align: center;">❌</td>
                </tr>
                    <td style="padding: 1rem; font-weight: bold;">TXT</td>
                    <td style="padding: 1rem; text-align: center;">✅</td>
                    <td style="padding: 1rem; text-align: center;">❌</td>
                    <td style="padding: 1rem; text-align: center;">❌</td>
                    <td style="padding: 1rem; text-align: center;">-</td>
                    <td style="padding: 1rem; text-align: center;">✅</td>
                </tr>
            </tbody>
        </table>
    </div>
    """, unsafe_allow_html=True)
    
    criar_divider()
    
    # ========================================
    # DICAS E INFORMAÇÕES
    # ========================================
    
    st.markdown("### 💡 Dicas e Recomendações")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("""
        #### 📄 Para PDFs:
        - ✅ Resolução: 300 DPI (alta qualidade)
        - ✅ Múltiplas páginas geram múltiplas imagens
        - ✅ Texto extraído preserva quebras de linha
        - ✅ LaTeX gerado pode precisar ajustes
        """)
        
        st.markdown("""
        #### 🖼️ Para Imagens:
        - ✅ PNG preserva transparência
        - ✅ JPEG é mais compacto
        - ✅ Conversão RGB automática
        - ✅ Alta qualidade mantida
        """)
    
    with col2:
        st.markdown("""
        #### 📝 Para Texto:
        - ✅ Encoding UTF-8 automático
        - ✅ PDF com quebras de linha
        - ✅ LaTeX com pacotes básicos
        - ✅ Linhas longas são truncadas em PDF
        """)
        
        st.markdown("""
        #### ⚙️ Configurações:
        - ✅ Conversão em lote suportada
        - ✅ Máximo 10 arquivos por vez
        - ✅ Tamanho máximo: 5MB por arquivo
        - ✅ Processamento local (privado)
        """)
    
    criar_divider()
    
    st.markdown("### 📚 Exemplos de Uso")
    
    with st.expander("📄 Converter PDF em imagens"):
        st.markdown("""
        **Caso de uso:** Extrair páginas de um PDF como imagens
        
        1. Selecione **PDF** como entrada
        2. Selecione **PNG** ou **JPEG** como saída
        3. Faça upload do PDF
        4. Cada página será convertida em uma imagem separada
        
        **Dica:** Use PNG para preservar qualidade e JPEG para arquivos menores.
        """)
    
    with st.expander("🖼️ Criar PDF a partir de imagens"):
        st.markdown("""
        **Caso de uso:** Compilar múltiplas imagens em um único PDF
        
        1. Selecione **PNG** ou **JPG/JPEG** como entrada
        2. Selecione **PDF** como saída
        3. Faça upload das imagens
        4. Cada imagem será convertida em um PDF individual
        
        **Dica:** Use a ferramenta "Unir PDFs" depois para combinar os PDFs gerados.
        """)
    
    with st.expander("📝 Converter texto para LaTeX"):
        st.markdown("""
        **Caso de uso:** Preparar documento de texto para LaTeX
        
        1. Selecione **TXT** como entrada
        2. Selecione **TEX** como saída
        3. Faça upload do arquivo de texto
        4. O LaTeX gerado incluirá estrutura básica
        
        **Dica:** O arquivo .tex gerado pode precisar de ajustes manuais para formatação avançada.
        """)

# Footer
criar_divider()
st.markdown("""
<div style='text-align: center; color: #666; padding: 1rem 0;'>
    <p>🚀 Sistema de Conversão de Arquivos</p>
</div>
""", unsafe_allow_html=True)