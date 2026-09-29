# 📑 DOCUMENTAÇÃO TÉCNICA E OPERACIONAL — Saav Dados BD (SAAVEDRA)

> **Observação:** Esta documentação foi formatada para ser copiada e colada diretamente no **Confluence** ou exportada como base de conhecimento da empresa.

---

## 📌 1. Metadados do Documento

| Atributo | Detalhe |
| :--- | :--- |
| **Nome do Sistema** | Saav Dados BD — Portal Financeiro Saavedra |
| **Código do Projeto** | `SAAV-Saav Dados BD` |
| **Versão Atual** | `1.3.0` |
| **Área Negocial** | Departamento Financeiro / Compras / Logística |
| **Linguagem / Framework** | Python 3.11+ / Streamlit |
| **Status do Sistema** | 🟢 **Em Produção** |
| **URL em Produção** | [https://Saav-Dados-BD-saavedra.streamlit.app/](https://Saav-Dados-BD-saavedra.streamlit.app/) |
| **Desenvolvedor Principal** | Jonatan Severo |
| **Unidade de Negócio** | Saavedra Suporte Web |
| **E-mail de Suporte** | `suporte.saav@saavedra.com.br` |
| **Perfil LinkedIn** | [linkedin.com/in/jonatanfsevero](https://www.linkedin.com/in/jonatanfsevero/) |
| **Última Atualização** | 02/09/2026 |

---

## 🎯 2. Visão Geral e Objetivo Negocial

### 2.1 Contexto
A operação comercial da **Saavedra** envolve a comercialização de suprimentos e dispositivos hospitalares sob contratos de fornecimento público e privado (ex.: Becton Dickinson - BD, Unimed, HCPA, EBSERH, PUC, GHC, etc.). 

Anteriormente, o processo de consolidação de relatórios de vendas, verificação de preços tabelados em propostas comerciais em PDF e segregação de vendas fora de contrato dependia de digitação e cruzamento manual em planilhas Excel, demandando horas de trabalho e gerando riscos de inconsistência financeira.

### 2.2 Solução: Saav Dados BD
O **Saav Dados BD** é uma ferramenta de automação inteligente que:
1. **Ingere** relatórios de vendas brutos (Excel/CSV) e identifica automaticamente as colunas principais.
2. **Extrai** com precisão os preços unitários e vigências contidas em propostas contratuais no formato PDF.
3. **Aplica a Regra Suprema de Contingência**, direcionando itens sem contrato BD para a aba `NORMAL` e itens contratados para suas respectivas abas operacionais.
4. **Permite edição em tempo real** diretamente no navegador para correções ou preenchimento de preços pendentes.
5. **Gera uma planilha executiva padronizada** (`PROCESSADO_Relatorio_Final_Saav_Dados_BD.xlsx`) pronta para conciliação financeira e auditoria.

---

## 📖 3. Manual Operacional do Usuário (Passo a Passo)

```
[ PASSO 1: Fazer Upload dos Arquivos ] 
       ↳ 1º Relatório de Vendas (Excel / CSV)
       ↳ 2º Contratos BD (PDFs das propostas)
       ↳ 3º Tabela Preços Normal (Excel / CSV - Opcional)
                   │
                   ▼
[ PASSO 2: Processamento e Equalização Automática ]
                   │
                   ▼
[ PASSO 3: Validação na Prévia Editável (Data Editor) ]
       ↳ Dê duplo-clique no campo "PRECO_COMPRA_FINAL" se houver valores em branco.
                   │
                   ▼
[ PASSO 4: Exportação ]
       ↳ Clique no botão "GERAR RELATÓRIO FINAL 📥"
       ↳ Baixe a planilha consolidada pronta.
```

### 3.1 Instruções Detalhadas
1. **Acessar a Aplicação:** Abra o navegador no endereço indicado (ex: `http://localhost:8501` ou URL interna do portal).
2. **Upload dos Arquivos:**
   - **1º Campo (Obrigatório):** Selecione o arquivo Excel (`.xlsx`, `.xls`) ou `.csv` contendo o relatório de vendas bruto.
   - **2º Campo (Recomendado):** Selecione um ou múltiplos arquivos PDF contendo as propostas/contratos da BD.
   - **3º Campo (Opcional):** Selecione a tabela de preços normais (tabela padrão de compras).
3. **Conferência da Prévia:**
   - Na seção **"Prévia do Relatório (Aba RESUMO)"**, o sistema exibe os dados consolidados.
   - Colunas como `CONTRATO_FINAL`, `SIGLA_RESUMO`, `QTDCOM` e `VLRTOTAL` ficam protegidas contra edição para segurança dos dados.
   - A coluna `PRECO_COMPRA_FINAL` aceita alteração manual direta.
4. **Geração do Download:**
   - Clique no botão **"GERAR RELATÓRIO FINAL 📥"**.
   - O sistema acionará uma animação de confirmação e exibirá o botão verde **"📄 Baixar Planilha Consolidada"**.

---

## ⚖️ 4. Regras de Negócio e Lógica de Mapeamento

### 4.1 De-Para de Clientes e Contratos

O sistema utiliza a função `agrupar_cliente` para varrer termos de razão social, CNPJ e códigos de clientes, mapeando para as siglas institucionais e números de contratos cadastrados na constante `CONTRATOS_MAPPING`:

| Sigla / Grupo | Termos de Busca (Regex/Contém) | CNPJs / Códigos | Número do Contrato |
| :--- | :--- | :--- | :--- |
| **UNIMED** | `UNIMED` | `87096616` | `450128261` |
| **PUC** | `UNIAO BRASILEIRA`, `PUC` | `88630413` | `450155842` |
| **H DIVINA** | `DIVINA` | `87317764` | `450146829` |
| **HCPA** | `CLINICAS` | `87020517` | `450139832` |
| **SMS POA** | `PORTO ALEGRE` + (`PREF` / `MUNICIPIO`) | `92963560` | `450120243` |
| **EBSERH** | `EBSERH`, `SERVICOS HOSPITALARES` | `15126437` | `450098658` |
| **HCAA** | `ASTROGILDO` | `95610887` | `450137626` |
| **GHC / CONCEICAO**| `GHC`, `CONCEICAO`, `CONCEIÇÃO` | `450166419` | `450166419` |
| **SANTA CASA** | `SANTA CASA` | — | *Direcionamento específico* |

### 4.2 Padronização de Colunas do Relatório de Vendas
O sistema realiza varredura nas 20 primeiras linhas do relatório de vendas para localizar o cabeçalho real (`RAZAOSOCIAL` ou `CONVENIO`) e renomeia automaticamente os campos conforme abaixo:

| Termo Encontrado no Arquivo | Coluna Padronizada no Sistema |
| :--- | :--- |
| Contém `REF` e `PROD` | `REFPROD` |
| Contém `DESC` | `DESCRICAO` |
| Contém `QTD` | `QTDCOM` |
| Contém `VLR` ou `VALOR` | `VLRTOTAL` |
| Contém `RAZ` e `SOC` | `RAZAOSOCIAL` |
| Contém `CONV` | `CONVENIO` |

### 4.3 A Regra Suprema de Destinação (Fluxo Decisório)
Para cada produto comercializado:
1. **Verificação de Preço BD:** Checa se a referência do produto (`REFPROD`) foi encontrada no PDF correspondente ao `GRUPO_CLIENTE`.
2. **Definição de Aba Destino:**
   - **SE** `VALOR_TABELADO_BD` existe $\rightarrow$ `ABA_DESTINO = GRUPO_CLIENTE`, `CONTRATO_FINAL = Nº CONTRATO BD`.
   - **SENÃO** $\rightarrow$ `ABA_DESTINO = 'NORMAL'`, `CONTRATO_FINAL = 'NORMAL'`.
3. **Composição do Preço de Compra Final:**
   $$\text{PRECO\_COMPRA\_FINAL} = \text{coalesce}(\text{VALOR\_TABELADO\_BD}, \text{PRECO\_NORMAL}, \text{Preço Editado Manualmente})$$

---

## 📊 5. Estrutura do Arquivo de Saída (Excel Consolidado)

O relatório gerado em `.xlsx` possui a seguinte composição gráfica e de conteúdo:

### 5.1 Aba `RESUMO`
- **Cabeçalho:** Fundo Laranja Saavedra (`#F37021`) com texto branco em negrito.
- **Estrutura de Colunas:** `CONTRATO`, `SIGLA/GRUPO`, `PEDIDO`, `Ref Prod`, `Descrição`, `Qtd Com`, `VLR UNIT`, `VLR TOTAL`, `VLR UNIT COMPRA`, `VLR TOTAL COMPRA`.
- **Subtotais Acumulados:** Inserção de linha destacada ao final de cada grupo (`TOTAL ACUMULADO {destino}`) com soma total dos valores de venda e compra.
- **Formatação Monetária:** Colunas de valor formatadas em `R$ #,##0.00`.

### 5.2 Abas Individuais por Cliente (`UNIMED`, `PUC`, `HCPA`, `NORMAL`, etc.)
- **Cabeçalho:** Fundo Grafite (`#333333`) com texto branco em negrito.
- **Seção Superior:** Lista completa das transações brutas contendo `CONTRATO`, `CNPJ_PARCEIRO`, `UF`, `COD_CLI_USO`, `RAZÃO SOCIAL`, `CNPJ_PARC_USO`, `CONVENIO`, `Ref Prod`, `Descrição`, `Qtd`.
- **Seção Inferior (Tabela Resumo da Aba):** Tabela sintética consolidando `Ref Prod`, `Descrição`, `Qtd Com`, `VLR UNIT VENDA`, `VLR TOTAL VENDA` e a linha final `TOTAL GERAL`.

---

## ⚙️ 6. Instalação e Sustentação Técnica

### 6.1 Requisitos de Infraestrutura
- **SO Compatível:** Windows Server / Linux Ubuntu 22.04 LTS / macOS.
- **Python:** 3.11+
- **Bibliotecas Chave:**
  - `streamlit`: Servidor web reativo e renderização gráfica.
  - `pandas`: Motor de ETL e agregação estatística.
  - `pdfplumber`: Extração textual e tabular de documentos PDF.
  - `xlsxwriter`: Formatação avançada e geração nativa de arquivos `.xlsx`.

### 6.2 Comando de Execução em Produção
Para manter a aplicação executando continuamente em segundo plano no servidor:
```bash
streamlit run app.py --server.port 8501 --server.address 0.0.0.0
```

---

## ❓ 7. Troubleshooting e Perguntas Frequentes (FAQ)

### Q1: O que fazer se um novo contrato ou cliente for adicionado?
**R:** Basta atualizar a configuração `CLIENTES_CONFIG` no arquivo [`src/config/settings.py`](file:///c:/Users/SAAV054/Documents/Desenvolvimento/Saav-Dados-BD/src/config/settings.py) incluindo o termo identificador, CNPJ (se houver) e o número do contrato correspondente.

### Q2: Por que um produto foi parar na aba `NORMAL` em vez da aba do cliente?
**R:** Isso ocorre quando o produto vendido não foi encontrado na tabela do PDF do contrato correspondente àquele cliente. O sistema aplica a *Regra Suprema* e destina o item para `NORMAL` para evitar precificação incorreta.

### Q3: O PDF não está extraindo os preços corretamente. Como ajustar?
**R:** Certifique-se de que o PDF é um documento pesquisável (vetorial) e não uma imagem digitalizada. O `pdfplumber` necessita de camadas de texto editáveis para capturar a célula contendo `"R$"`.

---

## 👨‍💻 8. INFORMAÇÕES DE AUTORIA & SUPORTE TÉCNICO

Para dúvidas arquiteturais, solicitações de alterações ou suporte técnico nesta solução:

- **Desenvolvedor Principal:** Jonatan Severo
- 📧 **E-mail de Suporte:** [suporte.saav@saavedra.com.br](mailto:suporte.saav@saavedra.com.br)
- 💼 **Perfil Profissional LinkedIn:** [linkedin.com/in/jonatanfsevero](https://www.linkedin.com/in/jonatanfsevero/)
- 🏢 **Unidade de Negócio:** Saavedra Suporte Web
