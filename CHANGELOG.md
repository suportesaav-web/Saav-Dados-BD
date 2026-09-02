# 📜 Registro de Mudanças (Changelog)

Todas as alterações notáveis no projeto **The Nehemizer** serão documentadas neste arquivo.

O formato é baseado em [Keep a Changelog](https://keepachangelog.com/pt-BR/1.0.0/), e este projeto adere ao [Semantic Versioning](https://semver.org/lang/pt-BR/).

## [1.3.0] - 2026-09-02

### 💰 Inteligência Financeira & Gestão de Margem
- **Cálculo de Margem Bruta e % Margem:** Incorporação de cálculo de margem e spread financeiro na Aba RESUMO do Excel e no painel executivo da aplicação.
- **Linha de Fechamento Consolidada:** Adição de `TOTAL GERAL CONSOLIDADO` com destaque corporativo na planilha Excel gerada via `XlsxWriter`.
- **Margem Dinâmica na Prévia:** A grade interativa agora calcula a margem bruta estimada em tempo real conforme o analista preenche ou ajusta preços de compra.

### 🔄 Confiabilidade & Reatividade da Sessão
- **Assinatura Combinada de Arquivos (`gerar_assinatura_arquivos`):** Detecção automática de alterações em qualquer arquivo (Vendas, PDFs de contratos ou Tabela Normal), permitindo reprocessamento instantâneo sem necessidade de recarregar a planilha de vendas.
- **Invalidação Segura de Cache:** Limpeza proativa de downloads prévios ao trocar arquivos, prevenindo inconsistência documental.

### 🧪 Qualidade de Código & Testes Automatizados
- **Suíte de Testes Unitários (`tests/`):** 13 testes automatizados cobrindo identificação de clientes/CNPJs, normalização de colunas, Regra Suprema de Contingência e integridade da geração do Excel.

---

## [1.2.1] - 2026-09-02

### 📚 Documentação & Governança
- **Reestruturação do README em 4 Camadas:** Divisão limpa em Resumo Executivo, Como Funciona, Regras de Negócio e Documentação Técnica.
- **Seção "Antes x Depois":** Comparativo de impacto de negócio no topo do README entre processo manual anterior e a solução automatizada.
- **Documento Dedicado de Regras:** Criação do [`docs/regras-negocio.md`](docs/regras-negocio.md) contendo os de-paras detalhados de instituições e contratos, preservando o README limpo e desacoplado.

### ⚙️ Engenharia & Refatoração
- **Centralização de Clientes e Contratos:** Criação da estrutura `CLIENTES_CONFIG` em [`src/config/settings.py`](src/config/settings.py) e refatoração de `agrupar_cliente` em [`src/services/pdf_service.py`](src/services/pdf_service.py), eliminando termos e CNPJs *hardcoded* espalhados.

---

## [1.2.0] - 2026-08-31

### 🎨 Identidade Visual & Design Corporativo Saavedra
- **Paleta Oficial Saavedra:** Adoção estrita das cores institucionais Laranja (`#DC4405`), Vermelho (`#DA291C`) e Grafite/Preto (`#25282A`) com fundos suaves neutros (`#F8F9FA`).
- **Design Sóbrio e Profissional:** Remoção de elementos informais (emojis de instrumentos e balões decorativos) e substituição por confirmações corporativas sutis (`st.toast`).
- **Tipografia e Estilos CSS Refinados:** Hierarquia visual limpa, cards com bordas suaves e métricas com contraste aprimorado.
- **Relatório Excel Atualizado:** Cabeçalhos das planilhas exportadas padronizados com as cores oficiais Saavedra.

---

## [1.1.0] - 2026-08-31

### ✨ Adicionado
- **Arquitetura Modular (`src/`):** Divisão de responsabilidades em `config/`, `services/` e `utils/`.
- **Guia Inicial & Download de Template:** Tela amigável de boas-vindas com instruções e botão para baixar planilha de exemplo (`Template_Vendas_TheNehemizer_Exemplo.xlsx`).
- **Filtro Rápido de Preços Pendentes:** Toggle `🔍 Apenas preços pendentes` para facilitar o preenchimento rápido de itens sem preço de compra.
- **Gráficos Executivos:** Visualização gráfica de faturamento por cliente e distribuição de itens (Contrato BD vs Aba NORMAL).
- **Parser de PDF com Regex Flexível:** Suporte a múltiplos padrões de formatação monetária (com e sem `R$`, pontos e vírgulas) e identificação de clientes em páginas múltiplas.
- **Persistência de Sessão (`st.session_state`):** Garantia de retenção das edições manuais e do arquivo exportado durante a navegação.

### 🔄 Alterado
- **Refatoração do `app.py`:** Redução de complexidade, servindo como orquestrador principal e delegando regras aos módulos especializados.
- **Melhorias Visuais no README:** Estruturação semântica com HTML5, badges interativas e tabelas estilizadas com padrão Saavedra.

---

## [1.0.0] - 2026-08-30

### 🚀 Lançamento Inicial
- **Leitura Resiliente de Vendas:** Suporte a arquivos `.xlsx`, `.xls` e `.csv` com múltiplos encodings e descoberta dinâmica de linha de cabeçalho.
- **Parser de Contratos BD em PDF:** Extração automática de tabelas com `pdfplumber` e `@st.cache_data`.
- **Regra Suprema de Contingência:** Alocação de produtos com contrato BD para suas respectivas abas e direcionamento de itens sem contrato para a aba `NORMAL`.
- **Prévia Interativa:** Tabela editável com `st.data_editor` para preenchimento de preços faltantes.
- **Exportação Multi-Aba com XlsxWriter:** Geração de planilha com **Aba RESUMO** estilizada e abas analíticas por cliente com subtotais e totais gerais.
