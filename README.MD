# 🛠️ Ferramentas de Processamento Inteligente

![Python](https://img.shields.io/badge/Python-3.8%2B-blue)
![Streamlit](https://img.shields.io/badge/Streamlit-1.44.0-red)
![License](https://img.shields.io/badge/License-MIT-green)
![Status](https://img.shields.io/badge/Status-Ativo-success)

> **Plataforma completa de ferramentas para processamento, conversão e análise preditiva de arquivos**  
> Desenvolvido pelo Time de Business Intelligence

---

## 📋 Índice

- [Sobre o Projeto](#-sobre-o-projeto)
- [Funcionalidades](#-funcionalidades)
- [Tecnologias Utilizadas](#-tecnologias-utilizadas)
- [Estrutura do Projeto](#-estrutura-do-projeto)
- [Instalação](#-instalação)
- [Como Usar](#-como-usar)
- [Ferramentas Detalhadas](#-ferramentas-detalhadas)
- [Requisitos dos Arquivos](#-requisitos-dos-arquivos)
- [Troubleshooting](#-troubleshooting)
- [Contribuindo](#-contribuindo)
- [Licença](#-licença)

---

## 🎯 Sobre o Projeto

Este projeto oferece um conjunto completo de ferramentas web para automatizar tarefas rotineiras de processamento de dados e arquivos. Desenvolvido com **Streamlit**, proporciona uma interface moderna e intuitiva para operações que tradicionalmente exigiriam múltiplas ferramentas ou scripts complexos.

### 🌟 Diferenciais

- ✅ **Interface Intuitiva** - Design moderno e responsivo
- ✅ **Machine Learning** - Previsão de demanda com 6 algoritmos
- ✅ **Processamento Local** - Seus dados não saem do navegador
- ✅ **Multi-formato** - Suporte a Excel, PDF, CSV, imagens e texto
- ✅ **Zero Configuração** - Pronto para usar após instalação
- ✅ **Código Aberto** - Totalmente customizável

---

## 🚀 Funcionalidades

### 1️⃣ Previsão de Demanda com IA 🤖

Sistema completo de Machine Learning para previsão de séries temporais.

**Recursos:**
- 📊 6 algoritmos de ML (Linear Regression, Ridge, Lasso, Random Forest, Gradient Boosting, XGBoost)
- 📈 Análise automática de sazonalidade e tendências
- 🎯 Previsões futuras com intervalos de confiança (95%)
- 📉 Métricas detalhadas: MAE, RMSE, MAPE, R²
- 🔍 Feature importance e análise de resíduos
- 📥 Formato brasileiro: Ano | Mês | Volume

**Use Cases:**
- Planejamento de produção
- Gestão de estoque
- Forecasting de vendas
- Análise de demanda sazonal

---

### 2️⃣ União de Arquivos Excel 📂

Consolida múltiplos arquivos Excel em um único documento.

**Recursos:**
- 📑 Upload de múltiplos arquivos simultaneamente
- ✅ Validação automática de estrutura e colunas
- 📊 Estatísticas detalhadas do consolidado
- 💾 Download em formato .xlsx
- ⚡ Processamento otimizado para grandes volumes

**Use Cases:**
- Consolidação de relatórios mensais
- União de bases de diferentes departamentos
- Agregação de dados de filiais

---

### 3️⃣ União de PDFs 📄

Combina múltiplos PDFs em um único arquivo.

**Recursos:**
- 🔗 Upload de múltiplos PDFs
- ↕️ Sistema drag-and-drop para ordenação
- 🎨 Preservação de qualidade e formatação
- 📥 Download instantâneo do resultado

**Use Cases:**
- Unificação de relatórios
- Compilação de documentos
- Criação de manuais consolidados

---

### 4️⃣ Conversor Universal 🔄

Conversão entre múltiplos formatos de arquivo.

**Formatos Suportados:**
- 📄 **PDF** ↔ 🖼️ **Imagem** (PNG, JPEG)
- 📝 **Texto** → 📄 **PDF**
- 📝 **Texto** → 📐 **LaTeX**
- 🖼️ **Imagem** → 📄 **PDF**

**Recursos:**
- 🎯 Conversão em lote (múltiplos arquivos)
- ⚙️ Preservação de qualidade
- 💾 Download individual de cada resultado

**Use Cases:**
- Digitalização de documentos
- Preparação de apresentações
- Conversão para impressão

---

## 🛠️ Tecnologias Utilizadas

### Core
- **Python 3.8+** - Linguagem base
- **Streamlit 1.44.0** - Framework web
- **Pandas 2.2.3** - Manipulação de dados

### Machine Learning
- **scikit-learn** - Algoritmos de ML
- **XGBoost** - Gradient boosting otimizado
- **NumPy** - Computação numérica
- **SciPy** - Análise estatística

### Processamento de Arquivos
- **PyMuPDF 1.24.0** - Manipulação de PDFs
- **Pillow 11.1.0** - Processamento de imagens
- **ReportLab 4.1.0** - Geração de PDFs
- **XlsxWriter 3.2.0** - Criação de Excel

### Visualização
- **Plotly** - Gráficos interativos
- **Matplotlib** - Visualizações estáticas
- **Seaborn** - Gráficos estatísticos

---

## 📁 Estrutura do Projeto

```
Ferramentas/
│
├── Home.py                          # Página inicial
├── config.py                        # Configurações globais
├── requirements.txt                 # Dependências
├── .gitignore                       # Arquivos ignorados
├── README.md                        # Documentação
│
├── pages/                           # Páginas da aplicação
│   ├── 01_📈_Previsao_Demanda.py   # Sistema de ML
│   ├── 02_📁_Unir_Arquivos.py      # União Excel/PDF
│   └── 03_🔄_Conversor.py          # Conversor universal
│
├── .streamlit/                      # Configurações Streamlit
│   └── secrets.toml                 # Credenciais (NÃO versionar!)
│
└── data/                            # Dados (gitignored)
    ├── uploads/                     # Arquivos enviados
    ├── temp/                        # Temporários
    └── output/                      # Resultados
```

---

## 📦 Instalação

### Pré-requisitos

- Python 3.8 ou superior
- pip (gerenciador de pacotes)
- Git (opcional)

### Passo a Passo

#### 1. Clone o repositório (ou baixe o ZIP)

```bash
git clone https://github.com/seu-usuario/ferramentas-processamento.git
cd ferramentas-processamento
```

#### 2. Crie um ambiente virtual (recomendado)

**Windows:**
```bash
python -m venv venv
venv\Scripts\activate
```

**Linux/Mac:**
```bash
python3 -m venv venv
source venv/bin/activate
```

#### 3. Instale as dependências

```bash
pip install -r requirements.txt
```

#### 4. Execute a aplicação

```bash
streamlit run Home.py
```

#### 5. Acesse no navegador

A aplicação abrirá automaticamente em: `http://localhost:8501`

---

## 💻 Como Usar

### Início Rápido

1. **Execute a aplicação** com `streamlit run Home.py`
2. **Escolha a ferramenta** no menu lateral
3. **Faça upload** dos arquivos
4. **Configure** as opções (se necessário)
5. **Processe** e baixe o resultado

### Vídeo Tutorial

> 🎥 *Em breve: vídeo demonstrativo de cada ferramenta*

---

## 🔧 Ferramentas Detalhadas

### 📈 Previsão de Demanda

#### Formato de Dados Aceito

**Opção 1: Formato Brasileiro (recomendado)**
```
Ano    | Mês       | Volume (Toneladas)
2022   | janeiro   | 47.764,00
2022   | fevereiro | 49.651,43
2022   | março     | 59.543,25
```

**Opção 2: Formato Internacional**
```
Data        | Demanda
2022-01-01  | 47764.00
2022-02-01  | 49651.43
2022-03-01  | 59543.25
```

#### Algoritmos Disponíveis

| Modelo | Melhor Para | Velocidade | Precisão |
|--------|-------------|------------|----------|
| **Linear Regression** | Tendências lineares | ⚡⚡⚡ | ⭐⭐ |
| **Ridge** | Dados com colinearidade | ⚡⚡⚡ | ⭐⭐⭐ |
| **Lasso** | Seleção de features | ⚡⚡⚡ | ⭐⭐⭐ |
| **Random Forest** | Relações não-lineares | ⚡⚡ | ⭐⭐⭐⭐ |
| **Gradient Boosting** | Precisão máxima | ⚡ | ⭐⭐⭐⭐⭐ |
| **XGBoost** | Melhor performance | ⚡ | ⭐⭐⭐⭐⭐ |

#### Métricas de Avaliação

- **MAE** (Mean Absolute Error) - Erro médio absoluto
- **RMSE** (Root Mean Squared Error) - Penaliza erros grandes
- **MAPE** (Mean Absolute Percentage Error) - Erro percentual (%)
- **R²** (Coefficient of Determination) - Variância explicada (0-1)

**Interpretação do MAPE:**
- < 10% = Excelente
- 10-20% = Bom
- 20-50% = Razoável
- > 50% = Impreciso

#### Requisitos Mínimos

- ✅ Mínimo de **24 meses** de histórico (recomendado: 36+)
- ✅ Dados **mensais** consistentes (sem falhas)
- ✅ Valores **numéricos** válidos
- ✅ Sem outliers extremos (ou tratá-los antes)

---

### 📂 União de Arquivos Excel

#### Requisitos

- ✅ Todos os arquivos devem ter **mesmas colunas**
- ✅ Nomes de colunas **idênticos**
- ✅ Máximo **5MB por arquivo**
- ✅ Formato **.xlsx** (preferencialmente)

#### Validações Automáticas

- Verificação de estrutura
- Compatibilidade de colunas
- Detecção de duplicatas
- Contagem de registros

---

### 📄 União de PDFs

#### Recursos

- Upload de múltiplos PDFs simultaneamente
- Reordenação via drag-and-drop
- Preservação de bookmarks (se existentes)
- Manutenção de qualidade original

#### Limitações

- Máximo **10 PDFs** por vez
- Tamanho total máximo: **50MB**
- PDFs protegidos por senha não são suportados

---

### 🔄 Conversor Universal

#### Matriz de Conversão

| De ⬇️ / Para ➡️ | PDF | PNG | JPEG | TXT | TEX |
|-----------------|-----|-----|------|-----|-----|
| **PDF** | - | ✅ | ✅ | ✅ | ✅ |
| **PNG** | ✅ | - | ✅ | ❌ | ❌ |
| **JPEG** | ✅ | ✅ | - | ❌ | ❌ |
| **TXT** | ✅ | ❌ | ❌ | - | ✅ |

#### Configurações de Qualidade

**PDF → Imagem:**
- Resolução: 300 DPI (alta qualidade)
- Formato de cores: RGB

**Imagem → PDF:**
- Compressão: JPEG (qualidade 95%)
- Orientação: Automática

---

## 📋 Requisitos dos Arquivos

### Tamanhos Máximos

| Tipo | Limite | Observação |
|------|--------|------------|
| Excel | 5 MB | Por arquivo |
| PDF | 5 MB | Por arquivo |
| Imagem | 5 MB | Por arquivo |
| CSV | 5 MB | Por arquivo |
| Texto | 2 MB | Por arquivo |

### Formatos Suportados

**Leitura:**
- Excel: `.xlsx`, `.xls`
- PDF: `.pdf`
- Imagem: `.png`, `.jpg`, `.jpeg`
- Texto: `.txt`, `.csv`

**Exportação:**
- Excel: `.xlsx`
- PDF: `.pdf`
- Imagem: `.png`, `.jpeg`
- Texto: `.txt`, `.tex`

---

## 🐛 Troubleshooting

### Problemas Comuns

#### ❌ Erro: "Arquivo muito grande"
**Solução:** Reduza o tamanho do arquivo ou divida em partes menores.

#### ❌ Erro: "Colunas incompatíveis" (União Excel)
**Solução:** Certifique-se de que todos os arquivos têm exatamente as mesmas colunas.

#### ❌ Erro: "Dados insuficientes" (Previsão)
**Solução:** Forneça pelo menos 24 meses de dados históricos.

#### ❌ Erro: "Formato de data inválido"
**Solução:** Use o formato brasileiro (Ano | Mês | Volume) ou internacional (YYYY-MM-DD).

#### ❌ Erro: "ModuleNotFoundError"
**Solução:** Reinstale as dependências: `pip install -r requirements.txt`

#### ❌ App não abre no navegador
**Solução:** 
1. Verifique se a porta 8501 está livre
2. Tente: `streamlit run Home.py --server.port 8502`
3. Acesse manualmente: `http://localhost:8501`

---

## 🔐 Segurança e Privacidade

### Dados Locais

- ✅ Todo processamento é feito **localmente** no navegador
- ✅ Seus dados **não são enviados** para servidores externos
- ✅ Arquivos temporários são **automaticamente deletados**

### Boas Práticas

- 🔒 Nunca versione arquivos `.env` ou credenciais
- 🔒 Mantenha backups dos dados originais
- 🔒 Revise resultados antes de usar em produção
- 🔒 Use ambiente virtual para isolamento

---

## 🤝 Contribuindo

Contribuições são bem-vindas! Para contribuir:

1. Fork o projeto
2. Crie uma branch: `git checkout -b feature/nova-funcionalidade`
3. Commit suas mudanças: `git commit -m 'Adiciona nova funcionalidade'`
4. Push para a branch: `git push origin feature/nova-funcionalidade`
5. Abra um Pull Request

### Código de Conduta

- Seja respeitoso e profissional
- Documente suas mudanças
- Teste antes de submeter
- Siga o estilo de código existente

---

## 📞 Suporte

### Reportar Bugs

Encontrou um bug? Abra uma [issue](https://github.com/seu-usuario/ferramentas-processamento/issues) com:

- Descrição detalhada do problema
- Passos para reproduzir
- Screenshots (se aplicável)
- Mensagens de erro
- Sistema operacional e versão do Python

### Solicitação de Funcionalidades

Tem uma ideia? Compartilhe nas [discussions](https://github.com/seu-usuario/ferramentas-processamento/discussions)!

---

## 📄 Licença

Este projeto está sob a licença MIT. Veja o arquivo [LICENSE](LICENSE) para mais detalhes.

```
MIT License

Copyright (c) 2025 Time de Business Intelligence

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
```

---

## 🙏 Agradecimentos

- Time de Business Intelligence
- Comunidade Streamlit
- Contribuidores do projeto
- Usuários e testadores

---

## 📊 Estatísticas do Projeto

![GitHub Stars](https://img.shields.io/github/stars/seu-usuario/ferramentas-processamento?style=social)
![GitHub Forks](https://img.shields.io/github/forks/seu-usuario/ferramentas-processamento?style=social)
![GitHub Issues](https://img.shields.io/github/issues/seu-usuario/ferramentas-processamento)
![GitHub Contributors](https://img.shields.io/github/contributors/seu-usuario/ferramentas-processamento)

---

## 🗺️ Roadmap

### Em Desenvolvimento 🚧
- [ ] Sistema de autenticação
- [ ] Dashboard de métricas
- [ ] API REST

### Planejado 📅
- [ ] Suporte a mais formatos de arquivo
- [ ] Integração com bancos de dados
- [ ] Modo escuro
- [ ] Exportação para PowerPoint
- [ ] Scheduler de tarefas

### Futuro 🔮
- [ ] App mobile
- [ ] Integração com cloud storage
- [ ] Processamento em tempo real
- [ ] Multi-idioma

---

<div align="center">

**⭐ Se este projeto foi útil, considere dar uma estrela no GitHub!**

Desenvolvido com ❤️ pelo Time de BI

[Reportar Bug](https://github.com/seu-usuario/ferramentas-processamento/issues) · [Solicitar Feature](https://github.com/seu-usuario/ferramentas-processamento/issues) · [Documentação](https://github.com/seu-usuario/ferramentas-processamento/wiki)

</div># Ferramentas
