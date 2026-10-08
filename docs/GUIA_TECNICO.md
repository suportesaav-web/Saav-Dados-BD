# Guia Técnico de Desenvolvimento ⚙️

Bem-vindo à documentação técnica do sistema **Saav Dados BD / Cliente**. Este documento é voltado para desenvolvedores e mantenedores que precisem realizar suporte, escalabilidade e correções na base de código.

## 1. Arquitetura do Projeto

O sistema é um aplicativo web desenvolvido integralmente em **Python** utilizando o framework **Streamlit** e a biblioteca **Pandas**. 

A arquitetura adota boas práticas de modularização para separar as camadas de interface gráfica, regras de negócio e geração de arquivos:

```
Saav-Dados-BD/
├── app.py                      # Arquivo principal (Entrypoint do Streamlit)
├── requirements.txt            # Dependências (Streamlit, Pandas, XlsxWriter, etc.)
├── docs/                       # Documentações do Projeto
│   ├── MANUAL_USUARIO.md
│   ├── TROUBLESHOOTING.md
│   └── GUIA_TECNICO.md
└── src/                        # Código Fonte Principal
    ├── config/                 
    │   └── settings.py         # Configurações globais (Cores, Dicionário de Clientes, CSS)
    ├── services/
    │   ├── business_rules.py   # Lógicas pesadas de formatação e consolidação
    │   ├── excel_exporter.py   # Módulo responsável por escrever o .xlsx nativo
    │   └── pdf_service.py      # Agrupamento e identificação de nomenclaturas de Hospitais
    └── utils/
        └── ui_components.py    # (Opcional/Legado) Componentes extra de interface
```

## 2. Padrões de Código e Manutenção

- **Estado da Interface (Session State):** Toda edição feita nas tabelas (como no `st.data_editor`) deve estar amarrada a chaves de sessão (`st.session_state`). Sem isso, o Streamlit apaga as modificações do usuário em cada clique.
- **Exportação (Excel):** A exportação de tabelas NÃO utiliza `df.to_excel()` simples. Usamos a engine `xlsxwriter` para formatar colunas de moeda nativamente, inserir as células coloridas do padrão corporativo (Laranja/Grafite) e **injetar fórmulas Excel dinâmicas**.
- **Performance:** Evite laços de repetição (for-loops) varrendo DataFrames, a menos que seja para exportação fina. Utilize sempre vetores nativos do Pandas (`apply`, `np.where`).

## 3. Deployment (Nuvem)

O aplicativo é hospedado na **Streamlit Cloud Community**.
- O processo é integrado ao GitHub. Qualquer `git push` disparado para a branch `main` irá acionar o _Continuous Deployment_ (CD) do Streamlit, re-aplicando a nova versão em poucos minutos.
- Garanta que todo novo pacote utilizado no código seja registrado no `requirements.txt`. O Streamlit fará o `pip install` baseado nele na hora do build.

## 4. Dicionário de Clientes

Novos clientes com contrato pré-pactuado devem ser cadastrados no arquivo `src/config/settings.py` na variável `CLIENTES_CONFIG`.
Eles alimentam o dicionário que re-organiza abas automaticamente, sem que o operador humano tenha que classificar tudo manualmente no UI.
