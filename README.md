# Saav Dados BD / Cliente 📊

Um sistema inteligente desenvolvido em **Python** + **Streamlit** para automação, análise, e segmentação de relatórios de faturamento hospitalar.

## Visão Geral do Projeto

A ferramenta "Saav Dados BD / Cliente" permite realizar o upload de planilhas massivas de faturamento (via ERP Sankhya ou similar) e aplicar regras de negócio autônomas para mapear quais produtos foram vendidos para clientes chaves pré-acordados e quais devem seguir para um faturamento genérico contingenciado ("NORMAL"). 

Além da validação de preços nativa e da segmentação interativa, o projeto entrega uma **exportação em `.xlsx` formatada em alto nível** nas cores oficiais da empresa, injetando fórmulas nativas do Excel para recálculo fluido de lucros baseados em valor de compra vs. valor de venda.

---

## 📚 Documentação Principal

Separamos a documentação baseada no seu perfil de acesso. Para se guiar, acesse um dos links abaixo:

1. **[Manual do Usuário](docs/MANUAL_USUARIO.md):** 
   - Aprenda a operar o aplicativo, fazer os envios de arquivos, configurar novas abas e realizar a edição de Valores de Compra em tempo real.
2. **[Guia Técnico & Manutenção](docs/GUIA_TECNICO.md):** 
   - Documentação de engenharia voltada para os programadores e suporte de TI. Detalha a arquitetura do Streamlit, bibliotecas Python utilizadas (Pandas, Xlsxwriter) e estrutura de pastas.
3. **[Solução de Problemas (Troubleshooting)](docs/TROUBLESHOOTING.md):** 
   - Enfrentando algum Bug? Leia nosso mapeamento com os **Top 10 erros mais frequentes** (como quebras de interface, loopings de loading, e problemas com dados) e saiba como diagnosticar e aplicar a solução correta.

---

## Estrutura do Código ⚙️

Adotamos a seguinte estrutura visando as boas práticas de desenvolvimento de software em Python:

```
Saav-Dados-BD/
├── app.py                      # Core Executável do Streamlit
├── requirements.txt            # Controle de pacotes cloud-native
├── docs/                       # Base de Conhecimento e POPs
│   ├── MANUAL_USUARIO.md
│   ├── TROUBLESHOOTING.md
│   └── GUIA_TECNICO.md
└── src/                        # Modularização e Serviços
    ├── config/                 
    │   └── settings.py         # Configurações de Temas e Clientes Chave
    ├── services/
    │   ├── business_rules.py   # Validação de regras e strings
    │   └── excel_exporter.py   # Escrita avançada e relatórios em XlsxWriter
```

## Ferramentas Tecnológicas
- **Linguagem:** Python 3.12+
- **Framework Web:** Streamlit
- **Motor de Dados:** Pandas
- **Exportação de Arquivos:** Xlsxwriter
- **Deployment:** Streamlit Community Cloud (via Integração GitHub CI/CD)

---
*Este repositório contém código proprietário desenvolvido para uso interno da operação da Saavedra.*
