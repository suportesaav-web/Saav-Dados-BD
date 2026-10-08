# Manual do Usuário 📖

Bem-vindo(a) ao sistema **Saav Dados BD / Cliente**. Esta ferramenta foi projetada para organizar as vendas por clientes, separando relatórios de faturamento corporativo para clientes de contrato, tudo com exportação inteligente para Excel.

## 1. Fazendo Upload da Planilha
1. Abra o portal web do sistema no seu navegador.
2. Na caixa tracejada, clique em **Browse files** (ou arraste sua planilha).
3. O sistema só aceitará arquivos **Excel (.xlsx)**. É necessário exportar o faturamento nesse formato lá do ERP.

## 2. Painel de Classificação de Parceiros
Assim que você envia o arquivo, a tela abrirá o mapeamento de clientes.
- O robô já terá separado alguns hospitais conhecidos (Ex: `UNIMED`, `HMV`, `GHC`). O restante ficará como `NORMAL` (contingência geral).
- Você pode visualizar e alterar livremente cada caixa suspensa para realocar uma conta hospitalar para outra aba.
- **Criar Nova Aba:** Clicando no campo "➕ Criar Nova Aba Customizada", você pode digitar o nome de um Hospital novo e adicioná-lo ao menu para categorização imediata.

## 3. Prévia do Relatório e Edição de Preços de Compra
Descendo a página, você verá uma tabela visualizando o resumo do faturamento.
- **Tudo em um só lugar:** Aqui os itens são agrupados por Hospital e Produto. 
- **Separação Inteligente por Preço:** Se um mesmo produto for vendido para o mesmo hospital mas com Valores Unitários (VLR UNIT) diferentes (por causa de lotes ou condições distintas), o sistema exibirá linhas separadas para cada preço, preservando o valor exato!
- **Edição de Abas:** Você ainda pode remanejar a aba destino do item diretamente pelo menu suspenso `ABA DESTINO`.
- **Coluna CONTRATO:** Além do destino, você pode alterar o campo `CONTRATO`. Ele serve para identificar qual foi a regra de contrato aplicada na venda daquele item, independente da aba em que ele vai ficar.
- **VLR COMPRA (Custo):** Todos os itens vêm zerados. Você pode dar dois cliques na célula de `VLR COMPRA` e digitar o custo real. O campo `TOT VLR COMPRA` irá se auto-multiplicar instantaneamente para mostrar o impacto na quantidade.
- **VLR UNIT VENDA:** Este campo vem fixado do seu faturamento bruto (apenas leitura). Ele exibe o valor unitário exato da nota.

## 4. Geração do Relatório Final
Com tudo revisado e os valores de compra incluídos:
1. Clique no grande botão azul **"GERAR RELATÓRIO FINAL 📥"**.
2. Aguarde alguns segundos.
3. Clique no botão de Download que aparecerá na tela.
4. O seu arquivo `.xlsx` virá formatado nas cores da Saavedra, dividido em várias abas (uma aba para o RESUMO geral, e outras abas separadas por hospital).
5. As colunas de Total de Compra e Total de Venda já estarão amarradas com Fórmulas Nativas do Excel!
