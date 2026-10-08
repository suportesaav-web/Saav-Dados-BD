# Troubleshooting e Solução de Problemas

Este documento compila os erros mais comuns (e suas soluções) que podem ocorrer durante o uso ou manutenção do sistema **Saav Dados BD / Cliente**.

## 1. Erro: `ModuleNotFoundError: No module named X` no Deploy
**Descrição:** Ocorre ao tentar rodar a aplicação no Streamlit Cloud ou localmente, indicando que uma biblioteca não foi encontrada.
**Causa:** O arquivo `requirements.txt` está desatualizado.
**Solução:** Adicione a biblioteca faltante no `requirements.txt` e faça o commit/push. (Ex: se faltar o `pandas`, garanta que ele está na lista).

## 2. Erro: Falha ao fazer Upload da Planilha (Formato Inválido)
**Descrição:** O sistema recusa o arquivo ou acusa um erro de leitura.
**Causa:** O usuário fez o upload de um arquivo `.xls` (formato antigo) ou `.csv` em vez do formato `.xlsx` suportado.
**Solução:** Abra a planilha no Excel e salve-a explicitamente como "Pasta de Trabalho do Excel (*.xlsx)". Suba este novo arquivo.

## 3. Erro: `KeyError: 'REFPROD'` ou Coluna não encontrada
**Descrição:** A aplicação quebra ao tentar processar o relatório de faturamento.
**Causa:** As colunas exportadas do sistema ERP (Sankhya) não batem com os nomes mapeados no motor de regras (`src/services/business_rules.py`).
**Solução:** Verifique se as colunas da planilha exportada contêm palavras-chave esperadas (ex: "Ref Prod", "Qtd", "Desc"). Se o Sankhya mudou o padrão de exportação, o mapeamento em `normalizar_colunas_vendas` deve ser atualizado.

## 4. Erro: `ValueError: DataFrame index must be unique`
**Descrição:** Erro ao realizar edições diretamente na Prévia do Relatório.
**Causa:** Dois produtos iguais (mesma referência) vendidos para parceiros distintos acabaram sendo agrupados sem a diferenciação de destino, gerando conflito de chaves.
**Solução:** (Corrigido na v2.0.0 via campo oculto `ABA_DESTINO_ORIGINAL`). Se o erro voltar, certifique-se de que o cruzamento de edição no `app.py` utiliza a chave tripla `['ABA_DESTINO_ORIGINAL', 'REFPROD', 'DESCRICAO']`.

## 5. Erro: O Total Geral Não Bate Com a Planilha Original
**Descrição:** O Excel final consolida um Valor Total divergente da planilha fonte.
**Causa:** Alguns registros podem estar vindo sem Quantidade, com quantidade negativa, ou com nomes de colunas que não foram somadas adequadamente, ficando de fora do `.groupby`.
**Solução:** Valide os dados nulos na planilha de origem. Verifique se existem linhas de devolução (que podem ter quantidade negativa ou nula) afetando a soma final.

## 6. Erro: Lerdeza e Travamento da Interface
**Descrição:** O app no Streamlit fica muito lento ao rolar as tabelas.
**Causa:** Upload de arquivos gigantescos (mais de 100.000 linhas) sobrecarregam a renderização da tabela na interface do `st.data_editor`.
**Solução:** O Streamlit renderiza os dados no navegador. Para relatórios monstruosos, é recomendado quebrar o faturamento mensal em arquivos quinzenais.

## 7. Erro: Valor de Compra e TOT VLR COMPRA Não Aparecem no Excel
**Descrição:** O Excel exportado veio sem as colunas de custo e compra, ou sem as fórmulas.
**Causa:** Código de geração não refletiu o estado da interface.
**Solução:** Verifique o `excel_exporter.py`. Garanta que a lista de cabeçalhos inclui as colunas `"VLR COMPRA"` e `"TOT VLR COMPRA"`, e que a função `write_formula` está apontando para as colunas corretas (F, G, etc).

## 8. Erro: Divisão por Zero (`VLR UNIT VENDA` = 0)
**Descrição:** O VLR UNIT VENDA aparece zerado ou com `NaN`/`Inf`.
**Causa:** A quantidade vendida (`QTDCOM`) está igual a 0 ou vazio na origem, mas há um `VLRTOTAL` na nota (brindes ou amostras atípicas).
**Solução:** O script já utiliza `np.where(QTDCOM > 0, VLRTOTAL / QTDCOM, 0)` para mitigar isto. Cheque se os tipos de dados não foram lidos como `string` em vez de números. 

## 9. Erro: Abas de Clientes sumiram (Tudo vai pro NORMAL)
**Descrição:** Você faz o upload do arquivo e 100% dos dados caem no NORMAL, não isolando a UNIMED ou outros hospitais.
**Causa:** A "Razão Social" exportada pelo ERP mudou e os termos de busca (ex: "MOINHOS DE VENTO") não batem mais.
**Solução:** Edite o arquivo `src/config/settings.py` em `CLIENTES_CONFIG` e adicione as novas palavras-chave de identificação no array `'termos'`.

## 10. Erro: A interface "pisca" (reloads infinitos) ao alterar o VLR COMPRA
**Descrição:** Ao digitar um valor de compra, o site recarrega infinitamente.
**Causa:** Conflito de `st.session_state` e checagem de igualdade (`.equals()`) nas tabelas do Streamlit, que detecta alteração de estado no loop.
**Solução:** Garanta que a comparação `if not resumo_df_ui.equals(st.session_state['resumo_df_editado']):` aconteça somente após verificar se houve realmente mudança de dados, usando `st.rerun()` estritamente dentro desse bloco e com um `.copy()` dos DataFrames atualizados.
